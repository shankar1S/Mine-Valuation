# Strategic Mine Valuation Engine ⚒️

### Thesis: Real Options vs. Static DCF in Volatile Markets

**Author:** Pushkar  
**Department:** Mining Engineering, NITK Surathkal  
**Year:** 2026

---

## 📖 Overview
This project is a **Strategic Real Options Valuation (ROV) Engine** designed to value mining assets in high-volatility environments. 

Unlike traditional **Discounted Cash Flow (DCF)** models—which assume a fixed mine plan regardless of gold price—this engine simulates a "Active Manager" who can:
1.  **High Grade** (Target rich zones) when prices crash.
2.  **Lean Operations** (Cut fixed costs) to survive distress.
3.  **Stockpile Process** (Pause mining, run mill only) to eliminate strip ratios.

## 🏗️ Architecture
The system follows a strict **Model-View-Controller (MVC)** design pattern for modularity:

* **`gui/` (The Face):** A Streamlit-based dashboard for interactive sensitivity analysis.
* **`brain/` (The Logic):** * `real_options.py`: Evaluates the "Option to Abandon" vs. "Option to Restart" (Hysteresis).
    * `strategy_library.py`: Translates human inputs (e.g., "20% Cost Cut") into mathematical modifiers.
* **`core/` (The Physics):**
    * `cashflow_engine.py`: The time-stepping simulation loop (Path Dependent).
    * `geology_manager.py`: Manages the depletion of the ore body and strip ratios.
    * `stochastic_engine.py`: Generates Geometric Brownian Motion (GBM) price paths.

## 🚀 How to Run

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Launch the Engine:**
    ```bash
    streamlit run gui/dashboard.py
    ```

## 📊 Key Features
* **Dynamic Geology Scaling:** Adjusts grade/tonnage curves based on user inputs.
* **Stochastic Cost Modeling:** Correlates input costs (Oil/Labor) with Gold Price.
* **Comparative Analysis:** Runs 5,000+ Monte Carlo simulations to compare Static vs. Flexible NPV.
* **Risk Metrics:** Calculates Value at Risk (VaR) and Probability of Loss.

---
*Built for the Final Year B.Tech Project.*