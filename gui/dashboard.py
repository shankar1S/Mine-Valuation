import streamlit as st
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go

from data.mine_configs import REAL_WORLD_PROFILES, FeasibilityConfig
from core.stochastic_engine import StochasticEngine
from core.cashflow_engine import CashFlowEngine
# IMPORT THE NEW BRAIN COMPONENT (The Processor)
from brain.strategy_library import StrategyConfigurator

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Strategic Mine Valuation Engine", 
    layout="wide", 
    page_icon="⚒️",
    initial_sidebar_state="collapsed"
)

st.markdown(
    "<style>.block-container{max-width:100%;padding-left:1rem;padding-right:1rem;}</style>",
    unsafe_allow_html=True,
)

# --- SESSION STATE MANAGEMENT ---
def init_session_state():
    st.session_state.setdefault("baseline_run", True)

def reset_simulation():
    init_session_state()
    st.session_state.baseline_run = True

def run_app():
    init_session_state()
    # --- HEADER ---
    c_head1, c_head2 = st.columns([3, 1])
    with c_head1:
        st.title("⚒️ Strategic Mine Valuation Engine")
        st.markdown("### Thesis: `Real Options` vs `Static DCF` in Volatile Markets")
    with c_head2:
        if st.button("🔄 Reset Analysis"):
            reset_simulation()
            st.rerun()

    st.markdown("---")

    # --- 1. PROFILE SELECTION ---
    col_profile, col_void = st.columns([1, 2])
    with col_profile:
        options = list(REAL_WORLD_PROFILES.keys())
        default_idx = next((i for i, s in enumerate(options) if "Marginal" in s), 0)
        profile_name = st.selectbox("📂 Select Asset Profile:", options, index=default_idx, on_change=reset_simulation)
        
    data = REAL_WORLD_PROFILES[profile_name]

    # --- 2. INPUT FORM ---
    with st.expander("🔧 Technical & Economic Parameters", expanded=True):
        def get_val(key, default=0.0):
            if key in data:
                val = data[key]
                if isinstance(val, list): return float(np.mean(val))
                return float(val)
            if key + "_SCHEDULE" in data: return float(np.mean(data[key + "_SCHEDULE"]))
            return default

        c1, c2, c3 = st.columns(3)
        reserves = c1.number_input("Reserves (Tonnes)", value=get_val("RESERVES"), format="%.0f")
        grade = c2.number_input("Avg Grade (g/t)", value=get_val("GRADE"), format="%.2f", step=0.1)
        strip = c3.number_input("Avg Strip Ratio (w:o)", value=get_val("STRIP"), format="%.2f", step=0.1)
        
        c4, c5, c6 = st.columns(3)
        capacity = c4.number_input("Mill Capacity (TPD)", value=get_val("CAPACITY"), format="%.0f", step=100.0)
        recovery = c5.number_input("Recovery Rate (%)", value=get_val("RECOVERY")*100, format="%.1f", step=0.5) / 100
        avail = c6.number_input("Fleet Availability (%)", value=get_val("AVAILABILITY")*100, format="%.1f", step=1.0) / 100
        
        c7, c8, c9 = st.columns(3)
        mining_cost = c7.number_input("Mining Cost ($/t moved)", value=get_val("OPEX_MINING"), format="%.2f")
        process_cost = c8.number_input("Processing Cost ($/t milled)", value=get_val("OPEX_PROCESS"), format="%.2f")
        cm_cost = c9.number_input("Care & Maint. Cost ($/yr)", value=get_val("CARE_AND_MAINT_COST", 2000000.0), format="%.0f")
        
        c10, c11, c12 = st.columns(3)
        price = c10.number_input("Gold Price ($/oz)", value=get_val("PRICE", 2000.0), step=50.0)
        vol = c11.slider("Gold Volatility (%)", 10, 60, int(get_val("VOLATILITY", 0.20)*100)) / 100
        capex = c12.number_input("Initial Capex ($)", value=get_val("CAPEX"), format="%.0f")

        i1, i2 = st.columns(2)
        iters = i1.selectbox("Monte Carlo Runs", [1000, 5000, 10000], index=1)
        cost_model = i2.selectbox("Cost Inflation Model", ["Deterministic (Fixed 3%)", "Stochastic (Oil Price Linked)"])

    # --- GEOLOGY SCALING LOGIC (UI Visuals Only) ---
    if "GRADE_SCHEDULE" in data:
        raw_grade_sched = np.array(data["GRADE_SCHEDULE"])
        raw_strip_sched = np.array(data.get("STRIP_SCHEDULE", [0]*len(raw_grade_sched)))
        orig_grade_avg = np.mean(raw_grade_sched) if np.mean(raw_grade_sched) > 0 else 1.0
        orig_strip_avg = np.mean(raw_strip_sched) if np.mean(raw_strip_sched) > 0 else 1.0
        scaled_grade_sched = raw_grade_sched * (grade / orig_grade_avg)
        scaled_strip_sched = raw_strip_sched * (strip / orig_strip_avg)
    else:
        scaled_grade_sched = np.array([grade] * 10)
        scaled_strip_sched = np.array([strip] * 10)

    # --- MAIN ACTION BUTTON ---
    st.markdown("---")
    if st.button("🚀 RECALCULATE BASELINE ASSESSMENT (Static DCF)", type="primary"):
        st.session_state.baseline_run = True

    # --- PHASE 2: EXECUTION ---
    if st.session_state.get("baseline_run", True):
        # A. BUILD CONFIG
        config = FeasibilityConfig()
        config.TOTAL_RESERVE_TONNES = reserves
        config.DESIGN_CAPACITY_TPD = capacity
        config.RECOVERY_RATE = recovery
        config.FLEET_AVAILABILITY = avail
        config.MINING_OPEX_PER_TONNE = mining_cost
        config.PROCESS_OPEX_PER_TONNE = process_cost
        config.CARE_AND_MAINT_COST = cm_cost 
        config.INITIAL_CAPEX = capex
        config.GOLD_PRICE_START = price
        config.PRICE_VOLATILITY = vol
        config.ROYALTY_RATE = 0.04
        config.TAX_RATE = 0.30
        config.COST_ESCALATION = 0.03
        config.RISK_FREE_RATE = 0.04
        config.DISCOUNT_RATE = 0.10
        config.SUSTAINING_CAPEX_YR = capex * 0.02
        config.CLOSURE_COST_ESTIMATE = capex * 0.15
        config.MINE_LIFE_YEARS = 40 
        
        config.RESTART_COST = get_val("RESTART_COST", 2000000.0)
        config.SHUTDOWN_COST = get_val("SHUTDOWN_COST", 1000000.0)
        config.RESTART_RAMP_UP = get_val("RESTART_RAMP_UP", 0.70)
        
        config.AVERAGE_GRADE_GPT = grade
        config.STRIP_RATIO = strip
        config.GRADE_SCHEDULE = scaled_grade_sched.tolist()
        config.STRIP_SCHEDULE = scaled_strip_sched.tolist()
        if "RAMP_UP_YR1" in data: config.RAMP_UP_YR1 = data["RAMP_UP_YR1"]
        if "RAMP_UP_YR2" in data: config.RAMP_UP_YR2 = data["RAMP_UP_YR2"]

        # B. RUN BASELINE
        stoch = StochasticEngine()
        engine = CashFlowEngine()
        test_prices = stoch.generate_price_path(config, override_volatility=vol)
        npv_static, log_static = engine.run_simulation(test_prices, config, strategy_mode="STATIC")
        
        # --- MARKET CONTEXT & STATUS ---
        oz_per_tonne = (grade * recovery) / 31.1035
        total_cost_per_tonne = (mining_cost * (1 + strip)) + process_cost
        breakeven_price = total_cost_per_tonne / oz_per_tonne if oz_per_tonne > 0 else 2000
        
        # Finance-Grade Risk Classification
        prob_loss_baseline = np.mean(np.array(npv_static) < 0) * 100 if isinstance(npv_static, list) else (100 if npv_static < 0 else 0)
        
        if prob_loss_baseline > 40:
            risk_label = "High Risk (Distressed)"
            risk_color = "red"
        elif prob_loss_baseline > 20:
            risk_label = "Moderate Risk"
            risk_color = "orange"
        else:
            risk_label = "Low Risk (Investable)"
            risk_color = "green"

        st.markdown(f"### `Baseline Status: {risk_label}`")
        st.markdown(f"**Static NPV:** :{risk_color}[${npv_static/1e6:.1f} M] | **Breakeven:** ${breakeven_price:.0f}/oz")

        col_mkt, col_geo = st.columns(2)
        with col_mkt:
            fig_price = go.Figure()
            fig_price.add_trace(go.Scatter(y=test_prices, mode='lines', name='Sample Price Path', line=dict(color='gold', width=1)))
            fig_price.add_hline(y=breakeven_price, line_dash="dash", line_color="red", annotation_text=f"Est. LOM Avg Breakeven: ${breakeven_price:.0f}/oz")
            fig_price.update_layout(title="📉 Market Volatility (External Risk)", xaxis_title="Year", yaxis_title="Price ($/oz)", template="plotly_white", height=350)
            st.plotly_chart(fig_price, width="stretch")

        with col_geo:
            min_len = min(len(scaled_grade_sched), len(scaled_strip_sched))
            sched_df = pd.DataFrame({
                "Year": range(1, min_len+1),
                "Grade (g/t)": scaled_grade_sched[:min_len],
                "Strip Ratio": scaled_strip_sched[:min_len]
            })
            fig_geo = go.Figure()
            fig_geo.add_trace(go.Scatter(x=sched_df["Year"], y=sched_df["Grade (g/t)"], name="Grade (g/t)", line=dict(color="#FFA15A", width=3)))
            fig_geo.add_trace(go.Scatter(x=sched_df["Year"], y=sched_df["Strip Ratio"], name="Strip Ratio", yaxis="y2", line=dict(dash="dot", color="grey")))
            fig_geo.update_layout(yaxis2=dict(overlaying="y", side="right"), title="📉 Underlying Geology (Scaled to Input)", template="plotly_white", height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_geo, width="stretch")

        # C. STRATEGIC REAL OPTIONS (CLEAN VERSION)
        st.markdown("---")
        st.subheader("⚔️ Real Options & Strategic Flexibility Analysis")
        st.markdown("Configure mutually exclusive strategies to isolate the value of specific operational flexibilities.")
        
        strategy_choice = st.selectbox(
            "Select Operational Flexibility Strategy:",
            ["High Grading (Margin Protection)", 
             "Lean Operations (Cost Compression)",
             "Stockpile / Alternative Feed (No Mining)"]
        )
        
        st.markdown(f"**Configure Physics for: {strategy_choice}**")
        
        # --- INPUT COLLECTION (UI ONLY) ---
        with st.form("strategy_config_form"):
            col_trig, col_phys, col_cost = st.columns(3)
            
            # 1. High Grading Inputs
            if "High Grading" in strategy_choice:
                with col_trig: trigger = st.number_input("Trigger Price ($/oz)", value=1500.0, step=50.0)
                with col_phys:
                    g_mult = st.number_input("Grade Multiplier (e.g. 1.20)", value=1.20, step=0.05)
                    t_mult = st.number_input("Throughput Multiplier (e.g. 0.75)", value=0.75, step=0.05)
                with col_cost: c_mult = st.number_input("Mining Cost Multiplier (e.g. 1.10)", value=1.10, step=0.05)
            
            # 2. Lean Operations Inputs
            elif "Lean Operations" in strategy_choice:
                with col_trig: trigger = st.number_input("Trigger Price ($/oz)", value=1400.0, step=50.0)
                with col_phys:
                    fix_cut = st.number_input("Fixed Cost Reduction (%)", value=20.0, step=5.0)
                    cap_cut = st.number_input("Sustaining Capex Cut (%)", value=50.0, step=10.0)
                with col_cost:
                    var_cut = st.number_input("Variable Cost Reduction (%)", value=5.0, step=1.0)
                    sev_cost = st.number_input("Severance Cost ($)", value=1000000.0, step=100000.0)
                    
            # 3. Stockpile Inputs
            elif "Stockpile" in strategy_choice:
                with col_trig: trigger = st.number_input("Trigger Price ($/oz)", value=1300.0, step=50.0)
                with col_phys:
                    sp_g = st.number_input("Stockpile Grade (g/t)", value=0.80, step=0.10)
                    _ = st.number_input("Stockpile Recovery (%)", value=65.0, step=5.0) # Visual placeholder
                    t_mult_sp = st.number_input("Throughput Multiplier (e.g. 1.20)", value=1.20, step=0.10)
                with col_cost:
                    rehand_cost = st.number_input("Rehandling Cost ($/t)", value=2.50, step=0.50)

            run_strategy = st.form_submit_button("⚡ RUN COMPARATIVE MONTE CARLO")

        # --- EXECUTION (DELEGATE TO BRAIN) ---
        if run_strategy:
            config.ALLOW_HIGH_GRADING = True 
            
            # --- BRAIN WORK HAPPENS HERE (No Math in Dashboard!) ---
            if "High Grading" in strategy_choice:
                modifiers = StrategyConfigurator.configure_high_grading(trigger, g_mult, t_mult, c_mult)
            elif "Lean Operations" in strategy_choice:
                modifiers = StrategyConfigurator.configure_lean_ops(trigger, fix_cut, var_cut, cap_cut, sev_cost)
            elif "Stockpile" in strategy_choice:
                modifiers = StrategyConfigurator.configure_stockpile(trigger, sp_g, grade, rehand_cost, mining_cost, t_mult_sp)
            
            # Inject configured modifiers into config
            config.HIGH_GRADE_TRIGGER_PRICE = modifiers.pop("trigger_price")
            config.HIGH_GRADE_MODIFIERS = modifiers

            # --- RUN SIMULATION ---
            static_results = []
            flexible_results = []
            duration_static = []
            duration_flex = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(iters):
                prices = stoch.generate_price_path(config, override_volatility=vol)
                costs = None
                if "Stochastic" in cost_model:
                    costs = stoch.generate_cost_path(config, prices)
                
                npv_s, log_s = engine.run_simulation(prices, config, strategy_mode="STATIC", cost_profile=costs)
                static_results.append(npv_s)
                duration_static.append(len(log_s['cash_flow'])-1)
                
                npv_f, log_f = engine.run_simulation(prices, config, strategy_mode="FLEXIBLE", cost_profile=costs)
                flexible_results.append(npv_f)
                duration_flex.append(len(log_f['cash_flow'])-1)
                
                if i % (iters//20) == 0:
                    progress_bar.progress((i+1)/iters)
                    status_text.text(f"Simulating Scenario {i}/{iters}...")
            
            progress_bar.progress(100)
            status_text.empty()
            
            # --- RESULTS ---
            flex_arr = np.array(flexible_results)
            static_arr = np.array(static_results)
            flex_avg = np.mean(flex_arr)
            static_avg = np.mean(static_arr)
            val_add = flex_avg - static_avg
            prob_loss_static = np.mean(static_arr < 0) * 100
            prob_loss_flex = np.mean(flex_arr < 0) * 100
            var_05_static = np.percentile(static_arr, 5)
            var_05_flex = np.percentile(flex_arr, 5)
            
            # Volatility Reduction (Risk Squeeze)
            std_static = np.std(static_arr)
            std_flex = np.std(flex_arr)
            vol_reduction = (std_static - std_flex) / std_static * 100 if std_static > 0 else 0.0

            st.markdown("### `Comparative Investment Analysis`")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Static NPV (Mean)", f"${static_avg/1e6:.1f} M")
            k2.metric("Flexible NPV (Mean)", f"${flex_avg/1e6:.1f} M", delta_color="normal" if val_add > 0 else "off")
            k3.metric("Option Premium", f"${val_add/1e6:.1f} M", "Value of Flexibility")
            k4.metric("Avg Mine Life", f"{np.mean(duration_flex):.1f} yrs", f"vs {np.mean(duration_static):.1f} yrs")
            
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Prob. of Loss", f"{prob_loss_flex:.1f}%", f"vs {prob_loss_static:.1f}% (Static)")
            r2.metric("VaR (5% Case)", f"${var_05_flex/1e6:.1f} M", f"vs ${var_05_static/1e6:.1f} M")
            r3.metric("Volatility Reduction", f"{vol_reduction:.1f}%", "Risk Squeezed Out")
            r4.metric("Strategy Trigger", f"< ${config.HIGH_GRADE_TRIGGER_PRICE:.0f}/oz", "Activation Price")

            st.markdown("---")
            ex_rate = 87.0 
            inr_crores_static = (static_avg * ex_rate) / 10000000
            inr_crores_flex = (flex_avg * ex_rate) / 10000000
            st.info(f"🇮🇳 **Indian Context:** The Static Project Value is **₹{inr_crores_static:.1f} Crores**. With Strategic Real Options, this increases to **₹{inr_crores_flex:.1f} Crores**.")

            hist_data = [static_results, flexible_results]
            group_labels = ['Static Strategy', f'Flexible Strategy']
            colors = ['#EF553B', '#00CC96'] 
            fig = ff.create_distplot(hist_data, group_labels, show_hist=False, colors=colors)
            fig.add_vline(x=0, line_dash="dash", line_color="black")
            fig.update_layout(title_text="NPV Probability Distribution (Risk Profile Shift)", template="plotly_white")
            st.plotly_chart(fig, width="stretch")

def main():
    st.title("Mine Valuation Engine")
    # rest of your app code
    run_app()

if __name__ == "__main__":
    main()
