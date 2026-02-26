# --- MINE PROFILE LIBRARY ---
# Features: "Switching Friction" & "Strategic Triggers".

REAL_WORLD_PROFILES = {
    "Manual Input (Custom)": {
        "RESERVES": 1_000_000.0,
        "CAPACITY": 1_000.0, 
        "RECOVERY": 0.90, "AVAILABILITY": 0.90,
        "GRADE_SCHEDULE": [1.0] * 20, 
        "STRIP_SCHEDULE": [5.0] * 20,
        "CARE_AND_MAINT_COST": 500_000.0, 
        "RESTART_COST": 1_000_000.0,
        "SHUTDOWN_COST": 500_000.0,      
        "RESTART_RAMP_UP": 0.70,         
        "OPEX_MINING": 3.0, "OPEX_PROCESS": 20.0, "CAPEX": 10_000_000.0,
        "PRICE": 2000.0, "VOLATILITY": 0.20,
        "RAMP_UP_YR1": 0.60, "RAMP_UP_YR2": 0.90
    },

    # --- NAME CHANGE HERE ---
    "Archetype 1: Distressed Asset Recapitalization": {
        "RESERVES": 137_000_000.0, 
        "CAPACITY": 35_000.0,      
        "RECOVERY": 0.92, "AVAILABILITY": 0.93,      
        "GRADE_SCHEDULE": [1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3, 1.2, 1.2, 1.1, 1.1, 1.0, 1.0, 0.9],
        "STRIP_SCHEDULE": [7.0, 7.0, 7.5, 7.5, 8.0, 8.0, 8.5, 8.5, 9.0, 9.0, 9.5, 9.5, 10.0, 10.0, 10.5],
        
        "CARE_AND_MAINT_COST": 40_000_000.0, 
        "RESTART_COST": 20_000_000.0,
        "SHUTDOWN_COST": 15_000_000.0,   
        "RESTART_RAMP_UP": 0.60,         
        
        "OPEX_MINING": 4.50, "OPEX_PROCESS": 15.00, "CAPEX": 1_500_000_000.0,  
        "PRICE": 2000.0, "VOLATILITY": 0.18,
        "RAMP_UP_YR1": 0.50, "RAMP_UP_YR2": 0.80
    },

    "Archetype 2: The Bonanza (e.g. Fosterville)": {
        "RESERVES": 1_700_000.0,   
        "CAPACITY": 2_000.0,       
        "RECOVERY": 0.98, "AVAILABILITY": 0.85,      
        "GRADE_SCHEDULE": [15.0, 14.0, 12.0, 10.0, 9.0, 8.0, 7.0, 6.0],
        "STRIP_SCHEDULE": [0.0] * 10,
        "CARE_AND_MAINT_COST": 5_000_000.0, 
        "RESTART_COST": 2_000_000.0,
        "SHUTDOWN_COST": 1_000_000.0,    
        "RESTART_RAMP_UP": 0.80,         
        "OPEX_MINING": 140.00, "OPEX_PROCESS": 55.00, "CAPEX": 200_000_000.0,    
        "PRICE": 2000.0, "VOLATILITY": 0.25,        
        "RAMP_UP_YR1": 0.70, "RAMP_UP_YR2": 1.00
    },
    
    "Archetype 3: The Marginal Producer (Thesis Case)": {
        "RESERVES": 12_000_000.0,
        "CAPACITY": 5_000.0, 
        "RECOVERY": 0.88, "AVAILABILITY": 0.82,
        "GRADE_SCHEDULE": [1.2, 1.1, 1.0, 0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65],
        "STRIP_SCHEDULE": [4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 8.5, 9.0, 9.5, 10.0],
        "CARE_AND_MAINT_COST": 3_000_000.0,
        "RESTART_COST": 5_000_000.0,
        "SHUTDOWN_COST": 2_000_000.0,    
        "RESTART_RAMP_UP": 0.75,         
        "OPEX_MINING": 3.80, "OPEX_PROCESS": 18.00, "CAPEX": 45_000_000.0,
        "PRICE": 2000.0, "VOLATILITY": 0.22,
        "RAMP_UP_YR1": 0.60, "RAMP_UP_YR2": 0.90
    }
}

class FeasibilityConfig:
    def __init__(self):
        # Default Safety Values
        self.TOTAL_RESERVE_TONNES = 1000000
        self.DESIGN_CAPACITY_TPD = 1000
        self.RECOVERY_RATE = 0.90
        self.FLEET_AVAILABILITY = 0.90
        self.MINING_OPEX_PER_TONNE = 5.0
        self.PROCESS_OPEX_PER_TONNE = 20.0
        self.INITIAL_CAPEX = 10000000
        self.GOLD_PRICE_START = 2000.0
        self.PRICE_VOLATILITY = 0.20
        self.RISK_FREE_RATE = 0.04
        self.DISCOUNT_RATE = 0.10
        self.COST_ESCALATION = 0.03
        self.RAMP_UP_YR1 = 0.60
        self.RAMP_UP_YR2 = 0.90
        self.CARE_AND_MAINT_COST = 1000000.0
        self.RESTART_COST = 2000000.0
        self.SHUTDOWN_COST = 1000000.0    
        self.RESTART_RAMP_UP = 0.70       
        self.CLOSURE_COST_ESTIMATE = 5000000.0
        self.SUSTAINING_CAPEX_YR = 500000.0
        self.ROYALTY_RATE = 0.04
        self.TAX_RATE = 0.30

        # --- STRATEGIC CONTROLS ---
        self.ALLOW_HIGH_GRADING = False
        self.HIGH_GRADE_TRIGGER_PRICE = 1500.0
        self.HIGH_GRADE_MODIFIERS = {"grade": 1.25, "throughput": 0.80, "cost": 1.15}