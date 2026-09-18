# ODD Protocol: Cybersecurity Regulatory Compliance Model

**Model Version:** 1.2.0  
**Framework:** Mesa 2.3.0 in Python 3.11  
**Authors:** RCoder / Elliot  
**Standard Reference:** Grimm et al. (2006, 2010, 2020)

---

## I. OVERVIEW

### 1. Purpose and Patterns
The purpose of this Agent-Based Model (ABM) is to simulate and investigate the multi-phase dynamics of cybersecurity regulatory compliance between three interdependent stakeholders: **Regulators**, **Software Producers**, and **Users**.

The model is designed to reproduce several stylized patterns observed in empirical cybersecurity governance:
- The tension between software producers' operational velocity and cybersecurity investments.
- The constraint of regulatory capacity on enforcement actions.
- Pre-incident lobbying and advocacy feedback loops.
- Phase-transition dynamics following a major data breach (fines, compensatory restitution, compliance mandates).
- Unequal risk and cost distribution quantified via the Gini coefficient.

### 2. Entities, State Variables, and Scales

#### A. Entities
1. **Regulator Agents:** Represent national or local regulatory bodies possessing varying jurisdictional authority and operational enforcement capacity.
2. **Software Producer Agents:** Represent software-as-a-service platforms, healthcare systems, or infrastructure providers holding user data.
3. **User Agents:** Represent individual consumers, organizations, or high-profile targets whose data is entrusted to producers.
4. **Environment:** A toroidal 2D discrete grid (`MultiGrid`, default $10 \times 10$) facilitating local stakeholder interactions and proximity-based lobbying/advocacy.

#### B. State Variables (Scale: 1 to 5)
Each agent possesses three core internal state variables:
- **`operational_capacity` $\in \{1, 2, 3, 4, 5\}$:** Logistical, technical, and institutional ability to perform core tasks (enforce rules, build products, advocate).
- **`regulatory_pressure` $\in \{1, 2, 3, 4, 5\}$:** Stringency of oversight demanded, applied, or felt.
- **`threat_level` $\in \{1, 2, 3, 4, 5\}$:** Risk exposure, threat surface size, or vulnerability status.

#### C. Financial & Cumulative Variables
- `wealth_or_cost` (Float): Net financial balance (fines paid/collected, compensation, remediation costs).
- `fines_paid` (Float): Total regulatory penalties paid by a producer.
- `compensation_paid` (Float): Total remediation/monitoring damages paid by a producer to users.
- `compensation_received` (Float): Total compensatory damages received by users.

#### D. Temporal Scales
- **Time Step ($t$):** Discrete step representing one interaction and governance cycle.
- **Phases:**
  - **Phase 1 ($t < t_{\text{incident}}$):** Pre-incident normal operations and compliance dynamics.
  - **Phase 2 ($t \ge t_{\text{incident}}$):** Post-incident breach response, legal enforcement, and recovery.

### 3. Process Overview and Scheduling
Within each simulation tick ($t$):
1. **Phase & Incident Assessment:** The model checks whether the incident threshold (time step limit or average system threat level $\ge 4.5$) has been reached. If triggered, the model transitions to Phase 2.
2. **Agent Execution:** All agents execute their `step()` method using `RandomActivation` (randomized agent order per tick).
   - In **Phase 1**, agents update operational capacity, pressure, and threat levels through peer interaction.
   - In **Phase 2**, regulators enforce penalties, producers pay fines/remediation, and users seek restitution.
3. **Data Collection:** Model-level macro metrics (average threats, Gini coefficient, disaggregated stakeholder metrics, and financial totals) are recorded by `mesa.DataCollector`.

---

## II. DESIGN CONCEPTS

- **Basic Principles:** Principal-Agent theory, Institutional Economics, and Socio-Technical Regulatory Feedback Loops.
- **Emergence:** System-wide compliance resilience or regulatory failure emerges from micro-level capacity constraints and risk exposure.
- **Adaptation:** Software producers reduce threat levels in Phase 2 if operational capacity permits; regulators scale enforcement based on available capacity.
- **Objectives:** Regulators maximize compliance and minimize systemic threat; Producers minimize costs and maximize operational capacity; Users maximize security and compensation.
- **Interaction:** Regulators interact with co-located producers and users on the spatial grid during Phase 1, and globally enforce penalties during Phase 2.
- **Stochasticity:** Stochastic behavioral rules govern compliance investment probabilities, threat escalation, and spatial agent placement.
- **Observation:** Real-time data collectors track Gini coefficients, disaggregated group means, and cumulative financial totals.

---

## III. DETAILS

### 1. Initialization
The model supports two initialization modes:
1. **Real-World Incident Presets:**
   - `equifax_2017`: High-value financial PII breach with legacy patching gaps.
   - `catalangate_whatsapp`: Advanced zero-click spyware targeting high-profile civil society figures.
   - `opm_2016`: Federal background check breach across legacy IT systems.
   - `illuminate_education_2025`: K-12 student data breach resulting in multi-state Attorney General enforcement.
   - `icrc_2022`: Targeted humanitarian data compromise in a complex governance environment.
2. **Random Setup (`--scenario random`):** Randomly sampled agent distributions and attribute ratings for Monte Carlo parameter exploration.

### 2. Submodels & Key Equations

#### A. Regulatory Enforcement Submodel (Phase 2)
When a regulator ($r$) with `operational_capacity` $\ge 3$ audits producer ($p$):
$$\text{Fine}_{p} = (\text{ThreatLevel}_p \times \$1,000) + ((6 - \text{OperationalCapacity}_p) \times \$500)$$

#### B. Producer Remediation & User Restitution Submodel (Phase 2)
Producers provide credit monitoring and remediation compensation to users ($u$):
$$\text{Compensation}_{p \to u} = \$200 \times \text{ThreatLevel}_p$$
Users seek additional court damages:
$$\text{Damages}_{u} = \text{ThreatLevel}_p \times \$150$$

#### C. Threat Inequality (Gini Coefficient)
$$\text{Gini} = \frac{2 \sum_{i=1}^n i \cdot y_i}{n \sum_{i=1}^n y_i} - \frac{n + 1}{n}$$
where $y_i$ is the sorted vector of agent threat levels.
