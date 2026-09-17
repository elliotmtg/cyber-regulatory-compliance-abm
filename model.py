import logging
import random
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import StakeholderAgent

logger = logging.getLogger("CyberComplianceModel")

class CyberComplianceModel(Model):
    """
    Agent-Based Model for Cybersecurity Regulatory Compliance.
    Simulates interactions between Regulators, Software Producers, and Users across two phases:
      - Phase 1: Normal operations, compliance pressure, threat evolution, leading up to an incident.
      - Phase 2: Incident response, remediation, fines, compensation, and recovery.
    """
    def __init__(self, num_regulators=3, num_producers=4, num_users=10, width=10, height=10, incident_step=15):
        super().__init__()
        self.num_regulators = num_regulators
        self.num_producers = num_producers
        self.num_users = num_users
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        
        self.running = True
        self.phase = 1
        self.incident_occurred = False
        self.incident_step = incident_step
        self.current_step_count = 0

        # Create Regulators
        reg_types = ["national", "local", "weak_regulator"]
        for i in range(self.num_regulators):
            stype = reg_types[i % len(reg_types)]
            agent = StakeholderAgent(f"reg_{i}", self, "regulator", sub_type=stype)
            self.schedule.add(agent)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

        # Create Software Producers
        prod_types = ["large_social", "mid_health", "standard"]
        for i in range(self.num_producers):
            stype = prod_types[i % len(prod_types)]
            agent = StakeholderAgent(f"prod_{i}", self, "producer", sub_type=stype)
            self.schedule.add(agent)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

        # Create Users
        user_types = ["high_profile", "regular"]
        for i in range(self.num_users):
            stype = user_types[i % len(user_types)]
            agent = StakeholderAgent(f"user_{i}", self, "user", sub_type=stype)
            self.schedule.add(agent)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

        # Data Collector setup
        self.datacollector = DataCollector(
            model_reporters={
                "Phase": lambda m: m.phase,
                "IncidentOccurred": lambda m: int(m.incident_occurred),
                "AvgThreat": lambda m: m.get_average_threat(),
                "AvgOperationalCapacity": lambda m: m.get_average_op_cap(),
                "AvgRegulatoryPressure": lambda m: m.get_average_reg_press(),
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
        logger.info("CyberComplianceModel initialized successfully with %d agents.", len(self.schedule.agents))

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

    def trigger_incident(self):
        """Triggers the cybersecurity incident where unauthorized access occurs."""
        self.incident_occurred = True
        self.phase = 2
        logger.warning("CYBERSECURITY INCIDENT TRIGGERED at step %d! Unauthorized access to user data stored by software producers.", self.current_step_count)
        
        # Incident impact on threat levels and capacity
        for agent in self.schedule.agents:
            if agent.stakeholder_type == "producer":
                agent.threat_level = min(5, agent.threat_level + 1)
                agent.wealth_or_cost -= 5000  # initial breach penalty/loss
            elif agent.stakeholder_type == "user":
                agent.threat_level = min(5, agent.threat_level + 1)
            elif agent.stakeholder_type == "regulator":
                agent.operational_capacity = min(5, agent.operational_capacity + 1) # mobilize

    def step(self):
        self.current_step_count += 1
        logger.info("--- Step %d (Phase %d) ---", self.current_step_count, self.phase)
        
        # Check if we should trigger the incident in Phase 1
        if self.phase == 1 and (self.current_step_count >= self.incident_step or self.get_average_threat() >= 4.0):
            self.trigger_incident()

        self.datacollector.collect(self)
        self.schedule.step()
