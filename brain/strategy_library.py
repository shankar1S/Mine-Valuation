class StrategyConfigurator:
    """
    COMPONENT: THE STRATEGY PROCESSOR
    
    WHY: 
    - Decouples the UI (User Intent) from the Engine (Mathematical Execution).
    - Prevents "Spaghetti Code" in the dashboard.
    
    HOW:
    - Receives human-readable inputs (e.g., "20% Cost Cut").
    - Returns machine-readable modifiers (e.g., "0.80 Multiplier").
    """
    
    @staticmethod
    def configure_high_grading(trigger_price, grade_mult, thru_mult, cost_mult):
        """
        STRATEGY: HIGH GRADING (MARGIN PROTECTION)
        
        WHY: 
        - In low price environments, we prioritize revenue over mine life.
        - We target high-grade zones only, sacrificing total reserve recovery.
        
        HOW:
        - Grade goes UP (Revenue boost).
        - Throughput goes DOWN (Harder to find specific high-grade ore).
        - Cost goes UP (Selective mining requires more drilling/planning).
        """
        return {
            "trigger_price": trigger_price,
            "grade": grade_mult,
            "throughput": thru_mult,
            "cost": cost_mult,
            "strategy_type": "High Grading"
        }

    @staticmethod
    def configure_lean_ops(trigger_price, fixed_cut_pct, var_cut_pct, capex_cut_pct, severance):
        """
        STRATEGY: LEAN OPERATIONS (COST COMPRESSION)
        
        WHY:
        - When cash flow is negative, we must cut "Fat" (Fixed Costs) to survive.
        - This often incurs a one-time penalty (Severance) but lowers burn rate.
        
        HOW:
        - Converts a "Cut %" into a "Retention Multiplier".
        - Example: 20% Cut -> We pay 80% of the baseline cost (Multiplier 0.80).
        """
        return {
            "trigger_price": trigger_price,
            
            # MATH TRANSFORMATION: 
            # Engine Formula: Cost = Base_Cost * (1 - Cut_Percentage)
            "fixed_cut": fixed_cut_pct / 100.0,
            "capex_cut": capex_cut_pct / 100.0,
            
            # Variable costs are handled via a generic multiplier in the engine
            "cost": 1.0 - (var_cut_pct / 100.0), 
            
            "severance": severance,
            "strategy_type": "Lean Operations"
        }

    @staticmethod
    def configure_stockpile(trigger_price, sp_grade, base_grade, 
                          rehandling_cost, base_mining_cost, throughput_mult):
        """
        STRATEGY: STOCKPILING (ZERO MINING)
        
        WHY:
        - Blasting fresh rock is expensive ($3.50/t). Rehandling loose rock is cheap ($1.50/t).
        - We pause the pit to stop losing money on waste stripping.
        
        HOW:
        1. Grade Mod: Scales down revenue (Stockpiles are usually low grade).
        2. Cost Mod: Drastically lowers mining cost (Rehandling only).
        3. Flag: Tells the engine to set Strip Ratio to 0.0 later.
        """
        # 1. Calculate Grade Drop (e.g., 0.8g/t vs 1.2g/t -> 0.66 factor)
        grade_mod = sp_grade / base_grade if base_grade > 0 else 0.0
        
        # 2. Calculate Cost Savings (e.g., $1.50 vs $3.50 -> 0.42 factor)
        cost_mod = rehandling_cost / base_mining_cost if base_mining_cost > 0 else 0.0
        
        return {
            "trigger_price": trigger_price,
            "grade": grade_mod,
            "throughput": throughput_mult,
            "cost": cost_mod,
            "strategy_type": "Stockpile"
        }