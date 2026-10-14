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
    # AGGREGATE MONTE CARLO STATISTICS FOR RESEARCH PUBLICATION
    # =================================================================
    
    # 1. CORE ESSENTIAL 5 RESEARCH PAPER METRICS
    term_threat_series = df_runs["Terminal_AvgThreat"]
    net_cost_series = df_runs["Producer_NetCost"]
    
    threat_mean = term_threat_series.mean()
    threat_std = term_threat_series.std()
    threat_min = term_threat_series.min()
    threat_max = term_threat_series.max()

    breach_rate = 100.0  # Base scheduled breach is modeled in each run
    early_breach_rate = (df_runs["EarlyBreach"].sum() / runs) * 100.0
    remediation_rate = (df_runs["RemediationSuccess"].sum() / runs) * 100.0
    stability_rate = (df_runs["Stabilized"].sum() / runs) * 100.0

    mttr_mean = df_runs["MTTR_Ticks"].mean()
    mttr_std = df_runs["MTTR_Ticks"].std()
    mttr_median = df_runs["MTTR_Ticks"].median()

    cost_mean = net_cost_series.mean()
    cost_median = net_cost_series.median()
    cost_q25 = net_cost_series.quantile(0.25)
    cost_q75 = net_cost_series.quantile(0.75)
    cost_p95 = net_cost_series.quantile(0.95)
    cost_max = net_cost_series.max()

    restitution_mean = df_runs["RestitutionCoveragePct"].mean()
    user_comp_mean = df_runs["User_CompReceived"].mean()

    paper_summary_rows = [
        {
            "Research Metric": "1. Equilibrium System Threat",
            "Result (Summary)": f"{threat_mean:.2f} +/- {threat_std:.2f}",
            "Benchmark / Scale": f"1 - 5 Scale (Min: {threat_min:.2f}, Max: {threat_max:.2f})",
            "Academic Interpretation": "Post-intervention ecosystem vulnerability level"
        },
        {
            "Research Metric": "2. Early Precursor Breach Rate",
            "Result (Summary)": f"{early_breach_rate:.1f}%",
            "Benchmark / Scale": "0% - 100% of Runs",
            "Academic Interpretation": "Failure before scheduled tick due to unmitigated risk"
        },
        {
            "Research Metric": "3. Mean Time to Remediate (MTTR)",
            "Result (Summary)": f"{mttr_mean:.2f} +/- {mttr_std:.2f} ticks",
            "Benchmark / Scale": f"Discrete Steps (Median: {mttr_median:.1f})",
            "Academic Interpretation": "Organizational recovery velocity to safe threat (<= 2.0)"
        },
        {
            "Research Metric": "4. Producer Financial Burden",
            "Result (Summary)": f"Median: ${cost_median:,.0f} [IQR: ${cost_q25:,.0f} - ${cost_q75:,.0f}]",
            "Benchmark / Scale": f"Mean: ${cost_mean:,.0f} | Worst-Case: ${cost_max:,.0f}",
            "Academic Interpretation": "Total economic cost of fines, crisis response, and claims"
        },
        {
            "Research Metric": "5. User Restitution Share",
            "Result (Summary)": f"{restitution_mean:.1f}%",
            "Benchmark / Scale": f"Mean Restitution: ${user_comp_mean:,.0f} per run",
            "Academic Interpretation": "Fraction of producer penalty costs returned to victims"
        }
    ]
    df_paper_summary = pd.DataFrame(paper_summary_rows)

    # 2. STAKEHOLDER MACRO EQUILIBRIUM COMPARISON (1-5 Scale)
    stakeholder_rows = [
        {
            "Stakeholder Group": "Software Producers",
            "Threat Level (1-5)": f"{df_runs['Terminal_Producer_Threat'].mean():.2f} +/- {df_runs['Terminal_Producer_Threat'].std():.2f}",
            "Operational Capacity (1-5)": f"{df_runs['Terminal_Producer_OpCap'].mean():.2f} +/- {df_runs['Terminal_Producer_OpCap'].std():.2f}",
            "Regulatory Pressure (1-5)": "N/A (Target of Regulation)"
        },
        {
            "Stakeholder Group": "Users / Consumers",
            "Threat Level (1-5)": f"{df_runs['Terminal_User_Threat'].mean():.2f} +/- {df_runs['Terminal_User_Threat'].std():.2f}",
            "Operational Capacity (1-5)": "N/A",
            "Regulatory Pressure (1-5)": "N/A"
        },
        {
            "Stakeholder Group": "Regulators",
            "Threat Level (1-5)": "N/A",
            "Operational Capacity (1-5)": f"{df_runs['Regulator_Capacity_T0'].mean():.2f} +/- {df_runs['Regulator_Capacity_T0'].std():.2f}",
            "Regulatory Pressure (1-5)": f"{df_runs['Terminal_Regulator_RegPress'].mean():.2f} +/- {df_runs['Terminal_Regulator_RegPress'].std():.2f}"
        },
        {
            "Stakeholder Group": "Entire System (Average)",
            "Threat Level (1-5)": f"{threat_mean:.2f} +/- {threat_std:.2f}",
            "Operational Capacity (1-5)": f"{df_runs['Terminal_AvgOpCap'].mean():.2f} +/- {df_runs['Terminal_AvgOpCap'].std():.2f}",
            "Regulatory Pressure (1-5)": f"{df_runs['Terminal_AvgRegPress'].mean():.2f} +/- {df_runs['Terminal_AvgRegPress'].std():.2f}"
        }
    ]
    df_stakeholder_summary = pd.DataFrame(stakeholder_rows)

    # 3. RECOVERY & RESILIENCE DYNAMICS
    recovery_summary_rows = [
        {"Resilience Metric": "Remediation Success Rate", "Value": f"{remediation_rate:.1f}%", "Description": "Producer threat successfully reduced to <= 2.0 post-breach"},
        {"Resilience Metric": "Early Endogenous Breach Rate", "Value": f"{early_breach_rate:.1f}%", "Description": "Breached prior to scheduled incident step due to threat >= 4.75"},
        {"Resilience Metric": "Mean Time to Remediate (MTTR)", "Value": f"{mttr_mean:.2f} +/- {mttr_std:.2f} ticks", "Description": f"Median MTTR: {mttr_median:.1f} ticks to resolve vulnerability"},
        {"Resilience Metric": "System Stability Rate", "Value": f"{stability_rate:.1f}%", "Description": "Runs where final average threat stabilized <= 2.5"}
    ]
    df_recovery_summary = pd.DataFrame(recovery_summary_rows)

    # 4. ECONOMIC COSTS & RESTITUTION DISTRIBUTION
    financial_rows = [
        {"Economic Metric": "Mean Producer Total Cost", "Amount ($)": f"${cost_mean:,.2f}", "Description": "Average overall financial impact per producer"},
        {"Economic Metric": "Median Producer Total Cost", "Amount ($)": f"${cost_median:,.2f}", "Description": "Median overall financial impact (50th percentile)"},
        {"Economic Metric": "Interquartile Range (IQR: 25% - 75%)", "Amount ($)": f"${cost_q25:,.2f} - ${cost_q75:,.2f}", "Description": "Middle 50% distribution of producer costs"},
        {"Economic Metric": "High-Impact Scenario (95th Percentile)", "Amount ($)": f"${cost_p95:,.2f}", "Description": "Cost in the top 5% most severe regulatory outcomes"},
        {"Economic Metric": "Worst-Case Single Run Cost", "Amount ($)": f"${cost_max:,.2f}", "Description": "Maximum financial loss observed across all runs"},
        {"Economic Metric": "Average Victim Restitution Paid", "Amount ($)": f"${user_comp_mean:,.2f}", "Description": "Mean compensation received by affected users"},
        {"Economic Metric": "Restitution Share (%)", "Amount ($)": f"{restitution_mean:.1f}%", "Description": "Fraction of producer costs directly repairing user harm"}
    ]
    df_financial_summary = pd.DataFrame(financial_rows)

    # 5. PRECURSOR SENSITIVITY ATTRIBUTION (Spearman Rank Correlations)
    precursor_factors = ["Producer_BusinessChange_T0", "Producer_Failures_T0", "PrecursorRiskIndex_T0", "Regulator_Capacity_T0"]
    sensitivity_rows = []
    for factor in precursor_factors:
        corr_threat = df_runs[factor].rank().corr(df_runs["Terminal_AvgThreat"].rank())
        corr_cost = df_runs[factor].rank().corr(df_runs["Producer_NetCost"].rank())
        sensitivity_rows.append({
            "Precursor Factor": factor.replace("_T0", "").replace("_", " "),
            "Correlation with Threat (r)": round(corr_threat, 3) if not np.isnan(corr_threat) else 0.0,
            "Correlation with Cost (r)": round(corr_cost, 3) if not np.isnan(corr_cost) else 0.0,
            "Policy Impact": "Elevates Vulnerability" if corr_threat > 0.1 else ("Improves Security" if corr_threat < -0.1 else "Neutral")
        })
    df_sensitivity = pd.DataFrame(sensitivity_rows)

    # Save summary statistics CSV
    summary_csv_path = os.path.join(output_dir, "summary_statistics.csv")
    with open(summary_csv_path, "w", encoding="utf-8") as f:
        f.write("# 1. Core Paper Metrics\n")
        df_paper_summary.to_csv(f, index=False)
        f.write("\n# 2. Stakeholder Macro Equilibrium\n")
        df_stakeholder_summary.to_csv(f, index=False)
        f.write("\n# 3. Recovery and Resilience Dynamics\n")
        df_recovery_summary.to_csv(f, index=False)
        f.write("\n# 4. Economic Costs and Restitution\n")
        df_financial_summary.to_csv(f, index=False)
        f.write("\n# 5. Precursor Sensitivity Drivers\n")
        df_sensitivity.to_csv(f, index=False)

    # =================================================================
    # GENERATE MARKDOWN EXECUTIVE REPORT (PAPER READY)
    # =================================================================
    report_path = os.path.join(output_dir, "monte_carlo_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Monte Carlo Simulation Sweep: Academic Research Summary\n\n")
        f.write(f"- **Total Iterations (Runs):** `{runs}`\n")
        f.write(f"- **Simulation Steps:** `{steps}` | **Scheduled Incident Step:** `{incident_step}` | **Base Seed:** `{base_seed}`\n")
        f.write(f"- **Execution Timestamp:** `{datetime.now().isoformat()}`\n\n")
        f.write("---\n\n")

        f.write("## Table 1: Core Research Paper Metrics (Executive Overview)\n\n")
        f.write("The 5 primary statistical indicators recommended for academic publication:\n\n")
        f.write(df_to_markdown(df_paper_summary) + "\n\n")

        f.write("## Table 2: Stakeholder Macro Equilibrium (1–5 Scale)\n\n")
        f.write("Disaggregated post-intervention equilibrium states across stakeholder groups:\n\n")
        f.write(df_to_markdown(df_stakeholder_summary) + "\n\n")

        f.write("## Table 3: Organizational Resilience & Recovery Dynamics\n\n")
        f.write("Empirical metrics measuring breach prevention and remediation agility:\n\n")
        f.write(df_to_markdown(df_recovery_summary) + "\n\n")

        f.write("## Table 4: Economic Costs & Victim Restitution Distribution\n\n")
        f.write("Financial burden on software producers and compensation allocation to users:\n\n")
        f.write(df_to_markdown(df_financial_summary) + "\n\n")

        f.write("## Table 5: Sensitivity Analysis (Key Precursor Drivers)\n\n")
        f.write("Rank correlation evaluating which pre-breach precursor factors most heavily influence final threat and cost:\n\n")
        f.write(df_to_markdown(df_sensitivity) + "\n\n")

        f.write("---\n*Report generated by Cybersecurity Regulatory Compliance ABM Monte Carlo Engine for Academic Publication.*\n")

    # =================================================================
    # PRINT TERMINAL DASHBOARD
    # =================================================================
    if verbose:
        print("\n" + "=" * 80)
        print(f"--- MONTE CARLO RESEARCH RESULTS (N = {runs} Runs) ---")
        print("=" * 80)

        print("\n[ TABLE 1: CORE RESEARCH PAPER METRICS ]")
        print(df_paper_summary.to_string(index=False))

        print("\n[ TABLE 2: STAKEHOLDER MACRO EQUILIBRIUM (1-5 Scale) ]")
        print(df_stakeholder_summary.to_string(index=False))

        print("\n[ TABLE 3: RESILIENCE & RECOVERY DYNAMICS ]")
        print(df_recovery_summary.to_string(index=False))

        print("\n[ TABLE 4: ECONOMIC COSTS & RESTITUTION ]")
        print(df_financial_summary.to_string(index=False))

        print("\n[ TABLE 5: SENSITIVITY ANALYSIS (Precursor Drivers) ]")
        print(df_sensitivity.to_string(index=False))

        print("\n" + "=" * 80)
        print(f"Outputs successfully generated:")
        print(f"  - Raw Runs Dataset:     {os.path.abspath(runs_csv_path)}")
        print(f"  - Summary Statistics:   {os.path.abspath(summary_csv_path)}")
        print(f"  - Markdown Report:      {os.path.abspath(report_path)}")
        print("=" * 80 + "\n")

    return {
        "df_runs": df_runs,
        "df_paper_summary": df_paper_summary,
        "df_stakeholder_summary": df_stakeholder_summary,
        "df_recovery_summary": df_recovery_summary,
        "df_financial_summary": df_financial_summary,
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
