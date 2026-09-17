import logging
import random
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import StakeholderAgent

logger = logging.getLogger("CyberComplianceModel")

# Preset scenario definitions based on real-world incidents
SCENARIOS = {
    "equifax_2017": {
        "description": "Equifax Data Breach (2017): High-value financial PII data, large threat surface, legacy patching gaps, strong regulatory scrutiny post-breach.",
        "regulators": [
            {"sub_type": "national", "props": {"operational_capacity": 4, "regulatory_pressure": 5, "threat_level": 1}},
            {"sub_type": "local", "props": {"operational_capacity": 2, "regulatory_pressure": 3, "threat_level": 2}}
        ],
        "producers": [
            {"sub_type": "large_social", "props": {"operational_capacity": 2, "regulatory_pressure": 4, "threat_level": 5}}
        ],
        "users": [
            {"sub_type": "regular", "props": {"operational_capacity": 1, "regulatory_pressure": 2, "threat_level": 3}} for _ in range(8)
        ]
    },
    "catalangate_whatsapp": {
        "description": "CatalanGate / Pegasus spyware: Targeted high-profile civil society targets, advanced threat actors, sophisticated zero-click exploits, moderate baseline producer security.",
        "regulators": [
            {"sub_type": "national", "props": {"operational_capacity": 3, "regulatory_pressure": 4, "threat_level": 3}},
            {"sub_type": "weak_regulator", "props": {"operational_capacity": 1, "regulatory_pressure": 2, "threat_level": 2}}
        ],
        "producers": [
            {"sub_type": "large_social", "props": {"operational_capacity": 4, "regulatory_pressure": 3, "threat_level": 4}}
        ],
        "users": [
            {"sub_type": "high_profile", "props": {"operational_capacity": 5, "regulatory_pressure": 5, "threat_level": 5}} for _ in range(5)
        ]
    },
    "opm_2016": {
        "description": "OPM Data Breach (2016): Federal government background check records compromised, legacy IT systems, low operational capacity in cybersecurity, severe national security impact.",
        "regulators": [
            {"sub_type": "national", "props": {"operational_capacity": 2, "regulatory_pressure": 3, "threat_level": 4}}
        ],
        "producers": [
            {"sub_type": "mid_health", "props": {"operational_capacity": 1, "regulatory_pressure": 2, "threat_level": 5}}
        ],
        "users": [
            {"sub_type": "high_profile", "props": {"operational_capacity": 3, "regulatory_pressure": 4, "threat_level": 4}} for _ in range(6)
        ]
    },
    "illuminate_education_2025": {
        "description": "Illuminate Education (Multi-State AG Enforcement 2025): K-12 student data exposure, growing multi-state attorney general regulatory pressure, swift post-incident compliance mandates.",
        "regulators": [
            {"sub_type": "national", "props": {"operational_capacity": 5, "regulatory_pressure": 5, "threat_level": 2}},
            {"sub_type": "local", "props": {"operational_capacity": 4, "regulatory_pressure": 5, "threat_level": 2}}
        ],
        "producers": [
            {"sub_type": "mid_health", "props": {"operational_capacity": 3, "regulatory_pressure": 5, "threat_level": 4}}
        ],
        "users": [
            {"sub_type": "regular", "props": {"operational_capacity": 3, "regulatory_pressure": 4, "threat_level": 3}} for _ in range(7)
        ]
    },
    "icrc_2022": {
        "description": "International Committee of the Red Cross (ICRC 2022): Compromise of confidential humanitarian data, specialized high-value targeted infrastructure, weak initial regulatory frameworks for non-profits.",
        "regulators": [
            {"sub_type": "weak_regulator", "props": {"operational_capacity": 2, "regulatory_pressure": 2, "threat_level": 3}}
        ],
        "producers": [
            {"sub_type": "standard", "props": {"operational_capacity": 2, "regulatory_pressure": 2, "threat_level": 4}}
        ],
        "users": [
            {"sub_type": "high_profile", "props": {"operational_capacity": 2, "regulatory_pressure": 3, "threat_level": 4}} for _ in range(6)
        ]
    }
}

class CyberComplianceModel(Model):
    """
    Agent-Based Model for Cybersecurity Regulatory Compliance supporting real-world incident presets and random setups.
    """
    def __init__(self, scenario_name="equifax_2017", width=10, height=10, incident_step=10):
        super().__init__()
        self.scenario_name = scenario_name
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        
        self.running = True
        self.phase = 1
        self.incident_occurred = False
        self.incident_step = incident_step
        self.current_step_count = 0

        if scenario_name == "random":
            # Fully randomized setup across stakeholder types and properties
            num_regulators = random.randint(2, 4)
            num_producers = random.randint(3, 6)
            num_users = random.randint(8, 15)
            
            reg_types = ["national", "local", "weak_regulator"]
            for i in range(num_regulators):
                stype = random.choice(reg_types)
                agent = StakeholderAgent(f"reg_{i}", self, "regulator", sub_type=stype)
                self.schedule.add(agent)
                self.grid.place_agent(agent, (random.randrange(width), random.randrange(height)))

            prod_types = ["large_social", "mid_health", "standard"]
            for i in range(num_producers):
                stype = random.choice(prod_types)
                agent = StakeholderAgent(f"prod_{i}", self, "producer", sub_type=stype)
                self.schedule.add(agent)
                self.grid.place_agent(agent, (random.randrange(width), random.randrange(height)))

            user_types = ["high_profile", "regular"]
            for i in range(num_users):
                stype = random.choice(user_types)
                agent = StakeholderAgent(f"user_{i}", self, "user", sub_type=stype)
                self.schedule.add(agent)
                self.grid.place_agent(agent, (random.randrange(width), random.randrange(height)))
        else:
            # Load scenario configuration
            scenario_def = SCENARIOS.get(scenario_name, SCENARIOS["equifax_2017"])
            
            # Instantiate Regulators
            for idx, r_data in enumerate(scenario_def["regulators"]):
                agent = StakeholderAgent(f"reg_{idx}", self, "regulator", sub_type=r_data["sub_type"], custom_props=r_data["props"])
                self.schedule.add(agent)
                self.grid.place_agent(agent, (random.randrange(width), random.randrange(height)))

            # Instantiate Producers
            for idx, p_data in enumerate(scenario_def["producers"]):
                agent = StakeholderAgent(f"prod_{idx}", self, "producer", sub_type=p_data["sub_type"], custom_props=p_data["props"])
                self.schedule.add(agent)
                self.grid.place_agent(agent, (random.randrange(width), random.randrange(height)))

            # Instantiate Users
            for idx, u_data in enumerate(scenario_def["users"]):
                agent = StakeholderAgent(f"user_{idx}", self, "user", sub_type=u_data["sub_type"], custom_props=u_data["props"])
                self.schedule.add(agent)
                self.grid.place_agent(agent, (random.randrange(width), random.randrange(height)))

        # Data Collector setup with Gini coefficient and advanced distribution trackers
        self.datacollector = DataCollector(
            model_reporters={
                "Phase": lambda m: m.phase,
                "IncidentOccurred": lambda m: int(m.incident_occurred),
                "AvgThreat": lambda m: m.get_average_threat(),
                "AvgOperationalCapacity": lambda m: m.get_average_op_cap(),
                "AvgRegulatoryPressure": lambda m: m.get_average_reg_press(),
                "ThreatGini": lambda m: m.calculate_gini([a.threat_level for a in m.schedule.agents]),
            },
            agent_reporters={
                "Type": lambda a: a.stakeholder_type,
                "SubType": lambda a: a.sub_type,
                "OperationalCapacity": lambda a: a.operational_capacity,
                "RegulatoryPressure": lambda a: a.regulatory_pressure,
                "ThreatLevel": lambda a: a.threat_level,
                "WealthOrCost": lambda a: a.wealth_or_cost
            }
        )
        logger.info("CyberComplianceModel initialized with preset scenario '%s' (%d agents).", scenario_name, len(self.schedule.agents))

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
        """Calculates the Gini coefficient for a list of values."""
        if not values:
            return 0.0
        sorted_v = sorted(values)
        n = len(sorted_v)
        if n == 0 or sum(sorted_v) == 0:
            return 0.0
        cumulative = sum((i + 1) * v for i, v in enumerate(sorted_v))
        return (2 * cumulative) / (n * sum(sorted_v)) - (n + 1) / n

    def trigger_incident(self):
        self.incident_occurred = True
        self.phase = 2
        logger.warning("CYBERSECURITY INCIDENT TRIGGERED at step %d for scenario '%s'!", self.current_step_count, self.scenario_name)
        
        for agent in self.schedule.agents:
            if agent.stakeholder_type == "producer":
                agent.threat_level = min(5, agent.threat_level + 1)
                agent.wealth_or_cost -= 5000
            elif agent.stakeholder_type == "user":
                agent.threat_level = min(5, agent.threat_level + 1)
            elif agent.stakeholder_type == "regulator":
                agent.operational_capacity = min(5, agent.operational_capacity + 1)

    def step(self):
        self.current_step_count += 1
        logger.info("--- Step %d (Phase %d) ---", self.current_step_count, self.phase)
        
        if self.phase == 1 and (self.current_step_count >= self.incident_step or self.get_average_threat() >= 4.5):
            self.trigger_incident()

        self.datacollector.collect(self)
        self.schedule.step()
