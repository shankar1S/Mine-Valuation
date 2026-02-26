import numpy_financial as npf

class SimulationReport:
    """
    COMPONENT: THE TONGUE (REPORTING LEDGER)
    
    WHY: 
    - The Engine does the work; the Reporter keeps the score.
    - Aggregates annual cash flows into a final 'Net Present Value' (NPV).
    
    HOW:
    - Uses numpy_financial to apply the Discount Rate (Time Value of Money).
    """
    def __init__(self, config):
        self.cash_flows = []
        self.decisions = []
        self.operational_years = 0
        self.care_maint_years = 0
        self.discount_rate = config.DISCOUNT_RATE

    def record_step(self, cash_flow, decision):
        """
        Logs one year of activity.
        """
        self.cash_flows.append(cash_flow)
        self.decisions.append(decision)
        
        if decision == "ACTIVE":
            self.operational_years += 1
        elif decision == "CLOSED":
            self.care_maint_years += 1

    def finalize(self):
        """
        Calculates the Final Score (NPV).
        
        MATH:
        NPV = Sum( CashFlow_t / (1 + r)^t )
        """
        self.npv = npf.npv(self.discount_rate, self.cash_flows)
        self.total_years = len(self.decisions)
        return self

    def summary(self):
        return {
            "NPV": self.npv,
            "Life (Yrs)": self.total_years,
            "Active Years": self.operational_years,
            "Paused Years": self.care_maint_years
        }