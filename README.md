# Cybersecurity Regulatory Compliance ABM

An Agent-Based Model (ABM) built with **Mesa** simulating the multi-phase dynamics of cybersecurity regulatory compliance between three core stakeholders: **Regulators**, **Software Producers**, and **Users**.

The model captures interaction feedback loops across three properties rated on an integer scale of 1 to 5:
- **Operational Capacity**
- **Regulatory Pressure**
- **Threat Level**

The simulation advances across two distinct phases:
1. **Phase 1 (Pre-Incident):** Normal business and governance interactions, compliance investments, threat surface evolution, and lobbying/advocacy pressures.
2. **Phase 2 (Post-Incident):** Triggered when an attacker breaches producer-stored user data. Stakeholders respond by maximizing gains and minimizing losses (regulatory fines, court damages, credit monitoring compensation, security improvements, and capacity rebuilding).

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
- **Phase-Segregated Statistics:** Separate descriptive metrics (`mean`, `std`, `min`, `max`, `quartiles`) for Phase 1 vs. Phase 2.
- **Disaggregated Stakeholder Analytics:** Tracks individual sub-group averages for Regulators, Producers, and Users separately to prevent aggregation bias.
- **Inequality & Distribution Metrics:** Measures threat dispersion using the **Gini coefficient** over time.
- **Financial & Enforcement Tracking:** Quantifies total fines levied, damages/compensation paid, and net producer costs.
- **Reproducibility & Data Logging:** Generates `outputs/config.json`, `outputs/model_output.csv`, `outputs/agent_output.csv`, and `logs/simulation.log`.

---

## Installation & Setup

### Prerequisites
- Python 3.11+
- `uv` package manager (or Python virtual environments)

### Setup Virtual Environment
```bash
git clone https://github.com/elliotmtg/cyber-regulatory-compliance-abm.git
cd cyber-regulatory-compliance-abm

# Create virtual environment and install pinned dependencies
uv venv .venv --python /usr/bin/python3
uv pip install -r requirements.txt
```

---

## Running the Simulation

### 1. Convenience Shell Wrapper (Recommended)
Run with default settings (Equifax 2017 scenario, 30 steps, incident at step 10):
```bash
./run.sh
```

### 2. Custom Preset Scenarios
Specify any preset scenario using the `--scenario` flag:

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

### 3. Command-Line Options
- `--scenario`: Preset incident name (`equifax_2017`, `catalangate_whatsapp`, `opm_2016`, `illuminate_education_2025`, `icrc_2022`, or `random`).
- `--steps`: Total simulation steps (default: `30`).
- `--incident_step`: Step at which the cybersecurity incident occurs (default: `10`).
- `--seed`: Random seed for reproducibility (default: `42`).
- `--output`: Output directory for generated CSVs and config JSON (default: `outputs`).

---

## Output Structure

Each run outputs the following artifacts:
- **`outputs/config.json`**: Exact simulation parameters, scenario name, seed, and timestamp.
- **`outputs/model_output.csv`**: Time-series macro metrics, Gini coefficients, and disaggregated stakeholder averages for every tick.
- **`outputs/agent_output.csv`**: Step-by-step state records for each individual agent.
- **`logs/simulation.log`**: Detailed event log of compliance enforcement, fines levied, and compensation paid.
