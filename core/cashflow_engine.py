from brain.real_options import RealOptionsManager
from core.geology_manager import GeologyManager
from core.reporter import SimulationReport

class CashFlowEngine:
    """
    COMPONENT: THE COORDINATOR
    
    WHY: 
    - This is the 'Simulation Loop'. It steps through time year-by-year.
    - It enforces 'Path Dependency' (decisions in Year 5 depend on Price in Year 5).
    """
    def __init__(self):
        self.brain = RealOptionsManager()

    def run_simulation(self, price_path, config, strategy_mode="FLEXIBLE", cost_profile=None):
        
        # 1. INITIALIZATION
        # Why: Set up the virtual mine body and the reporting ledger.
        geo = GeologyManager(config)
        report = SimulationReport(config)
        
        # YEAR 0: We spend money to build the mine before operations start.
        report.record_step(-config.INITIAL_CAPEX, "CONSTRUCTION")
        
        is_mine_open = True 
        calendar_year = 1   
        MAX_YEARS = 40 
        
        # --- THE MAIN LOOP (PATH DEPENDENCY) ---
        # How: We loop until the ore runs out OR we hit the max mine life.
        while geo.current_reserve > 0 and calendar_year < MAX_YEARS:
            
            # A. MONITOR ENVIRONMENT
            # Why: Read the stochastic price for *this specific year*.
            current_price = price_path[min(calendar_year, len(price_path)-1)]
            
            # B. CHECK STRATEGIC TRIGGER (THE REAL OPTION)
            # Why: If Price < Trigger, we exercise our option to change operations.
            is_stressed = False
            if strategy_mode == "FLEXIBLE" and config.ALLOW_HIGH_GRADING:
                if current_price < config.HIGH_GRADE_TRIGGER_PRICE:
                    is_stressed = True

            # C. APPLY STRATEGY MODIFIERS
            # Default: Business as Usual (Multipliers = 1.0)
            mod_grade = 1.0
            mod_throughput = 1.0
            mod_var_cost = 1.0
            mod_fixed_cost = 1.0
            mod_capex = 1.0
            is_stockpiling = False

            if is_stressed:
                # How: Retrieve the specific "Rescue Plan" configured in the Dashboard
                mods = config.HIGH_GRADE_MODIFIERS
                
                # Apply Physics changes (Grade/Throughput)
                mod_grade = mods.get("grade", 1.0)
                mod_throughput = mods.get("throughput", 1.0)
                mod_var_cost = mods.get("cost", 1.0)
                
                # Apply Lean Ops changes (Cost Cuts)
                cut_fixed = mods.get("fixed_cut", 0.0)
                cut_capex = mods.get("capex_cut", 0.0)
                mod_fixed_cost = 1.0 - cut_fixed
                mod_capex = 1.0 - cut_capex
                
                # Check for Stockpile Mode (Special Physics Rule)
                if mods.get("strategy_type") == "Stockpile":
                    is_stockpiling = True

            # D. INTERROGATE GEOLOGY
            # Why: Ask the 'Body' for the next block of rock.
            # Note: We pass 'is_stockpiling' so Geology knows to set Strip Ratio = 0.
            rock_data = geo.get_next_block(force_stockpile=is_stockpiling)
            
            if rock_data is None: break # Stop if mine is empty.

            # E. CALCULATE PHYSICALS
            # How: Base Geology * Strategic Modifier
            effective_grade = rock_data['grade'] * mod_grade
            
            annual_capacity = config.DESIGN_CAPACITY_TPD * 365
            actual_throughput = annual_capacity * config.FLEET_AVAILABILITY * rock_data['ramp_factor'] * mod_throughput
            
            # Constraint: Cannot mine more than what remains in the ground.
            if actual_throughput > geo.current_reserve:
                actual_throughput = geo.current_reserve

            # F. CALCULATE COSTS (FINANCIAL ENGINE)
            # 1. Inflation Logic (Stochastic or Deterministic)
            if cost_profile is not None:
                c_idx = min(calendar_year, len(cost_profile)-1)
                cost_inflator = cost_profile[c_idx]
            else:
                cost_inflator = (1 + config.COST_ESCALATION) ** (calendar_year - 1)
            
            # 2. Variable Costs (Mining & Processing)
            mining_cost = config.MINING_OPEX_PER_TONNE * cost_inflator * mod_var_cost
            total_tonnes_moved = actual_throughput * (1 + rock_data['strip_ratio'])
            cost_mining_total = total_tonnes_moved * mining_cost
            
            process_cost = config.PROCESS_OPEX_PER_TONNE * cost_inflator * mod_var_cost
            cost_process_total = actual_throughput * process_cost
            
            # 3. Fixed Costs (Lean Ops Cuts applied here via 'mod_fixed_cost')
            fixed_cost_total = config.CARE_AND_MAINT_COST * cost_inflator * mod_fixed_cost
            
            # 4. Revenue
            recovered_oz = (actual_throughput * effective_grade * config.RECOVERY_RATE) / 31.1035
            revenue = recovered_oz * current_price
            royalties = revenue * config.ROYALTY_RATE
            
            total_opex = cost_mining_total + cost_process_total + fixed_cost_total + royalties
            
            # G. THE BRAIN DECISION (SHUTDOWN LOGIC)
            # Why: Even with our strategy, are we losing so much money that we should close?
            unit_cost = (total_opex / recovered_oz) if recovered_oz > 0 else 99999
            brain_maint_cost = config.CARE_AND_MAINT_COST * cost_inflator * mod_fixed_cost
            
            status, cf, prod_factor = self.brain.evaluate_decision(
                price=current_price, 
                unit_cost=unit_cost, 
                produced_oz=recovered_oz, 
                maintenance_cost=brain_maint_cost,
                restart_cost=config.RESTART_COST,
                shutdown_cost=config.SHUTDOWN_COST,      
                restart_ramp_up=config.RESTART_RAMP_UP,            
                is_open=is_mine_open,    
                mode=strategy_mode
            )
            
            # H. EXECUTE DECISION
            # Apply Capex Cuts (Lean Ops)
            sustaining_capex = config.SUSTAINING_CAPEX_YR * cost_inflator * mod_capex
            
            if status == "CARE_MAINTENANCE":
                # Decision: CLOSE MINE
                report.record_step(cf, "CLOSED")
                is_mine_open = False 
                
            else: 
                # Decision: OPERATE
                real_throughput = actual_throughput * prod_factor
                final_cf = cf - sustaining_capex
                
                # Deplete the rock (Physical Change)
                geo.deplete(real_throughput) 
                report.record_step(final_cf, "ACTIVE")
                is_mine_open = True 

            # I. TAXES
            last_cf_idx = len(report.cash_flows) - 1
            pre_tax = report.cash_flows[last_cf_idx]
            if pre_tax > 0:
                tax = pre_tax * config.TAX_RATE
                report.cash_flows[last_cf_idx] -= tax
            
            calendar_year += 1
            
        # CLOSURE PHASE
        closure_bill = -config.CLOSURE_COST_ESTIMATE * ((1 + config.COST_ESCALATION) ** len(report.cash_flows))
        report.record_step(closure_bill, "CLOSURE")
        
        report.finalize()
        
        return report.npv, {
            "cash_flow": report.cash_flows,
            "decisions": report.decisions
        }