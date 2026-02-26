import numpy as np

class StochasticEngine:
    """
    COMPONENT: THE WORLD (MARKET SIMULATOR)
    
    WHY: 
    - Deterministic prices (e.g., flat $2000) ignore risk.
    - We must simulate thousands of "Alternative Futures" to test robustness.
    
    HOW:
    - Uses 'Geometric Brownian Motion' (GBM), the standard model for asset prices.
    - Math: dS = u*S*dt + sigma*S*dW
    """
    def __init__(self):
        self.rng = np.random.default_rng()

    def generate_price_path(self, config, override_volatility=None):
        """
        Generates one possible 50-year future for Gold Prices.
        """
        # 1. Setup Time Horizon
        T = 50.0  
        dt = 1.0  # Yearly steps
        steps = int(T / dt)
        
        # 2. Volatility (Sigma)
        # Why: This controls how wild the price swings are. Higher Vol = Higher Option Value.
        sigma = override_volatility if override_volatility is not None else config.PRICE_VOLATILITY
        
        # 3. Drift (Mu)
        # Why: We use the Risk-Free Rate for 'Risk-Neutral Valuation'.
        mu = config.RISK_FREE_RATE 
        
        # 4. Random Shocks (dW)
        # Why: The 'Heartbeat' of the market. Normally distributed random numbers.
        dW = self.rng.normal(0, np.sqrt(dt), steps)
        
        # 5. Construct Path
        path = [config.GOLD_PRICE_START]
        for t in range(steps):
            # The GBM Formula: New_Price = Old_Price * e^(Drift + Shock)
            drift_term = (mu - 0.5 * sigma**2) * dt
            diffusion_term = sigma * dW[t]
            
            new_price = path[-1] * np.exp(drift_term + diffusion_term)
            path.append(new_price)
            
        return path

    def generate_cost_path(self, config, gold_price_path, cost_elasticity=0.5, cost_volatility=0.10):
        """
        Generates Cost Inflation (Oil/Labor) linked to Gold Prices.
        
        WHY: 
        - When Gold goes up, Oil and Labor often go up too (Correlation).
        - This prevents the "Free Lunch" error where Revenue rises but Costs stay flat.
        """
        steps = len(gold_price_path) - 1 
        cost_path = [1.0] # Starts at index 1.0 (100%)
        
        base_drift = config.COST_ESCALATION
        
        for t in range(1, steps + 1):
            # 1. Independent Shock (Supply Chain issues)
            dW_cost = self.rng.normal(0, 1.0) * cost_volatility
            
            # 2. Correlation 'Pull' (Gold Price Change)
            gold_log_ret = np.log(gold_price_path[t] / gold_price_path[t-1])
            gold_impact = gold_log_ret * cost_elasticity
            
            # 3. Combine
            total_move = base_drift + dW_cost + gold_impact
            
            new_factor = cost_path[-1] * np.exp(total_move)
            cost_path.append(new_factor)
            
        return cost_path