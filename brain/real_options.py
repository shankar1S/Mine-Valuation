class RealOptionsManager:
    """
    COMPONENT: THE BRAIN (DECISION LOGIC)
    
    WHY: 
    - Evaluates the "Option to Abandon" and "Option to Restart".
    - Implements 'Hysteresis': The mine resists changing state because change is expensive.
    
    HOW:
    - Compares 'Value of Open' vs 'Value of Closed' vs 'Value of Restarting'.
    - Includes penalties (Shutdown Cost, Restart Cost, Ramp-up Inefficiency).
    """
    def evaluate_decision(self, price, unit_cost, produced_oz, 
                          maintenance_cost, restart_cost, shutdown_cost, 
                          restart_ramp_up, is_open, mode="FLEXIBLE"):
        
        # 1. CALCULATE BASE METRICS
        # Profit if we run at 100% capacity
        normal_operating_cf = (price - unit_cost) * produced_oz
        
        # Cost if we are in Care & Maintenance (always negative)
        care_maint_cf = -abs(maintenance_cost)
        
        if mode == "STATIC":
            # STATIC CASE: The mine is dumb. It never closes, even if losing money.
            return "ACTIVE", normal_operating_cf, 1.0 
            
        elif mode == "FLEXIBLE":
            # FLEXIBLE CASE: The mine thinks like a human manager.
            
            # SCENARIO 1: We are currently OPEN.
            if is_open:
                # OPTION A: Stay Open (Status Quo)
                val_stay_open = normal_operating_cf
                
                # OPTION B: Close Down
                # Physics: You must pay Severance (Shutdown Cost) to fire everyone.
                val_close = care_maint_cf - abs(shutdown_cost)
                
                # DECISION RULE: Only close if losses > shutdown cost.
                if val_stay_open >= val_close:
                    return "ACTIVE", val_stay_open, 1.0
                else:
                    return "CARE_MAINTENANCE", val_close, 0.0
            
            # SCENARIO 2: We are currently CLOSED.
            else:
                # OPTION A: Stay Closed (Status Quo)
                val_stay_closed = care_maint_cf
                
                # OPTION B: Restart
                # Physics: Restarting is hard. You only get partial production (Ramp Up Factor).
                restarted_oz = produced_oz * restart_ramp_up
                restarted_operating_cf = (price - unit_cost) * restarted_oz
                
                # Physics: You must pay to hire everyone back (Restart Cost).
                val_restart = restarted_operating_cf - abs(restart_cost)
                
                # DECISION RULE: Only restart if profits > restart cost.
                if val_restart > val_stay_closed:
                    return "ACTIVE", val_restart, restart_ramp_up 
                else:
                    return "CARE_MAINTENANCE", val_stay_closed, 0.0
        
        return "ACTIVE", normal_operating_cf, 1.0