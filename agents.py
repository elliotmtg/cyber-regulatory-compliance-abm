import logging
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random

logger = logging.getLogger("CyberComplianceModel")

class StakeholderAgent(Agent):
    """
    Base Agent class representing a stakeholder in the cyber regulatory compliance ecosystem.
    Stakeholder types: 'regulator', 'producer', 'user'.
    Properties (scale 1 to 5):
      - operational_capacity (op_cap)
      - regulatory_pressure (reg_press)
      - threat_level (threat)
    """
    def __init__(self, unique_id, model, stakeholder_type, sub_type=None, custom_props=None):
        super().__init__(unique_id, model)
        self.stakeholder_type = stakeholder_type
        self.sub_type = sub_type
        
        if custom_props:
            self.operational_capacity = custom_props.get("operational_capacity", 3)
            self.regulatory_pressure = custom_props.get("regulatory_pressure", 3)
            self.threat_level = custom_props.get("threat_level", 3)
        else:
            self._initialize_properties()
        
        self.wealth_or_cost = 0.0
        self.fines_paid = 0.0
        self.compensation_paid = 0.0
        self.compensation_received = 0.0

    def _initialize_properties(self):
        if self.stakeholder_type == "regulator":
            if self.sub_type == "national":
                self.operational_capacity = 4
                self.regulatory_pressure = 4
            elif self.sub_type == "weak_regulator":
                self.operational_capacity = 1
                self.regulatory_pressure = 1
            else:
                self.operational_capacity = 2
                self.regulatory_pressure = 3
            self.threat_level = 2

        elif self.stakeholder_type == "producer":
            if self.sub_type == "large_social":
                self.operational_capacity = 4
                self.regulatory_pressure = 4
                self.threat_level = 5
            elif self.sub_type == "mid_health":
                self.operational_capacity = 2
                self.regulatory_pressure = 3
                self.threat_level = 4
            else:
                self.operational_capacity = 3
                self.regulatory_pressure = 3
                self.threat_level = 3

        elif self.stakeholder_type == "user":
            if self.sub_type == "high_profile":
                self.operational_capacity = 4
                self.regulatory_pressure = 4
                self.threat_level = 4
            else:
                self.operational_capacity = 2
                self.regulatory_pressure = 2
                self.threat_level = 2

    def step(self):
        if self.model.phase == 1:
            self.step_phase_one()
        else:
            self.step_phase_two()

    def step_phase_one(self):
        neighbors = self.model.grid.get_cell_list_contents([self.pos])
        
        if self.stakeholder_type == "regulator":
            avg_threat = self.model.get_average_threat()
            if avg_threat >= 3 and self.operational_capacity >= 2:
                self.regulatory_pressure = min(5, self.regulatory_pressure + 1)
            elif self.operational_capacity <= 1 and random.random() < 0.3:
                self.regulatory_pressure = max(1, self.regulatory_pressure - 1)
                
            for n in neighbors:
                if n.stakeholder_type == "user":
                    if n.regulatory_pressure >= 4:
                        self.regulatory_pressure = min(5, self.regulatory_pressure + 1)
                elif n.stakeholder_type == "producer":
                    if n.operational_capacity >= 4 and random.random() < 0.4:
                        self.regulatory_pressure = max(1, self.regulatory_pressure - 1)

        elif self.stakeholder_type == "producer":
            if self.regulatory_pressure >= 4:
                if random.random() < 0.5:
                    self.operational_capacity = max(1, self.operational_capacity - 1)
            else:
                if random.random() < 0.4 and self.operational_capacity < 5:
                    self.operational_capacity += 1
                    self.threat_level = min(5, self.threat_level + 1)
            
            if random.random() < 0.3:
                self.operational_capacity = min(5, self.operational_capacity + 1)

        elif self.stakeholder_type == "user":
            producers = [agent for agent in self.model.schedule.agents if agent.stakeholder_type == "producer"]
            if producers:
                avg_prod_threat = sum(p.threat_level for p in producers) / len(producers)
                if avg_prod_threat >= 4 and random.random() < 0.5:
                    self.threat_level = min(5, self.threat_level + 1)
            
            for n in neighbors:
                if n.stakeholder_type == "regulator" and self.regulatory_pressure >= 4:
                    n.regulatory_pressure = min(5, n.regulatory_pressure + 1)

        self.operational_capacity = max(1, min(5, self.operational_capacity))
        self.regulatory_pressure = max(1, min(5, self.regulatory_pressure))
        self.threat_level = max(1, min(5, self.threat_level))

    def step_phase_two(self):
        if not self.model.incident_occurred:
            return

        if self.stakeholder_type == "regulator":
            if self.operational_capacity >= 3:
                producers = [a for a in self.model.schedule.agents if a.stakeholder_type == "producer"]
                for p in producers:
                    fine = p.threat_level * 1000 + (6 - p.operational_capacity) * 500
                    p.wealth_or_cost -= fine
                    p.fines_paid += fine
                    self.wealth_or_cost += fine * 0.1
                    logger.info(f"Regulator {self.unique_id} fined Producer {p.unique_id} by ${fine}")

        elif self.stakeholder_type == "producer":
            if self.threat_level > 1 and self.operational_capacity >= 2:
                self.threat_level = max(1, self.threat_level - 1)
                self.operational_capacity = min(5, self.operational_capacity + 1)
            
            users = [a for a in self.model.schedule.agents if a.stakeholder_type == "user"]
            comp_cost = 200 * self.threat_level
            for u in users:
                u.compensation_received += comp_cost
                self.wealth_or_cost -= comp_cost
                self.compensation_paid += comp_cost
            logger.info(f"Producer {self.unique_id} paid compensation/remediation costs totaling ${comp_cost * len(users)}")

        elif self.stakeholder_type == "user":
            producers = [a for a in self.model.schedule.agents if a.stakeholder_type == "producer"]
            for p in producers:
                damages = p.threat_level * 150
                self.wealth_or_cost += damages
                self.compensation_received += damages
            
            self.operational_capacity = min(5, self.operational_capacity + 1)
            self.regulatory_pressure = min(5, self.regulatory_pressure + 1)
            self.threat_level = max(1, self.threat_level - 1)
