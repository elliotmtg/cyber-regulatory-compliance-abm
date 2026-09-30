# ODD Protocol: Cybersecurity Regulatory Compliance Model

**Model Version:** 2.0.0 (Empirical 5-Stage Lifecycle & Actuarial Risk Extension)  
**Framework:** Mesa 2.3.0 in Python 3.11  
**Authors:** RCoder / Elliot  
**Standard Reference:** Grimm et al. (2006, 2010, 2020)

---

## I. OVERVIEW

### 1. Purpose and Patterns
The purpose of this Agent-Based Model (ABM) is to simulate, analyze, and stress-test the multi-stage dynamics of cybersecurity regulatory compliance between three interdependent stakeholder groups: **Regulators**, **Software Producers**, and **Users**.

Following the principles of **Pattern-Oriented Modeling (POM)** (Grimm et al., 2005), the model is calibrated against empirical case analyses (`Cases & Units-Grid view (3).csv`) across five real-world cybersecurity breaches:
- **Equifax (2017):** Massive financial PII breach, legacy technical debt, aggressive multi-agency post-breach regulatory scrutiny.
- **CatalanGate / Pegasus (WhatsApp, 2019–2022):** Targeted zero-click spyware exploitation of civil society figures; strict EU GDPR data privacy governance vs. state surveillance.
- **OPM (2015–2016):** Compromise of 21.5M federal background check records across legacy government IT infrastructure.
- **Illuminate Education (2022–2025):** K-12 student PII exposure resulting in multi-state Attorney General consortium enforcement and FTC consent orders.
- **ICRC (2022):** Targeted humanitarian data compromise in a complex international governance framework with non-profit mission constraints.

The model reproduces several key empirical macro patterns:
1. **The Velocity–Security Trade-off:** Producers accumulate hidden security debt when feature deployment outpaces proactive hardening.
2. **Precursor Risk Build-up:** Incidents are preceded by organizational destabilization (M&A, rapid scaling, unaddressed patching backlogs) that erodes capacity.
3. **Responsive Enforcement Pyramids:** Post-breach regulatory escalation moves from administrative posturing to monetary penalties, mandatory audits, and structural governance consent decrees.
4. **Heavy-Tailed Actuarial Risk:** Cyber liabilities exhibit extreme tail risk, where average costs underestimate catastrophic loss scenarios.
5. **Asymmetric Risk Dispersion:** Threat levels and operational recovery are unequally distributed across stakeholders, tracked via the Gini coefficient.

---

### 2. Entities, State Variables, and Scales

#### A. Entities
1. **Regulator Agents:** Federal/national agencies, state attorneys general, or sector-specific overseers with statutory rulemaking, audit, and enforcement powers.
2. **Software Producer Agents:** Commercial software vendors, cloud platforms, or institutional data custodians maintaining user data.
3. **User Agents:** Heterogeneous consumer bases, enterprise clients, or high-profile civil society targets utilizing producer software.
4. **Spatial Topology:** A toroidal 2D discrete grid (`MultiGrid`, default $10 \times 10$) representing local jurisdictional adjacency and peer influence.

#### B. Core Internal State Variables (Bounded Integer Scale: $1 \dots 5$)
All qualitative attributes are mapped to a standardized, human-auditable 1–5 scale:
- **`operational_capacity` $\in \{1, 2, 3, 4, 5\}$:** Institutional, logistical, and technical ability to execute core responsibilities (enforce, build, or self-defend).
- **`regulatory_pressure` $\in \{1, 2, 3, 4, 5\}$:** Oversight intensity exerted, demanded, or experienced.
- **`threat_level` $\in \{1, 2, 3, 4, 5\}$:** Threat surface area, vulnerability severity, or exploitation exposure.

#### C. Empirical Stage-Specific Behavioral Variables ($1 \dots 5$)
Calibrated directly from empirical case study nodes:
- **Stage 1 (Context Baseline):** `env_regulatory`, `env_threat`, `env_operational`.
- **Stage 2 (Operating):**
  - *Regulators:* `op_rulemaking`, `op_enforcement`, `op_investigation`, `op_influencing`.
  - *Producers:* `op_implementing`, `op_securing`, `op_influencing`, `op_complying`.
  - *Users:* `op_deploying`, `op_securing`, `op_influencing`, `op_complying`.
- **Stage 3 (Precursors):** `precursor_capacity`, `precursor_business_change`, `precursor_compliance`, `precursor_failures`.
- **Stage 4 (Recovering):** `rec_posturing`, `rec_compensating`, `rec_correcting`, `rec_complying`.
- **Stage 5 (Outcomes):** `out_costs`, `out_transformations`, `out_remedies`, `out_preservation`.

#### D. Financial Ledgers (Float, Currency $)
- `wealth_or_cost`: Cumulative financial balance (revenues, fines, crisis response expenses, user compensation).
- `fines_paid`: Cumulative administrative penalties paid to regulatory authorities.
- `compensation_paid`: Cumulative damages and credit monitoring compensation paid by producers to users.
- `compensation_received`: Cumulative restitution received by users.

#### E. Temporal Scales & Lifecycle Stages
- **Time Step ($t$):** Discrete tick representing one administrative/operational cycle.
- **The 5-Stage Empirical Progression:**
  - **Stage 1: Context ($t = 0$):** Static environmental baseline setup.
  - **Stage 2: Operating ($1 \le t \le \lfloor K/2 \rfloor$):** Routine steady-state governance, feature release, and cyber hygiene.
  - **Stage 3: Precursors ($\lfloor K/2 \rfloor + 1 \le t \le K$):** Risk destabilization, M&A integration drag, and unaddressed vulnerability build-up.
  - **Incident Trigger ($t = K$ or $\text{AvgThreat} \ge 4.75$):** Data breach event transition from Phase 1 to Phase 2.
  - **Stage 4: Recovering ($K + 1 \le t \le K + \lfloor(N-K)/2\rfloor$):** Post-breach enforcement, fines, PR posturing, user litigation, and technical patching.
  - **Stage 5: Outcomes ($K + \lfloor(N-K)/2\rfloor + 1 \le t \le N$):** Long-term institutionalization, legal precedents, structural reforms, and market preservation.

---

### 3. Process Overview and Scheduling

Within each simulation step ($t$):
1. **Stage & Incident Evaluation:**
   - Evaluates whether scheduled breach tick ($K$) or endogenous threat ceiling ($\text{AvgThreat} \ge 4.75$) has been met.
   - If triggered, invokes `trigger_incident()`, elevating producer threat to $5/5$, assessing initial crisis costs ($-\$5,000$), and shifting system state from Phase 1 to Phase 2 (`Recovering`).
   - Updates `model.current_stage` according to temporal step thresholds.
2. **Agent Activation:**
   - Executes agent steps using Mesa's `RandomActivation` scheduler (randomizing agent execution order per tick to prevent positional bias).
   - Each agent executes the behavioral method corresponding to the active stage (`step_operating()`, `step_precursors()`, `step_recovering()`, or `step_outcomes()`).
   - Post-step boundaries are enforced using `clamp(val, 1, 5)`.
3. **Data Collection:**
   - `mesa.DataCollector` records system-level macro averages, Gini inequality, disaggregated stakeholder scores, stage-specific behavioral nodes, and cumulative financial totals.

---

## II. DESIGN CONCEPTS

- **Basic Principles:**
  - *Responsive Regulation:* Regulatory enforcement follows an escalating pyramid of sanctions (Ayres & Braithwaite, 1992).
  - *Normalization of Deviance & Latent Failures:* Pre-incident risk accumulates incrementally as organizations accept unpatched vulnerabilities and organizational change (Vaughan, 1996; Reason, 1997, 2000).
  - *Security Technical Debt:* Prioritizing feature delivery over security hardening induces systemic fragility (Kruchten et al., 2012).
  - *Economics of Information Security:* Market externalities lead to under-investment in security because breach costs fall disproportionately on third-party users (Anderson & Moore, 2006).
  - *Heavy-Tailed Actuarial Cyber Risk:* Cyber breach damages follow Pareto-type power-law distributions, requiring extreme tail-risk metrics (Wheatley et al., 2016; Eling & Wirfs, 2016).
- **Emergence:** Macro stability or systemic breakdown emerges from micro-level interactions between regulator audit capacity, producer security debt, and user advocacy pressure.
- **Adaptation:** Producers adjust security investments post-breach under regulatory orders; regulators scale fines based on observed threat and producer capacity gaps.
- **Objectives:** Regulators minimize ecosystem vulnerability and deter negligence; Producers balance feature velocity with regulatory compliance costs; Users seek data protection and monetary restitution.
- **Sensing:** Regulators sense market threat levels through investigative audits and localized user complaints; producers sense regulatory pressure through audits and neighbor citations.
- **Interaction:** Agents interact via spatial grid proximity during Phase 1 (lobbying and complaints), and globally across the jurisdictional schedule during Phase 2 (fines, restitution payments, and class-action damages).
- **Stochasticity:** Bounded random probabilities model human fallibility: enforcement lapses, lobbying effectiveness, security debt accumulation, and early breach triggering.
- **Observation:** Complete time-series data logging to CSV, automated longitudinal stage trajectory matrices, side-by-side empirical audit tables, and batch Monte Carlo parameter sweeps.

---

## III. DETAILS

### 1. Initialization and Empirical Data Calibration

The model integrates empirical case data from `Cases & Units-Grid view (3).csv`. Qualitative ratings are standardized to the 1–5 integer scale:

| Qualitative Rating | Score | Activity / Stance | Environment / Capacity | Regime Strictness | Outcome Evaluation |
| :---: | :---: | :--- | :--- | :--- | :--- |
| **Passive / Weak / Low / Lenient / Unfavorable** | **1** | Passive | Weak / Low / Simple | Lenient | Unfavorable |
| **Somewhat Passive / Low / Lenient / Unfavorable** | **2** | Somewhat Passive | Somewhat Weak / Low / Familiar | Somewhat Lenient | Somewhat Unfavorable |
| **Neither / Moderate / Neutral** | **3** | Moderate | Neither Weak Nor Strong | Neutral | Neutral |
| **Somewhat Active / High / Strict / Favorable** | **4** | Somewhat Active | Somewhat Strong / High / Risky | Somewhat Strict | Somewhat Favorable |
| **Active / Strong / High / Strict / Favorable** | **5** | Active | Strong / High / Challenging / Risky | Strict | Favorable |

Scenarios are instantiated via two pathways:
1. **Calibrated Historical Presets:** Pre-configured profiles for `equifax_2017`, `catalangate_whatsapp`, `opm_2016`, `illuminate_education_2025`, and `icrc_2022`.
2. **Stochastic Random Sweeps (`--scenario random` / `--monte_carlo`):** Uniformly randomized initializations across agent populations ($2\dots4$ regulators, $1\dots3$ producers, $6\dots12$ users) and empirical profiles for Monte Carlo sweeps.

---

### 2. Submodels and Governing Equations

#### A. Operating Submodel: Security Debt & Compliance Friction
In Stage 2, producers balance feature velocity (`op_implementing`) against proactive hardening (`op_securing`):
$$\text{Security Debt Gap} = \text{op\_implementing} - \text{op\_securing}$$
If $\text{Security Debt Gap} > 0$, threat increases with probability $p = 0.30$.

Regulators evaluate system threat via investigation:
$$\text{If } \overline{\text{Threat}} \ge 3 \text{ and } \text{op\_investigation} \ge 3 \implies \text{regulatory\_pressure} \leftarrow \min(5, \text{regulatory\_pressure} + 1)$$

#### B. Precursor Submodel: Latent Risk Accumulation
In Stage 3, latent organizational fragility compounds:
$$\text{Precursor Vulnerability Index} = \frac{\text{precursor\_business\_change} + \text{precursor\_failures}}{\max(1, \text{operational\_capacity})}$$
- If `precursor_business_change` $\ge 4$ (e.g., M&A restructuring, rapid scaling), producer capacity drains with probability $p = 0.40$.
- If `precursor_failures` $\ge 4$ (unpatched CVEs, unencrypted data), producer threat increments directly.
- If regulator `precursor_capacity` $\le 2$, regulatory oversight lapses, reducing pressure.

#### C. Endogenous Incident Trigger Submodel
The breach occurs at tick $t = K$, or endogenously whenever cumulative precursor risk pushes average system threat past the critical stability limit:
$$\text{Incident Trigger Condition} = (t \ge K) \lor (\overline{\text{Threat}}_t \ge 4.75)$$

#### D. Recovering Submodel: Responsive Enforcement & Restitution
In Stage 4, regulators levy fines scaled to threat severity, enforcement posture, and producer negligence:
$$\text{Fine}_{p} = \left(\text{ThreatLevel}_p \times \$1,000 \times \frac{\text{rec\_compensating}}{3}\right) + \left((6 - \text{OperationalCapacity}_p) \times \$500\right)$$
Regulators retain a 10% administrative recovery fee, while 90% serves as a deterrent sanction.

Producers issue user restitution and credit monitoring fees:
$$\text{Compensation}_{p \to u} = \$200 \times \text{ThreatLevel}_p$$
Users seek class-action damages:
$$\text{Damages}_{u} = \text{ThreatLevel}_p \times \$150$$

#### E. Outcomes Submodel: Systemic Legacy & Equilibrium
In Stage 5, terminal equilibrium is established:
- High producer `out_transformations` ($\ge 4$) locks in permanent technical remediation ($\text{Threat} \leftarrow \max(1, \text{Threat} - 1)$).
- High producer `out_preservation` ($\ge 4$) stabilizes operational capacity ($\text{OpCap} \leftarrow \min(5, \text{OpCap} + 1)$).
- High regulatory `out_remedies` or `out_transformations` ($\ge 4$) institutionalizes permanent oversight vigilance.

#### F. Threat Inequality Submodel (Gini Coefficient)
Measures the dispersion of cyber threat exposure across the population:
$$\text{Gini} = \frac{2 \sum_{i=1}^n i \cdot y_i}{n \sum_{i=1}^n y_i} - \frac{n + 1}{n}$$
where $y_i$ is the vector of sorted agent threat levels ($y_1 \le y_2 \le \dots \le y_n$).

#### G. Actuarial Cyber Tail-Risk Submodel (Monte Carlo Sweeps)
Across $M$ stochastic runs, net producer financial burden ($L = \text{Producer\_NetCost}$) is evaluated using extreme-value risk metrics:
1. **Value at Risk ($\text{VaR}_\alpha$):**
   $$\text{VaR}_\alpha = \inf \{ l \in \mathbb{R} : \mathcal{P}(L > l) \le 1 - \alpha \}$$
   computed at $\alpha \in \{0.90, 0.95, 0.99\}$.
2. **Conditional Value at Risk ($\text{CVaR}_{0.95}$ / Expected Shortfall):**
   $$\text{CVaR}_{0.95} = \mathbb{E}\left[L \mid L \ge \text{VaR}_{0.95}\right]$$
   Quantifies the expected loss in the worst 5% tail-risk regulatory enforcement scenarios.
3. **Mean Time to Remediate (MTTR):**
   $$\text{MTTR} = \frac{1}{M}\sum_{i=1}^M \left(T_{\text{remediation}, i} - T_{\text{breach}, i}\right)$$
   measuring the average tick latency until producer threat drops $\le 2.0$.
4. **Precursor Risk Attribution (Spearman Rank Correlation $\rho$):**
   $$\rho = 1 - \frac{6 \sum d_i^2}{M(M^2 - 1)}$$
   attributing final threat and net cost variance to pre-breach precursor factors.

---

## IV. ACADEMIC REFERENCES

1. **Anderson, R., & Moore, T. (2006).** "The economics of information security." *Science*, 314(5799), 610–613. [DOI: 10.1126/science.1130992]
2. **Ayres, I., & Braithwaite, J. (1992).** *Responsive Regulation: Transcending the Deregulation Debate.* Oxford University Press. [ISBN: 978-0195070705]
3. **Eling, M., & Wirfs, J. H. (2016).** *Cyber Risk: Too Big to Insure? Risk Transfer Options for a Mercurial Risk Class.* Institute of Insurance Economics, University of St. Gallen. [DOI: 10.2139/ssrn.2801452]
4. **Farmer, J. D., & Foley, D. (2009).** "The economy needs agent-based modelling." *Nature*, 460(7256), 685–686. [DOI: 10.1038/460685a]
5. **Gini, C. (1912).** *Variabilità e mutabilità.* Reprinted in *Memorie di metodologica statistica* (Ed. Pizetti, E., Salvemini, T.). Rome: Libreria Eredi Virgilio Veschi (1955).
6. **Grimm, V., Revilla, E., Berger, U., Jeltsch, F., Mooij, W. M., Railsback, S. F., Sauermann, H., Skov-Petersen, H., Tobias, S., & DeAngelis, D. L. (2005).** "Pattern-oriented modeling of agent-based complex systems: Lessons from ecology." *Science*, 310(5750), 987–991. [DOI: 10.1126/science.1116681]
7. **Grimm, V., Berger, U., Bastiansen, F., Eliassen, S., Ginot, V., Giske, J., Goss-Custard, J., Grand, T., Heinz, S. K., Huse, G., Huth, A., Jepsen, J. U., Jørgensen, C., Mooij, W. M., Müller, B., Pe'er, G., Piou, C., Railsback, S. F., Robbins, A. M., ... & DeAngelis, D. L. (2006).** "A standard protocol for describing individual-based and agent-based models." *Ecological Modelling*, 198(1-2), 115–126. [DOI: 10.1016/j.ecolmodel.2006.04.023]
8. **Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., Giske, J., Groeneveld, J., Johnston, A. S., Milles, A., Nabe-Nielsen, J., Polhill, J. G., Radchuk, V., Rohwäder, M. S., Stillman, R. A., Thiele, J. C., & Ayllón, D. (2020).** "The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and outreach." *Journal of Artificial Societies and Social Simulation*, 23(2), 7. [DOI: 10.18564/jasss.4259]
9. **Kruchten, P., Nord, R. L., & Ozkaya, I. (2012).** "Technical debt: From metaphor to theory and practice." *IEEE Software*, 29(6), 18–21. [DOI: 10.1109/MS.2012.167]
10. **Reason, J. (1997).** *Managing the Risks of Organizational Accidents.* Ashgate Publishing. [ISBN: 978-1840141054]
11. **Reason, J. (2000).** "Human error: models and management." *British Medical Journal*, 320(7237), 768–770. [DOI: 10.1136/bmj.320.7237.768]
12. **Rockafellar, R. T., & Uryasev, S. (2000).** "Optimization of conditional value-at-risk." *Journal of Risk*, 2(3), 21–41. [DOI: 10.21314/JOR.2000.038]
13. **Solove, D. J., & Hartzog, W. (2014).** "The FTC and the new common law of privacy." *Columbia Law Review*, 114(3), 583–676.
14. **Vaughan, D. (1996).** *The Challenger Launch Decision: Risky Technology, Culture, and Deviance at NASA.* University of Chicago Press. [ISBN: 978-0226851761]
15. **Wheatley, S., Maillart, T., & Sornette, D. (2016).** "The extreme risk of personal data breaches and the erosion of privacy." *The European Physical Journal B*, 89(1), 1–12. [DOI: 10.1140/epjb/e2015-60754-4]
