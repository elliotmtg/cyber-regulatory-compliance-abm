# Cybersecurity Regulatory Compliance ABM

An Agent-Based Model (ABM) built with **Mesa** simulating the multi-phase dynamics of cybersecurity regulatory compliance between three core stakeholders: **Regulators**, **Software Producers**, and **Users**.

The model captures interaction feedback loops across three properties rated on an integer scale of 1 to 5:
- **Operational Capacity**
- **Regulatory Pressure**
- **Threat Level**

---

## 5-Stage Empirical Lifecycle Architecture

The simulation models the multi-phase lifecycle calibrated from empirical incident analyses across 5 transparent stages:

### Phase 1: Pre-Incident Dynamics
1. **Stage 1 (Context, $T=0$):** Static environmental baseline (`Regulatory Environment`, `Threat Environment`, `Operational Environment`).
2. **Stage 2 (Operating):** Steady-state operations and mutual feedback loops:
   - *Regulators:* `Rulemaking`, `Enforcement`, `Investigation`, `Influencing`
   - *Software Producers:* `Implementing`, `Securing`, `Influencing`, `Complying`
   - *Users:* `Deploying`, `Securing`, `Influencing`, `Complying`
3. **Stage 3 (Precursors):** Risk destabilization and vulnerability accumulation:
   - *Producers & Users:* `Business Change` (M&A, rapid scaling, legacy drag), `Unaddressed Failures & Weaknesses`, `Capacity` constraints, and `Compliance` shortfalls.
   - *Regulators:* `Regimes` strictness and `Capacity` oversight gaps.

### Phase 2: Post-Incident Dynamics (Triggered upon Data Breach)
4. **Stage 4 (Recovering):** Immediate stakeholder friction and crisis management:
   - `Posturing` (PR, testimony, public outrage, legal stances)
   - `Compensating` (regulatory fines, user damages, credit monitoring)
   - `Correcting / Enforcing` (consent decrees, emergency patches, contract cancellations)
   - `Complying` (submitting to mandatory audits and reporting orders)
5. **Stage 5 (Outcomes):** Long-term systemic equilibrium and legacy evaluation:
   - `Costs` (financial, reputational, and operational penalties)
   - `Transformations` (governance restructuring, leadership changes, new coalitions)
   - `Remedies` (settlement resolution, legal precedents, policy overhauls)
   - `Preservation` (market survival, user retention, regime durability)

---

## Empirical Calibration & 1–5 Scale Mapping

Values are derived from empirical case analyses (`Cases & Units-Grid view (3).csv`) and standardized to a human-auditable 1–5 integer scale:

| Score | Activity / Stance | Environment / Capacity | Regime Strictness | Outcome Evaluation |
| :---: | :--- | :--- | :--- | :--- |
| **1** | Passive | Weak / Low / Simple | Lenient | Unfavorable |
| **2** | Somewhat Passive | Somewhat Weak / Low / Familiar | Somewhat Lenient | Somewhat Unfavorable |
| **3** | Neither Passive Nor Active | Neither Weak Nor Strong / Neutral | Neither Lenient Nor Strict | Neither Unfavorable Nor Favorable |
| **4** | Somewhat Active | Somewhat Strong / High / Risky | Somewhat Strict | Somewhat Favorable |
| **5** | Active | Strong / High / Risky / Challenging | Strict | Favorable |

---

## Features

- **Real-World Incident Preset Scenarios:**
  - `equifax_2017`: High-value financial PII data breach with legacy patching gaps and aggressive post-breach regulatory scrutiny.
  - `catalangate_whatsapp`: Advanced zero-click spyware targeting high-profile civil society figures.
  - `opm_2016`: Federal background check records compromised across legacy government IT infrastructure.
  - `illuminate_education_2025`: K-12 student data breach resulting in multi-state Attorney General enforcement mandates.
  - `icrc_2022`: Targeted humanitarian data compromise in a complex international governance environment.
  - `random`: Fully randomized initializations for stochastic baseline and Monte Carlo parameter sweeps.
- **Initial State Transparency ($T=0$):** Tabulates every agent's starting operational capacity, regulatory pressure, and threat level before execution.
- **5-Stage Summary Analytics:** Descriptive metrics (`mean`, `std`, `Gini`) broken down across each lifecycle stage (`Operating`, `Precursors`, `Recovering`, `Outcomes`).
- **Disaggregated Stakeholder Analytics:** Tracks individual sub-group averages for Regulators, Producers, and Users separately to prevent aggregation bias.
- **Human-Auditable Empirical Benchmarking:** Outputs a side-by-side comparison table between simulated terminal outcomes and the empirical case study benchmark.
- **Financial & Enforcement Tracking:** Quantifies total fines levied, damages/compensation paid, and net producer costs.
- **Reproducibility & Data Logging:** Generates `outputs/config.json`, `outputs/model_output.csv`, `outputs/agent_output.csv`, and `logs/simulation.log`.

---

## Installation & Setup

### Prerequisites
- Python 3.11+
- `uv` package manager (or Python virtual environments)

### Setup Virtual Environment

**macOS / Linux (Bash):**
```bash
git clone https://github.com/elliotmtg/cyber-regulatory-compliance-abm.git
cd cyber-regulatory-compliance-abm

# Create virtual environment and install pinned dependencies
uv venv .venv --python /usr/bin/python3
uv pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/elliotmtg/cyber-regulatory-compliance-abm.git
cd cyber-regulatory-compliance-abm

# Create virtual environment and install pinned dependencies
uv venv .venv --python 3.11
uv pip install -r requirements.txt
```

---

## Running the Simulation

### 1. Convenience Wrapper (Recommended)
Run with default settings (Equifax 2017 scenario, 30 steps, incident at step 10):

**macOS / Linux:**
```bash
./run.sh
```

**Windows (PowerShell):**
```powershell
.\run.ps1
```

*(Alternatively, call Python directly: `.\.venv\Scripts\python.exe run.py` on Windows or `.venv/bin/python run.py` on Linux/macOS)*

### 2. Custom Preset Scenarios
Specify any preset scenario using the `--scenario` flag:

**macOS / Linux:**
```bash
# Equifax 2017
./run.sh --scenario equifax_2017 --steps 30 --incident_step 10

# CatalanGate / Pegasus
./run.sh --scenario catalangate_whatsapp --steps 30 --incident_step 10

# OPM 2016
./run.sh --scenario opm_2016 --steps 30 --incident_step 10

# Illuminate Education 2025
./run.sh --scenario illuminate_education_2025 --steps 30 --incident_step 10

# ICRC 2022
./run.sh --scenario icrc_2022 --steps 30 --incident_step 10

# Stochastic / Monte Carlo Randomized Setup
./run.sh --scenario random --steps 50 --incident_step 15 --seed 123
```

**Windows (PowerShell):**
```powershell
# Equifax 2017
.\run.ps1 --scenario equifax_2017 --steps 30 --incident_step 10

# CatalanGate / Pegasus
.\run.ps1 --scenario catalangate_whatsapp --steps 30 --incident_step 10

# OPM 2016
.\run.ps1 --scenario opm_2016 --steps 30 --incident_step 10

# Illuminate Education 2025
.\run.ps1 --scenario illuminate_education_2025 --steps 30 --incident_step 10

# ICRC 2022
.\run.ps1 --scenario icrc_2022 --steps 30 --incident_step 10

# Stochastic / Monte Carlo Randomized Setup
.\run.ps1 --scenario random --steps 50 --incident_step 15 --seed 123
```

### 3. Command-Line Options
- `--scenario`: Preset incident name (`equifax_2017`, `catalangate_whatsapp`, `opm_2016`, `illuminate_education_2025`, `icrc_2022`, or `random`).
- `--steps`: Total simulation steps (default: `30`).
- `--incident_step`: Step at which the cybersecurity incident occurs (default: `10`).
- `--seed`: Random seed for reproducibility (default: `42`).
- `--output`: Output directory for generated CSVs and config JSON (default: `outputs`).

---

## Output Structure

Each run outputs the following artifacts:
- **`outputs/summary_report.md`**: Human-auditable executive Markdown summary including the Longitudinal Trajectory Matrix, stage behavioral dashboards, financial ledgers, and empirical validation audit scorecard.
- **`outputs/config.json`**: Exact simulation parameters, scenario name, seed, and timestamp.
- **`outputs/model_output.csv`**: Time-series macro metrics, Gini coefficients, and disaggregated stakeholder averages for every tick.
- **`outputs/agent_output.csv`**: Step-by-step state records for each individual agent.
- **`logs/simulation.log`**: Detailed event log of compliance enforcement, fines levied, and compensation paid.
