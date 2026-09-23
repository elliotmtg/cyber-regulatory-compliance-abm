"""
Cybersecurity Regulatory Compliance ABM Engine
==============================================
Implements `CyberComplianceModel` based on Mesa. Manages the 5-stage lifecycle:
  1. Context     (T=0 baseline initialization)
  2. Operating   (Normal compliance, feature development, oversight)
  3. Precursors  (Accumulation of business changes and unaddressed vulnerabilities)
  4. Recovering  (Post-incident remediation, compensation, enforcement)
  5. Outcomes    (Long-term institutional, legal, and operational legacy)

Empirical profiles are calibrated directly from 'Cases & Units-Grid view (3).csv'.
"""

import logging
import random
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import StakeholderAgent

logger = logging.getLogger("CyberComplianceModel")

# =====================================================================
# EMPIRICAL SCENARIO PROFILES (1-5 Scale from Cases & Units Dataset)
# =====================================================================
EMPIRICAL_PROFILES = {
    "catalangate_whatsapp": {
        "description": "CatalanGate / Pegasus: Advanced zero-click spyware targeting civil society; strict GDPR compliance vs state-level surveillance.",
        "Regulator": {
            "Context": {"Regulatory Environment": 4, "Threat Environment": 3, "Operational Environment": 4},
            "Operating": {"Rulemaking": 5, "Enforcement": 4, "Investigation": 5, "Influencing": 5},
            "Precursors": {"Regimes": 4, "Capacity": 5},
            "Recovering": {"Posturing": 5, "Compensating": 3, "Correcting/Enforcing": 5, "Complying": 5},
            "Outcomes": {"Costs": 5, "Remedies": 5, "Transformations": 4, "Preservation": 4}
        },
        "Software Producer": {
            "Context": {"Regulatory Environment": 5, "Threat Environment": 5, "Operational Environment": 3},
            "Operating": {"Implementing": 5, "Securing": 5, "Influencing": 5, "Complying": 5},
            "Precursors": {"Capacity": 5, "Business Change": 5, "Compliance": 5, "Unaddressed Failures & Weaknesses": 2},
            "Recovering": {"Posturing": 5, "Compensating": 3, "Correcting": 5, "Complying": 5},
            "Outcomes": {"Costs": 3, "Transformations": 5, "Preservation": 5, "Remedies": 5}
        },
        "User": {
            "Context": {"Regulatory Environment": 3, "Threat Environment": 5, "Operational Environment": 5},
            "Operating": {"Deploying": 5, "Securing": 1, "Influencing": 4, "Complying": 3},
            "Precursors": {"Capacity": 3, "Business Change": 4, "Compliance": 4, "Unaddressed Failures & Weaknesses": 3},
            "Recovering": {"Posturing": 5, "Compensating": 4, "Correcting": 5, "Complying": 3},
            "Outcomes": {"Costs": 1, "Transformations": 4, "Remedies": 3, "Preservation": 5}
        },
        "agent_counts": {"regulators": 2, "producers": 1, "users": 6}
    },
    "equifax_2017": {
        "description": "Equifax Data Breach (2017): High-value financial PII data, legacy patching gaps, massive regulatory scrutiny post-breach.",
        "Regulator": {
            "Context": {"Regulatory Environment": 5, "Threat Environment": 2, "Operational Environment": 5},
            "Operating": {"Rulemaking": 5, "Enforcement": 5, "Investigation": 5, "Influencing": 5},
            "Precursors": {"Regimes": 5, "Capacity": 5},
            "Recovering": {"Posturing": 5, "Compensating": 5, "Correcting/Enforcing": 5, "Complying": 5},
            "Outcomes": {"Costs": 5, "Remedies": 5, "Transformations": 1, "Preservation": 5}
        },
        "Software Producer": {
            "Context": {"Regulatory Environment": 5, "Threat Environment": 5, "Operational Environment": 1},
            "Operating": {"Implementing": 4, "Securing": 4, "Influencing": 5, "Complying": 5},
            "Precursors": {"Capacity": 3, "Business Change": 4, "Compliance": 3, "Unaddressed Failures & Weaknesses": 5},
            "Recovering": {"Posturing": 5, "Compensating": 1, "Correcting": 5, "Complying": 5},
            "Outcomes": {"Costs": 1, "Transformations": 5, "Preservation": 4, "Remedies": 3}
        },
        "User": {
            "Context": {"Regulatory Environment": 5, "Threat Environment": 5, "Operational Environment": 4},
            "Operating": {"Deploying": 2, "Securing": 2, "Influencing": 3, "Complying": 4},
            "Precursors": {"Capacity": 1, "Business Change": 4, "Compliance": 5, "Unaddressed Failures & Weaknesses": 3},
            "Recovering": {"Posturing": 5, "Compensating": 5, "Correcting": 1, "Complying": 2},
            "Outcomes": {"Costs": 2, "Transformations": 1, "Remedies": 5, "Preservation": 5}
        },
        "agent_counts": {"regulators": 2, "producers": 1, "users": 8}
    },
    "icrc_2022": {
        "description": "ICRC Data Breach (2022): Humanitarian data compromise, mission-first mandate, weak state regulatory frameworks.",
        "Regulator": {
            "Context": {"Regulatory Environment": 5, "Threat Environment": 3, "Operational Environment": 2},
            "Operating": {"Rulemaking": 4, "Enforcement": 2, "Investigation": 2, "Influencing": 4},
            "Precursors": {"Regimes": 4, "Capacity": 3},
            "Recovering": {"Posturing": 2, "Compensating": 1, "Correcting/Enforcing": 4, "Complying": 3},
            "Outcomes": {"Costs": 3, "Remedies": 3, "Transformations": 2, "Preservation": 4}
        },
        "Software Producer": {
            "Context": {"Regulatory Environment": 5, "Threat Environment": 5, "Operational Environment": 3},
            "Operating": {"Implementing": 4, "Securing": 5, "Influencing": 4, "Complying": 5},
            "Precursors": {"Capacity": 5, "Business Change": 2, "Compliance": 5, "Unaddressed Failures & Weaknesses": 4},
            "Recovering": {"Posturing": 5, "Compensating": 4, "Correcting": 5, "Complying": 5},
            "Outcomes": {"Costs": 3, "Transformations": 4, "Preservation": 5, "Remedies": 3}
        },
        "User": {
            "Context": {"Regulatory Environment": 4, "Threat Environment": 5, "Operational Environment": 5},
            "Operating": {"Deploying": 3, "Securing": 3, "Influencing": 1, "Complying": 5},
            "Precursors": {"Capacity": 2, "Business Change": 2, "Compliance": 5, "Unaddressed Failures & Weaknesses": 4},
            "Recovering": {"Posturing": 1, "Compensating": 1, "Correcting": 4, "Complying": 1},
            "Outcomes": {"Costs": 3, "Transformations": 1, "Remedies": 1, "Preservation": 5}
        },
        "agent_counts": {"regulators": 1, "producers": 1, "users": 6}
    },
    "illuminate_education_2025": {
        "description": "Illuminate Education (2025): K-12 student data breach resulting in multi-state Attorney General consortium enforcement.",
        "Regulator": {
            "Context": {"Regulatory Environment": 4, "Threat Environment": 3, "Operational Environment": 2},
            "Operating": {"Rulemaking": 4, "Enforcement": 2, "Investigation": 4, "Influencing": 2},
            "Precursors": {"Regimes": 1, "Capacity": 1},
            "Recovering": {"Posturing": 4, "Compensating": 3, "Correcting/Enforcing": 5, "Complying": 4},
            "Outcomes": {"Costs": 3, "Remedies": 3, "Transformations": 4, "Preservation": 3}
        },
        "Software Producer": {
            "Context": {"Regulatory Environment": 3, "Threat Environment": 4, "Operational Environment": 3},
            "Operating": {"Implementing": 5, "Securing": 3, "Influencing": 2, "Complying": 3},
            "Precursors": {"Capacity": 2, "Business Change": 5, "Compliance": 3, "Unaddressed Failures & Weaknesses": 5},
            "Recovering": {"Posturing": 5, "Compensating": 3, "Correcting": 2, "Complying": 3},
            "Outcomes": {"Costs": 1, "Transformations": 3, "Preservation": 4, "Remedies": 3}
        },
        "User": {
            "Context": {"Regulatory Environment": 3, "Threat Environment": 5, "Operational Environment": 5},
            "Operating": {"Deploying": 5, "Securing": 5, "Influencing": 3, "Complying": 3},
            "Precursors": {"Capacity": 3, "Business Change": 5, "Compliance": 3, "Unaddressed Failures & Weaknesses": 3},
            "Recovering": {"Posturing": 5, "Compensating": 5, "Correcting": 4, "Complying": 2},
            "Outcomes": {"Costs": 1, "Transformations": 3, "Remedies": 1, "Preservation": 3}
        },
        "agent_counts": {"regulators": 2, "producers": 1, "users": 7}
    },
    "opm_2016": {
        "description": "OPM Data Breach (2016): Compromise of 21.5M federal background check records across legacy federal IT systems.",
        "Regulator": {
            "Context": {"Regulatory Environment": 4, "Threat Environment": 2, "Operational Environment": 5},
            "Operating": {"Rulemaking": 5, "Enforcement": 4, "Investigation": 5, "Influencing": 5},
            "Precursors": {"Regimes": 5, "Capacity": 4},
            "Recovering": {"Posturing": 5, "Compensating": 3, "Correcting/Enforcing": 5, "Complying": 5},
            "Outcomes": {"Costs": 5, "Remedies": 5, "Transformations": 4, "Preservation": 4}
        },
        "Software Producer": {
            "Context": {"Regulatory Environment": 5, "Threat Environment": 5, "Operational Environment": 5},
            "Operating": {"Implementing": 5, "Securing": 2, "Influencing": 1, "Complying": 1},
            "Precursors": {"Capacity": 3, "Business Change": 5, "Compliance": 2, "Unaddressed Failures & Weaknesses": 5},
            "Recovering": {"Posturing": 5, "Compensating": 4, "Correcting": 3, "Complying": 2},
            "Outcomes": {"Costs": 1, "Transformations": 5, "Preservation": 3, "Remedies": 3}
        },
        "User": {
            "Context": {"Regulatory Environment": 5, "Threat Environment": 5, "Operational Environment": 5},
            "Operating": {"Deploying": 5, "Securing": 5, "Influencing": 2, "Complying": 5},
            "Precursors": {"Capacity": 3, "Business Change": 5, "Compliance": 3, "Unaddressed Failures & Weaknesses": 3},
            "Recovering": {"Posturing": 5, "Compensating": 5, "Correcting": 1, "Complying": 3},
            "Outcomes": {"Costs": 2, "Transformations": 5, "Remedies": 3, "Preservation": 3}
        },
        "agent_counts": {"regulators": 1, "producers": 1, "users": 6}
    }
}

SCENARIOS = EMPIRICAL_PROFILES


class CyberComplianceModel(Model):
    """
    ABM managing the 5-stage lifecycle for cybersecurity regulatory compliance.
    """

    def __init__(self, scenario_name="equifax_2017", total_steps=30, incident_step=10, width=10, height=10):
        super().__init__()
        self.scenario_name = scenario_name
        self.total_steps = total_steps
        self.incident_step = incident_step
        self.current_step_count = 0

        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True

        # -------------------------------------------------------------
        # 5-STAGE LIFECYCLE MANAGEMENT
        # -------------------------------------------------------------
        # Stages: 'Context' (T=0), 'Operating', 'Precursors', 'Recovering', 'Outcomes'
        self.current_stage = "Context"
        self.phase = 1
        self.incident_occurred = False

        # Partitioning step thresholds for human-auditable stage pacing
        self.step_precursors_start = max(2, incident_step // 2)
        self.step_outcomes_start = incident_step + max(2, (total_steps - incident_step) // 2)

        # -------------------------------------------------------------
        # POPULATE AGENTS WITH EMPIRICAL PROFILES
        # -------------------------------------------------------------
        if scenario_name == "random":
            self._init_random_scenario(width, height)
        else:
            self._init_empirical_scenario(scenario_name, width, height)

        # -------------------------------------------------------------
        # DATA COLLECTOR (Tracks macro and stage-disaggregated metrics)
        # -------------------------------------------------------------
        self.datacollector = DataCollector(
            model_reporters={
                "Step": lambda m: m.current_step_count,
                "Stage": lambda m: m.current_stage,
                "Phase": lambda m: m.phase,
                "IncidentOccurred": lambda m: int(m.incident_occurred),

                # Macro Core Metrics (1-5 scale)
                "AvgThreat": lambda m: m.get_average_threat(),
                "AvgOperationalCapacity": lambda m: m.get_average_op_cap(),
                "AvgRegulatoryPressure": lambda m: m.get_average_reg_press(),
                "ThreatGini": lambda m: m.calculate_gini([a.threat_level for a in m.schedule.agents]),

                # Disaggregated Stakeholder Averages
                "Regulator_AvgOpCap": lambda m: m.get_group_avg("regulator", "operational_capacity"),
                "Regulator_AvgRegPress": lambda m: m.get_group_avg("regulator", "regulatory_pressure"),
                "Producer_AvgThreat": lambda m: m.get_group_avg("producer", "threat_level"),
                "Producer_AvgOpCap": lambda m: m.get_group_avg("producer", "operational_capacity"),
                "Producer_AvgRegPress": lambda m: m.get_group_avg("producer", "regulatory_pressure"),
                "User_AvgThreat": lambda m: m.get_group_avg("user", "threat_level"),
                "User_AvgOpCap": lambda m: m.get_group_avg("user", "operational_capacity"),
                "User_AvgRegPress": lambda m: m.get_group_avg("user", "regulatory_pressure"),

                # Stage Behavioral Tracking (1-5 averages)
                "AvgPosturing": lambda m: m.get_attr_avg("rec_posturing"),
                "AvgCorrecting": lambda m: m.get_attr_avg("rec_correcting"),
                "AvgTransformations": lambda m: m.get_attr_avg("out_transformations"),
                "AvgPreservation": lambda m: m.get_attr_avg("out_preservation"),

                # Stage 2: Operating Behavioral Nodes
                "Regulator_Rulemaking": lambda m: m.get_group_avg("regulator", "op_rulemaking"),
                "Regulator_Enforcement": lambda m: m.get_group_avg("regulator", "op_enforcement"),
                "Regulator_Investigation": lambda m: m.get_group_avg("regulator", "op_investigation"),
                "Producer_Implementing": lambda m: m.get_group_avg("producer", "op_implementing"),
                "Producer_Securing": lambda m: m.get_group_avg("producer", "op_securing"),
                "Producer_Complying": lambda m: m.get_group_avg("producer", "op_complying"),
                "User_Deploying": lambda m: m.get_group_avg("user", "op_deploying"),
                "User_Securing": lambda m: m.get_group_avg("user", "op_securing"),
                "User_Influencing": lambda m: m.get_group_avg("user", "op_influencing"),

                # Stage 3: Precursor Risk Nodes
                "Producer_BusinessChange": lambda m: m.get_group_avg("producer", "precursor_business_change"),
                "Producer_Failures": lambda m: m.get_group_avg("producer", "precursor_failures"),
                "Regulator_PrecursorCapacity": lambda m: m.get_group_avg("regulator", "precursor_capacity"),

                # Stage 4: Recovering Action Nodes
                "Regulator_Posturing": lambda m: m.get_group_avg("regulator", "rec_posturing"),
                "Regulator_Correcting": lambda m: m.get_group_avg("regulator", "rec_correcting"),
                "Producer_Posturing": lambda m: m.get_group_avg("producer", "rec_posturing"),
                "Producer_Correcting": lambda m: m.get_group_avg("producer", "rec_correcting"),
                "Producer_Compensating": lambda m: m.get_group_avg("producer", "rec_compensating"),
                "User_Posturing": lambda m: m.get_group_avg("user", "rec_posturing"),
                "User_Compensating": lambda m: m.get_group_avg("user", "rec_compensating"),
                "User_Correcting": lambda m: m.get_group_avg("user", "rec_correcting"),

                # Stage 5: Outcomes Evaluation Nodes
                "Regulator_OutCosts": lambda m: m.get_group_avg("regulator", "out_costs"),
                "Regulator_OutTransformations": lambda m: m.get_group_avg("regulator", "out_transformations"),
                "Regulator_OutRemedies": lambda m: m.get_group_avg("regulator", "out_remedies"),
                "Regulator_OutPreservation": lambda m: m.get_group_avg("regulator", "out_preservation"),
                "Producer_OutCosts": lambda m: m.get_group_avg("producer", "out_costs"),
                "Producer_OutTransformations": lambda m: m.get_group_avg("producer", "out_transformations"),
                "Producer_OutRemedies": lambda m: m.get_group_avg("producer", "out_remedies"),
                "Producer_OutPreservation": lambda m: m.get_group_avg("producer", "out_preservation"),
                "User_OutCosts": lambda m: m.get_group_avg("user", "out_costs"),
                "User_OutTransformations": lambda m: m.get_group_avg("user", "out_transformations"),
                "User_OutRemedies": lambda m: m.get_group_avg("user", "out_remedies"),
                "User_OutPreservation": lambda m: m.get_group_avg("user", "out_preservation"),

                # Financial Ledgers ($)
                "Producer_TotalFinesPaid": lambda m: sum(a.fines_paid for a in m.schedule.agents if a.stakeholder_type == "producer"),
                "Producer_TotalCompPaid": lambda m: sum(a.compensation_paid for a in m.schedule.agents if a.stakeholder_type == "producer"),
                "Producer_NetCost": lambda m: sum(-a.wealth_or_cost for a in m.schedule.agents if a.stakeholder_type == "producer"),
                "User_TotalCompReceived": lambda m: sum(a.compensation_received for a in m.schedule.agents if a.stakeholder_type == "user"),
            },
            agent_reporters={
                "Type": lambda a: a.stakeholder_type,
                "SubType": lambda a: a.sub_type,
                "OperationalCapacity": lambda a: a.operational_capacity,
                "RegulatoryPressure": lambda a: a.regulatory_pressure,
                "ThreatLevel": lambda a: a.threat_level,
                "EnvReg": lambda a: getattr(a, "env_regulatory", 3),
                "EnvThreat": lambda a: getattr(a, "env_threat", 3),
                "EnvOp": lambda a: getattr(a, "env_operational", 3),
                "WealthOrCost": lambda a: a.wealth_or_cost,
                "FinesPaid": lambda a: a.fines_paid,
                "CompensationPaid": lambda a: a.compensation_paid,
                "CompensationReceived": lambda a: a.compensation_received
            }
        )

        logger.info("Initialized CyberComplianceModel with scenario '%s' (%d agents).", scenario_name, len(self.schedule.agents))

    def _init_empirical_scenario(self, scenario_name, width, height):
        """Initializes agents using the calibrated empirical profile for the scenario."""
        scenario_def = EMPIRICAL_PROFILES.get(scenario_name, EMPIRICAL_PROFILES["equifax_2017"])
        counts = scenario_def.get("agent_counts", {"regulators": 2, "producers": 1, "users": 6})

        # Regulators
        reg_prof = scenario_def["Regulator"]
        for idx in range(counts["regulators"]):
            agent = StakeholderAgent(f"reg_{idx}", self, "regulator", sub_type="oversight", empirical_profile=reg_prof)
            self.schedule.add(agent)
            self.grid.place_agent(agent, (random.randrange(width), random.randrange(height)))

        # Producers
        prod_prof = scenario_def["Software Producer"]
        for idx in range(counts["producers"]):
            agent = StakeholderAgent(f"prod_{idx}", self, "producer", sub_type="vendor", empirical_profile=prod_prof)
            self.schedule.add(agent)
            self.grid.place_agent(agent, (random.randrange(width), random.randrange(height)))

        # Users
        user_prof = scenario_def["User"]
        for idx in range(counts["users"]):
            agent = StakeholderAgent(f"user_{idx}", self, "user", sub_type="client", empirical_profile=user_prof)
            self.schedule.add(agent)
            self.grid.place_agent(agent, (random.randrange(width), random.randrange(height)))

    def _init_random_scenario(self, width, height):
        """Initializes randomized baseline agents for Monte Carlo / parameter sweep benchmarking."""
        num_regs = random.randint(2, 4)
        num_prods = random.randint(1, 3)
        num_users = random.randint(6, 12)

        def make_random_profile():
            return {
                "Context": {"Regulatory Environment": random.randint(1, 5), "Threat Environment": random.randint(1, 5), "Operational Environment": random.randint(1, 5)},
                "Operating": {"Rulemaking": random.randint(1, 5), "Enforcement": random.randint(1, 5), "Investigation": random.randint(1, 5), "Influencing": random.randint(1, 5),
                              "Implementing": random.randint(1, 5), "Securing": random.randint(1, 5), "Deploying": random.randint(1, 5), "Complying": random.randint(1, 5)},
                "Precursors": {"Capacity": random.randint(1, 5), "Business Change": random.randint(1, 5), "Compliance": random.randint(1, 5), "Regimes": random.randint(1, 5), "Unaddressed Failures & Weaknesses": random.randint(1, 5)},
                "Recovering": {"Posturing": random.randint(1, 5), "Compensating": random.randint(1, 5), "Correcting": random.randint(1, 5), "Correcting/Enforcing": random.randint(1, 5), "Complying": random.randint(1, 5)},
                "Outcomes": {"Costs": random.randint(1, 5), "Remedies": random.randint(1, 5), "Transformations": random.randint(1, 5), "Preservation": random.randint(1, 5)}
            }

        for idx in range(num_regs):
            agent = StakeholderAgent(f"reg_{idx}", self, "regulator", empirical_profile=make_random_profile())
            self.schedule.add(agent)
            self.grid.place_agent(agent, (random.randrange(width), random.randrange(height)))

        for idx in range(num_prods):
            agent = StakeholderAgent(f"prod_{idx}", self, "producer", empirical_profile=make_random_profile())
            self.schedule.add(agent)
            self.grid.place_agent(agent, (random.randrange(width), random.randrange(height)))

        for idx in range(num_users):
            agent = StakeholderAgent(f"user_{idx}", self, "user", empirical_profile=make_random_profile())
            self.schedule.add(agent)
            self.grid.place_agent(agent, (random.randrange(width), random.randrange(height)))

    # =================================================================
    # LIFECYCLE PROGRESSION & INCIDENT TRIGGER
    # =================================================================
    def update_stage(self):
        """Updates the active stage based on step count and incident state."""
        if not self.incident_occurred:
            self.phase = 1
            if self.current_step_count < self.step_precursors_start:
                self.current_stage = "Operating"
            else:
                self.current_stage = "Precursors"
        else:
            self.phase = 2
            if self.current_step_count < self.step_outcomes_start:
                self.current_stage = "Recovering"
            else:
                self.current_stage = "Outcomes"

    def trigger_incident(self):
        """Triggers the cybersecurity incident (data breach), transitioning from Phase 1 to Phase 2."""
        self.incident_occurred = True
        self.phase = 2
        self.current_stage = "Recovering"
        logger.warning("CYBER INCIDENT TRIGGERED at step %d for scenario '%s'!", self.current_step_count, self.scenario_name)

        # Incident impact shock
        for agent in self.schedule.agents:
            if agent.stakeholder_type == "producer":
                agent.threat_level = 5  # Critical breach vulnerability
                agent.wealth_or_cost -= 5000  # Initial crisis response costs
            elif agent.stakeholder_type == "user":
                agent.threat_level = min(5, agent.threat_level + 1)
            elif agent.stakeholder_type == "regulator":
                agent.regulatory_pressure = min(5, agent.regulatory_pressure + 1)

    def step(self):
        """Advances the simulation by one step through the 5-stage lifecycle."""
        self.current_step_count += 1

        # Check for incident trigger
        if not self.incident_occurred:
            if self.current_step_count >= self.incident_step or self.get_average_threat() >= 4.75:
                self.trigger_incident()

        self.update_stage()
        logger.info("--- Step %d | Stage: %s | Phase: %d ---", self.current_step_count, self.current_stage, self.phase)

        # Record data for this step and execute agents
        self.datacollector.collect(self)
        self.schedule.step()

    # =================================================================
    # STATISTICAL REPORTERS
    # =================================================================
    def get_group_avg(self, stakeholder_type, attribute):
        agents = [a for a in self.schedule.agents if a.stakeholder_type == stakeholder_type]
        if not agents:
            return 0.0
        return sum(getattr(a, attribute, 0.0) for a in agents) / len(agents)

    def get_attr_avg(self, attribute):
        agents = [a for a in self.schedule.agents if hasattr(a, attribute)]
        if not agents:
            return 0.0
        return sum(getattr(a, attribute) for a in agents) / len(agents)

    def get_average_threat(self):
        agents = self.schedule.agents
        if not agents:
            return 0.0
        return sum(a.threat_level for a in agents) / len(agents)

    def get_average_op_cap(self):
        agents = self.schedule.agents
        if not agents:
            return 0.0
        return sum(a.operational_capacity for a in agents) / len(agents)

    def get_average_reg_press(self):
        agents = self.schedule.agents
        if not agents:
            return 0.0
        return sum(a.regulatory_pressure for a in agents) / len(agents)

    def calculate_gini(self, values):
        """Calculates Gini coefficient measuring inequality in threat distribution."""
        if not values:
            return 0.0
        sorted_v = sorted(values)
        n = len(sorted_v)
        if n == 0 or sum(sorted_v) == 0:
            return 0.0
        cumulative = sum((i + 1) * v for i, v in enumerate(sorted_v))
        return (2 * cumulative) / (n * sum(sorted_v)) - (n + 1) / n
