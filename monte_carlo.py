"""
Monte Carlo Parameter Sweeps for Cybersecurity Regulatory Compliance ABM
========================================================================
Executes stochastic parameter sweeps using randomized scenario initializations
to quantify emergent systemic stability, recovery dynamics, actuarial financial
tail risk (VaR & CVaR), and precursor sensitivity drivers.

Outputs:
  - outputs/monte_carlo/runs.csv (Individual run sample paths)
  - outputs/monte_carlo/summary_statistics.csv (Aggregated descriptive metrics)
  - outputs/monte_carlo/monte_carlo_report.md (Executive Markdown summary report)
"""

import argparse
import json
import logging
import os
import random
import numpy as np
import pandas as pd
from datetime import datetime
from model import CyberComplianceModel

logger = logging.getLogger("CyberComplianceModel")


def df_to_markdown(df):
    """Converts a pandas DataFrame to a GitHub-flavored Markdown table without external dependencies."""
    if df is None or df.empty:
        return ""
    headers = [str(c) for c in df.columns]
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join([":---" for _ in headers]) + " |"
    data_lines = []
    for _, row in df.iterrows():
        row_vals = [str(val) for val in row]
        data_lines.append("| " + " | ".join(row_vals) + " |")
    return "\n".join([header_line, separator_line] + data_lines)


def run_monte_carlo(runs=100, steps=30, incident_step=10, base_seed=42, output_dir="outputs/monte_carlo", verbose=True):
    """
    Executes M Monte Carlo simulation runs using the stochastic 'random' scenario.
    """
    os.makedirs(output_dir, exist_ok=True)

    if verbose:
        print("\n" + "=" * 80)
        print(f"--- STARTING MONTE CARLO SWEEP: {runs} RUNS (Random Scenarios) ---")
        print(f"Steps: {steps} | Scheduled Incident Step: {incident_step} | Base Seed: {base_seed}")
        print(f"Output Directory: {os.path.abspath(output_dir)}")
        print("=" * 80)

    run_records = []

    for run_idx in range(1, runs + 1):
        seed = base_seed + run_idx
        random.seed(seed)
        np.random.seed(seed)

        model = CyberComplianceModel(
            scenario_name="random",
            total_steps=steps,
            incident_step=incident_step
        )

        # -------------------------------------------------------------
        # 1. INITIAL PRECURSOR CONDITIONS (T = 0)
        # -------------------------------------------------------------
        prod_biz_change = model.get_group_avg("producer", "precursor_business_change")
        prod_failures = model.get_group_avg("producer", "precursor_failures")
        prod_cap_t0 = model.get_group_avg("producer", "operational_capacity")
        reg_cap_t0 = model.get_group_avg("regulator", "operational_capacity")
        reg_rp_t0 = model.get_group_avg("regulator", "regulatory_pressure")
        user_threat_t0 = model.get_group_avg("user", "threat_level")
        precursor_risk_idx = round((prod_biz_change + prod_failures) / max(1.0, prod_cap_t0), 2)

        # -------------------------------------------------------------
        # 2. RUN SIMULATION & TRACK RECOVERY DYNAMICS
        # -------------------------------------------------------------
        breach_step = None
        remediation_step = None

        for step_num in range(1, steps + 1):
            model.step()

            # Record breach step
            if model.incident_occurred and breach_step is None:
                breach_step = model.current_step_count

            # Track recovery: first tick where producer threat drops <= 2.0 post-breach
            if model.incident_occurred and breach_step is not None and remediation_step is None:
                prod_threat_now = model.get_group_avg("producer", "threat_level")
                if prod_threat_now <= 2.0:
                    remediation_step = model.current_step_count

        # Post-simulation recovery metrics
        early_breach = 1 if (breach_step is not None and breach_step < incident_step) else 0
        actual_breach_step = breach_step if breach_step is not None else incident_step

        if remediation_step is not None:
            mttr_ticks = remediation_step - actual_breach_step
            remediation_success = 1
        else:
            mttr_ticks = steps - actual_breach_step
            remediation_success = 0

        # -------------------------------------------------------------
        # 3. TERMINAL STEP METRICS
        # -------------------------------------------------------------
        term_threat = model.get_average_threat()
        term_opcap = model.get_average_op_cap()
        term_regpress = model.get_average_reg_press()
        term_gini = model.calculate_gini([a.threat_level for a in model.schedule.agents])

        term_prod_threat = model.get_group_avg("producer", "threat_level")
        term_prod_opcap = model.get_group_avg("producer", "operational_capacity")
        term_user_threat = model.get_group_avg("user", "threat_level")
        term_reg_regpress = model.get_group_avg("regulator", "regulatory_pressure")

        fines_paid = sum(a.fines_paid for a in model.schedule.agents if a.stakeholder_type == "producer")
        comp_paid = sum(a.compensation_paid for a in model.schedule.agents if a.stakeholder_type == "producer")
        net_cost = sum(-a.wealth_or_cost for a in model.schedule.agents if a.stakeholder_type == "producer")
        user_comp = sum(a.compensation_received for a in model.schedule.agents if a.stakeholder_type == "user")
        restitution_pct = (user_comp / net_cost * 100) if net_cost > 0 else 0.0

        run_records.append({
            "RunID": run_idx,
            "Seed": seed,
            # Precursors (T=0)
            "Producer_BusinessChange_T0": prod_biz_change,
            "Producer_Failures_T0": prod_failures,
            "Producer_Capacity_T0": prod_cap_t0,
            "Regulator_Capacity_T0": reg_cap_t0,
            "Regulator_RegPressure_T0": reg_rp_t0,
            "User_Threat_T0": user_threat_t0,
            "PrecursorRiskIndex_T0": precursor_risk_idx,
            # Breach & Recovery Dynamics
            "BreachStep": actual_breach_step,
            "EarlyBreach": early_breach,
            "RemediationSuccess": remediation_success,
            "MTTR_Ticks": mttr_ticks,
            # Terminal Macro State
            "Terminal_AvgThreat": term_threat,
            "Terminal_AvgOpCap": term_opcap,
            "Terminal_AvgRegPress": term_regpress,
            "Terminal_ThreatGini": term_gini,
            # Terminal Stakeholder Averages
            "Terminal_Producer_Threat": term_prod_threat,
            "Terminal_Producer_OpCap": term_prod_opcap,
            "Terminal_User_Threat": term_user_threat,
            "Terminal_Regulator_RegPress": term_reg_regpress,
            # Financial Ledger
            "Producer_FinesPaid": fines_paid,
            "Producer_CompPaid": comp_paid,
            "Producer_NetCost": net_cost,
            "User_CompReceived": user_comp,
            "RestitutionCoveragePct": restitution_pct,
            "Stabilized": 1 if term_threat <= 2.5 else 0
        })

        if verbose and (run_idx % max(1, runs // 10) == 0 or run_idx == runs):
            print(f"  [Progress] Completed {run_idx}/{runs} runs ({(run_idx/runs)*100:.0f}%) | Seed {seed} | Breach: Step {actual_breach_step} | Threat: {term_threat:.2f} | NetCost: ${net_cost:,.0f}")

    df_runs = pd.DataFrame(run_records)
    runs_csv_path = os.path.join(output_dir, "runs.csv")
    df_runs.to_csv(runs_csv_path, index=False)

    # =================================================================
    # AGGREGATE MONTE CARLO STATISTICS
    # =================================================================
    # 1. Macro Equilibrium Distributions
    macro_cols = ["Terminal_AvgThreat", "Terminal_AvgOpCap", "Terminal_AvgRegPress", "Terminal_ThreatGini"]
    macro_summary_rows = []
    for col in macro_cols:
        series = df_runs[col]
        q25 = series.quantile(0.25)
        q75 = series.quantile(0.75)
        macro_summary_rows.append({
            "Metric": col.replace("Terminal_", "").replace("_", " "),
            "Mean": round(series.mean(), 3),
            "StdDev": round(series.std(), 3),
            "Median": round(series.median(), 3),
            "Q25 (25%)": round(q25, 3),
            "Q75 (75%)": round(q75, 3),
            "IQR": round(q75 - q25, 3),
            "Min": round(series.min(), 3),
            "Max": round(series.max(), 3)
        })
    df_macro_summary = pd.DataFrame(macro_summary_rows)

    stability_rate = (df_runs["Stabilized"].sum() / runs) * 100.0

    # 2. Breach & Recovery Statistics
    early_breach_rate = (df_runs["EarlyBreach"].sum() / runs) * 100.0
    remediation_rate = (df_runs["RemediationSuccess"].sum() / runs) * 100.0
    mttr_mean = df_runs["MTTR_Ticks"].mean()
    mttr_std = df_runs["MTTR_Ticks"].std()
    mttr_median = df_runs["MTTR_Ticks"].median()

    recovery_summary_rows = [
        {"Dynamic Metric": "Early Endogenous Breach Rate (%)", "Value": f"{early_breach_rate:.1f}%", "Description": "Breached prior to scheduled incident step due to threat >= 4.75"},
        {"Dynamic Metric": "Remediation Success Rate (%)", "Value": f"{remediation_rate:.1f}%", "Description": "Producer threat successfully reduced to <= 2.0 post-breach"},
        {"Dynamic Metric": "Mean Time to Remediate (MTTR)", "Value": f"{mttr_mean:.2f} +/- {mttr_std:.2f} ticks", "Description": f"Median MTTR: {mttr_median:.1f} ticks to resolve vulnerability"},
        {"Dynamic Metric": "System Stability Rate (%)", "Value": f"{stability_rate:.1f}%", "Description": "Percentage of runs where final average threat stabilized <= 2.5"}
    ]
    df_recovery_summary = pd.DataFrame(recovery_summary_rows)

    # 3. Financial Tail-Risk Metrics (Actuarial Cyber Risk)
    net_costs = df_runs["Producer_NetCost"]
    exp_loss = net_costs.mean()
    var_90 = net_costs.quantile(0.90)
    var_95 = net_costs.quantile(0.95)
    var_99 = net_costs.quantile(0.99)
    cvar_95 = net_costs[net_costs >= var_95].mean() if len(net_costs[net_costs >= var_95]) > 0 else var_95
    mean_restitution = df_runs["RestitutionCoveragePct"].mean()

    tail_risk_rows = [
        {"Tail Risk Metric": "Expected Producer Burden (E[L])", "Amount ($)": f"${exp_loss:,.2f}", "Interpretation": "Mean financial burden across all stochastic environments"},
        {"Tail Risk Metric": "Value at Risk (VaR 90%)", "Amount ($)": f"${var_90:,.2f}", "Interpretation": "90% confidence upper loss limit"},
        {"Tail Risk Metric": "Value at Risk (VaR 95%)", "Amount ($)": f"${var_95:,.2f}", "Interpretation": "95% confidence upper loss limit (1-in-20 year loss)"},
        {"Tail Risk Metric": "Value at Risk (VaR 99%)", "Amount ($)": f"${var_99:,.2f}", "Interpretation": "99% confidence upper loss limit (1-in-100 catastrophic loss)"},
        {"Tail Risk Metric": "Conditional VaR (CVaR 95%)", "Amount ($)": f"${cvar_95:,.2f}", "Interpretation": "Expected Shortfall: Mean loss in the worst 5% black-swan runs"},
        {"Tail Risk Metric": "Average Restitution Coverage", "Amount ($)": f"{mean_restitution:.1f}%", "Interpretation": "Mean percentage of producer burden directed to user compensation"}
    ]
    df_tail_risk = pd.DataFrame(tail_risk_rows)

    # 4. Precursor Sensitivity & Attribution (Spearman Rank Correlations via rank().corr())
    precursor_factors = ["Producer_BusinessChange_T0", "Producer_Failures_T0", "PrecursorRiskIndex_T0", "Regulator_Capacity_T0"]
    sensitivity_rows = []
    for factor in precursor_factors:
        corr_threat = df_runs[factor].rank().corr(df_runs["Terminal_AvgThreat"].rank())
        corr_cost = df_runs[factor].rank().corr(df_runs["Producer_NetCost"].rank())
        sensitivity_rows.append({
            "Precursor Factor": factor.replace("_T0", "").replace("_", " "),
            "Spearman Corr (vs. Final Threat)": round(corr_threat, 3) if not np.isnan(corr_threat) else 0.0,
            "Spearman Corr (vs. Net Cost)": round(corr_cost, 3) if not np.isnan(corr_cost) else 0.0,
            "Sensitivity Direction": "Elevates Risk" if corr_threat > 0.1 else ("Mitigates Risk" if corr_threat < -0.1 else "Neutral")
        })
    df_sensitivity = pd.DataFrame(sensitivity_rows)

    # Save summary statistics CSV
    summary_csv_path = os.path.join(output_dir, "summary_statistics.csv")
    with open(summary_csv_path, "w", encoding="utf-8") as f:
        f.write("# 1. Macro Equilibrium Summary\n")
        df_macro_summary.to_csv(f, index=False)
        f.write("\n# 2. Recovery & Breach Dynamics\n")
        df_recovery_summary.to_csv(f, index=False)
        f.write("\n# 3. Financial Tail Risk (VaR / CVaR)\n")
        df_tail_risk.to_csv(f, index=False)
        f.write("\n# 4. Precursor Sensitivity Drivers\n")
        df_sensitivity.to_csv(f, index=False)

    # =================================================================
    # GENERATE MARKDOWN EXECUTIVE REPORT
    # =================================================================
    report_path = os.path.join(output_dir, "monte_carlo_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Monte Carlo Simulation Sweep Executive Report\n\n")
        f.write(f"- **Total Iterations (Runs):** `{runs}`\n")
        f.write(f"- **Simulation Steps:** `{steps}` | **Scheduled Incident Step:** `{incident_step}` | **Base Seed:** `{base_seed}`\n")
        f.write(f"- **Execution Timestamp:** `{datetime.now().isoformat()}`\n\n")
        f.write("---\n\n")

        f.write("## 1. Macro Equilibrium & Distribution Statistics (Terminal Step)\n\n")
        f.write(df_to_markdown(df_macro_summary) + "\n\n")
        f.write(f"- **System Stability Rate:** **`{stability_rate:.1f}%`** of runs successfully stabilized with terminal threat $\\le 2.5$.\n\n")

        f.write("## 2. Breach & Recovery Velocity Dynamics\n\n")
        f.write(df_to_markdown(df_recovery_summary) + "\n\n")

        f.write("## 3. Financial Tail-Risk & Actuarial Metrics (Producer Burden)\n\n")
        f.write(df_to_markdown(df_tail_risk) + "\n\n")
        f.write(f"> [!IMPORTANT]\n")
        f.write(f"> **Value at Risk (95%):** Under 95% of market conditions, producer losses will not exceed **${var_95:,.2f}**. In the worst 5% tail risk cases (CVaR 95%), losses surge to an average of **${cvar_95:,.2f}**.\n\n")

        f.write("## 4. Precursor Sensitivity & Vulnerability Attribution\n\n")
        f.write("Spearman rank correlation $(\\rho)$ evaluating which pre-breach precursor factors most heavily drive catastrophic losses:\n\n")
        f.write(df_to_markdown(df_sensitivity) + "\n\n")

        f.write("---\n*Report generated by Cybersecurity Regulatory Compliance ABM Monte Carlo Engine.*\n")

    # =================================================================
    # PRINT TERMINAL DASHBOARD
    # =================================================================
    if verbose:
        print("\n" + "=" * 80)
        print(f"--- MONTE CARLO SWEEP RESULTS (N = {runs} Runs) ---")
        print("=" * 80)

        print("\n[ 1. MACRO EQUILIBRIUM DISTRIBUTIONS ]")
        print(df_macro_summary.to_string(index=False))
        print(f"  >> System Stability Rate (Threat <= 2.5): {stability_rate:.1f}%")

        print("\n[ 2. BREACH & RECOVERY DYNAMICS ]")
        print(df_recovery_summary.to_string(index=False))

        print("\n[ 3. ACTUARIAL FINANCIAL TAIL RISK (VaR & CVaR) ]")
        print(df_tail_risk.to_string(index=False))

        print("\n[ 4. PRECURSOR SENSITIVITY DRIVERS (Spearman Rank Correlation) ]")
        print(df_sensitivity.to_string(index=False))

        print("\n" + "=" * 80)
        print(f"Outputs successfully generated:")
        print(f"  - Raw Runs Dataset:     {os.path.abspath(runs_csv_path)}")
        print(f"  - Summary Statistics:   {os.path.abspath(summary_csv_path)}")
        print(f"  - Markdown Report:      {os.path.abspath(report_path)}")
        print("=" * 80 + "\n")

    return {
        "df_runs": df_runs,
        "df_macro_summary": df_macro_summary,
        "df_recovery_summary": df_recovery_summary,
        "df_tail_risk": df_tail_risk,
        "df_sensitivity": df_sensitivity
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute Monte Carlo sweeps for Cybersecurity Compliance ABM.")
    parser.add_argument("--runs", type=int, default=100, help="Number of Monte Carlo iterations (default: 100).")
    parser.add_argument("--steps", type=int, default=30, help="Simulation steps per run (default: 30).")
    parser.add_argument("--incident_step", type=int, default=10, help="Scheduled incident step (default: 10).")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed (default: 42).")
    parser.add_argument("--output", type=str, default="outputs/monte_carlo", help="Directory for outputs.")

    args = parser.parse_args()
    run_monte_carlo(
        runs=args.runs,
        steps=args.steps,
        incident_step=args.incident_step,
        base_seed=args.seed,
        output_dir=args.output
    )
