"""
Stakeholder Agents for Cybersecurity Regulatory Compliance ABM
==============================================================
Defines the `StakeholderAgent` class representing Regulators, Software Producers,
and Users. Implements a human-auditable 5-stage lifecycle calibrated from empirical
cybersecurity incident cases:
  1. Context     (T=0 environmental baseline)
  2. Operating   (Steady-state activities: deploying, securing, complying, rulemaking, etc.)
  3. Precursors  (Vulnerability accumulation: business changes, compliance gaps, unaddressed weaknesses)
  4. Recovering  (Post-incident response: posturing, compensating, correcting, complying)
  5. Outcomes    (Terminal evaluation: costs, transformations, remedies, preservation)

All qualitative attributes are mapped to a bounded 1 to 5 integer scale:
  1 = Very Low / Passive / Weak / Lenient / Unfavorable
  2 = Low / Somewhat Passive / Somewhat Weak / Somewhat Lenient / Somewhat Unfavorable
  3 = Neutral / Neither Low Nor High / Moderate
  4 = High / Somewhat Active / Somewhat Strong / Somewhat Strict / Somewhat Favorable
  5 = Very High / Active / Strong / Strict / Favorable / Risky / Challenging
"""

import logging
import random
from mesa import Agent

logger = logging.getLogger("CyberComplianceModel")


def clamp(val, min_val=1, max_val=5):
    """Clamps an integer value to the 1-5 scale."""
    return max(min_val, min(max_val, int(round(val))))


class StakeholderAgent(Agent):
    """
    Agent representing a stakeholder in the cybersecurity compliance ecosystem.

    Stakeholder Types:
      - 'regulator': Government agencies, sector-specific overseers, or self-regulatory bodies.
      - 'producer': Software and technology vendors responsible for system security.
      - 'user': Enterprise clients, IT administrators, or individual end-users.
    """

    def __init__(self, unique_id, model, stakeholder_type, sub_type=None, empirical_profile=None):
        super().__init__(unique_id, model)
        self.stakeholder_type = stakeholder_type
        self.sub_type = sub_type or "standard"
        self.profile = empirical_profile or {}

        # -------------------------------------------------------------
        # 1. CORE SYSTEM PROPERTIES (Bounded 1 to 5)
        # -------------------------------------------------------------
        # Extracted from Stage 1: Context
        ctx = self.profile.get("Context", {})
        self.env_regulatory = ctx.get("Regulatory Environment", 3)
        self.env_threat = ctx.get("Threat Environment", 3)
        self.env_operational = ctx.get("Operational Environment", 3)

        # Baseline mappings to core properties:
        # - Operational Capacity initialized from Operational Environment
        # - Regulatory Pressure initialized from Regulatory Environment
        # - Threat Level initialized from Threat Environment
        self.operational_capacity = clamp(self.env_operational)
        self.regulatory_pressure = clamp(self.env_regulatory)
        self.threat_level = clamp(self.env_threat)

        # -------------------------------------------------------------
        # 2. STAGE 2: OPERATING PROPERTIES (Bounded 1 to 5)
        # -------------------------------------------------------------
        op = self.profile.get("Operating", {})
        if self.stakeholder_type == "regulator":
            self.op_rulemaking = op.get("Rulemaking", 3)
            self.op_enforcement = op.get("Enforcement", 3)
            self.op_investigation = op.get("Investigation", 3)
            self.op_influencing = op.get("Influencing", 3)
        elif self.stakeholder_type == "producer":
            self.op_implementing = op.get("Implementing", 3)
            self.op_securing = op.get("Securing", 3)
            self.op_influencing = op.get("Influencing", 3)
            self.op_complying = op.get("Complying", 3)
        elif self.stakeholder_type == "user":
            self.op_deploying = op.get("Deploying", 3)
            self.op_securing = op.get("Securing", 3)
            self.op_influencing = op.get("Influencing", 3)
            self.op_complying = op.get("Complying", 3)

        # -------------------------------------------------------------
        # 3. STAGE 3: PRECURSORS PROPERTIES (Bounded 1 to 5)
        # -------------------------------------------------------------
        prec = self.profile.get("Precursors", {})
        self.precursor_capacity = prec.get("Capacity", 3)
        self.precursor_business_change = prec.get("Business Change", 3)
        self.precursor_compliance = prec.get("Compliance", prec.get("Regimes", 3))
        self.precursor_failures = prec.get("Unaddressed Failures & Weaknesses", 3)

        # -------------------------------------------------------------
        # 4. STAGE 4: RECOVERING PROPERTIES (Bounded 1 to 5)
        # -------------------------------------------------------------
        rec = self.profile.get("Recovering", {})
        self.rec_posturing = rec.get("Posturing", 3)
        self.rec_compensating = rec.get("Compensating", 3)
        self.rec_correcting = rec.get("Correcting", rec.get("Correcting/Enforcing", 3))
        self.rec_complying = rec.get("Complying", 3)

        # -------------------------------------------------------------
        # 5. STAGE 5: OUTCOMES PROPERTIES (Bounded 1 to 5)
        # -------------------------------------------------------------
        outc = self.profile.get("Outcomes", {})
        self.out_costs = outc.get("Costs", 3)
        self.out_transformations = outc.get("Transformations", 3)
        self.out_remedies = outc.get("Remedies", 3)
        self.out_preservation = outc.get("Preservation", 3)

        # -------------------------------------------------------------
        # FINANCIAL & ENFORCEMENT LEDGER (Monetary Dollars)
        # -------------------------------------------------------------
        self.wealth_or_cost = 0.0
        self.fines_paid = 0.0
        self.compensation_paid = 0.0
        self.compensation_received = 0.0

    # =================================================================
    # STEP DISPATCHER ACROSS THE 5 STAGES
    # =================================================================
    def step(self):
        """Dispatches behavior based on the model's active lifecycle stage."""
        stage = self.model.current_stage

        if stage == "Operating":
            self.step_operating()
        elif stage == "Precursors":
            self.step_precursors()
        elif stage == "Recovering":
            self.step_recovering()
        elif stage == "Outcomes":
            self.step_outcomes()

        # Enforce bounds [1, 5] on core metrics after stage execution
        self.operational_capacity = clamp(self.operational_capacity)
        self.regulatory_pressure = clamp(self.regulatory_pressure)
        self.threat_level = clamp(self.threat_level)

    # -----------------------------------------------------------------
    # STAGE 2: OPERATING (Normal Steady-State Interactions)
    # -----------------------------------------------------------------
    def step_operating(self):
        """
        Executes steady-state operations:
        - Regulators conduct routine rulemaking, investigations, and enforcement signaling.
        - Producers balance software feature delivery (implementing) with security hardening.
        - Users deploy software, practice cyber hygiene, and voice feedback.
        """
        neighbors = self.model.grid.get_cell_list_contents([self.pos])

        if self.stakeholder_type == "regulator":
            # Rulemaking and Investigation response to ecosystem threat
            avg_threat = self.model.get_average_threat()
            if avg_threat >= 3 and self.op_investigation >= 3:
                self.regulatory_pressure = clamp(self.regulatory_pressure + 1)
            elif self.op_enforcement <= 2 and random.random() < 0.25:
                # Weak enforcement dilutes perceived regulatory pressure
                self.regulatory_pressure = clamp(self.regulatory_pressure - 1)

            # Stakeholder influence through neighbor interactions
            for n in neighbors:
                if n.stakeholder_type == "user" and n.op_influencing >= 4:
                    self.regulatory_pressure = clamp(self.regulatory_pressure + 1)
                elif n.stakeholder_type == "producer" and n.op_influencing >= 4:
                    # Producer lobbying softens regulatory pressure
                    if random.random() < 0.35:
                        self.regulatory_pressure = clamp(self.regulatory_pressure - 1)

        elif self.stakeholder_type == "producer":
            # Feature implementation velocity vs security investment
            if self.op_implementing > self.op_securing:
                # Security debt accumulates slightly
                if random.random() < 0.3:
                    self.threat_level = clamp(self.threat_level + 1)
            elif self.op_securing >= 4 and random.random() < 0.3:
                # High security diligence stabilizes or reduces threat
                self.threat_level = clamp(self.threat_level - 1)

            # Regulatory pressure creates operational compliance friction
            if self.regulatory_pressure >= 4:
                if random.random() < 0.3:
                    self.operational_capacity = clamp(self.operational_capacity - 1)
            else:
                if self.operational_capacity < 5 and random.random() < 0.3:
                    self.operational_capacity = clamp(self.operational_capacity + 1)

        elif self.stakeholder_type == "user":
            # User security hygiene protects against background threats
            if self.op_securing <= 2 and random.random() < 0.3:
                self.threat_level = clamp(self.threat_level + 1)
            elif self.op_securing >= 4 and random.random() < 0.3:
                self.threat_level = clamp(self.threat_level - 1)

    # -----------------------------------------------------------------
    # STAGE 3: PRECURSORS (Vulnerability Window & Destabilization)
    # -----------------------------------------------------------------
    def step_precursors(self):
        """
        Models the accumulation of latent risk before an incident:
        - Rapid business change (M&A, scaling, legacy migrations) strains operational capacity.
        - Unaddressed vulnerabilities build up threat surface.
        - Regulatory regimes may fail to catch emerging gaps if regulator capacity is weak.
        """
        if self.stakeholder_type == "producer":
            # High business change creates integration friction and drains capacity
            if self.precursor_business_change >= 4:
                if random.random() < 0.4:
                    self.operational_capacity = clamp(self.operational_capacity - 1)

            # Unaddressed failures compound threat level
            if self.precursor_failures >= 4:
                self.threat_level = clamp(self.threat_level + 1)
            elif self.precursor_compliance <= 2:
                # Lax compliance practices expose vulnerabilities
                if random.random() < 0.4:
                    self.threat_level = clamp(self.threat_level + 1)

        elif self.stakeholder_type == "regulator":
            # If regulator capacity is weak, enforcement lapses prior to breach
            if self.precursor_capacity <= 2:
                self.regulatory_pressure = clamp(self.regulatory_pressure - 1)
            elif self.precursor_capacity >= 4:
                # Vigilant regulators maintain strict oversight
                self.regulatory_pressure = clamp(self.regulatory_pressure + 1)

        elif self.stakeholder_type == "user":
            # Users with high dependency and low capacity become more vulnerable
            if self.precursor_business_change >= 4 and self.precursor_capacity <= 2:
                if random.random() < 0.3:
                    self.threat_level = clamp(self.threat_level + 1)

    # -----------------------------------------------------------------
    # STAGE 4: RECOVERING (Post-Incident Response & Enforcement)
    # -----------------------------------------------------------------
    def step_recovering(self):
        """
        Models post-incident stakeholder response:
        - Posturing: Public PR, testimony, outrage, and legal positioning.
        - Correcting: Consent decrees, contract cancellations, emergency patches.
        - Compensating: Monetary fines, restitution, and credit monitoring.
        - Complying: Submitting to mandatory audits and oversight.
        """
        if not self.model.incident_occurred:
            return

        if self.stakeholder_type == "regulator":
            # Enforcement & Correction: Regulators levy fines and impose corrective orders
            if self.rec_correcting >= 3 and self.operational_capacity >= 2:
                producers = [a for a in self.model.schedule.agents if a.stakeholder_type == "producer"]
                for p in producers:
                    # Fine formula calibrated to threat level, regulator enforcement, and producer capacity gap
                    fine = (p.threat_level * 1000 * self.rec_compensating // 3) + ((6 - p.operational_capacity) * 500)
                    p.wealth_or_cost -= fine
                    p.fines_paid += fine
                    self.wealth_or_cost += fine * 0.1
                    logger.info("Regulator %s levied fine of $%d on Producer %s", self.unique_id, fine, p.unique_id)

            # Public posturing elevates regulatory scrutiny across the sector
            if self.rec_posturing >= 4:
                self.regulatory_pressure = clamp(self.regulatory_pressure + 1)

        elif self.stakeholder_type == "producer":
            # Correcting actions: emergency remediation, security refactoring
            if self.rec_correcting >= 3:
                self.threat_level = clamp(self.threat_level - 1)
                self.operational_capacity = clamp(self.operational_capacity + 1)

            # Compensating actions: restitution, credit monitoring to users
            if self.rec_compensating >= 3:
                users = [a for a in self.model.schedule.agents if a.stakeholder_type == "user"]
                comp_per_user = 200 * self.threat_level
                total_comp = comp_per_user * len(users)
                self.wealth_or_cost -= total_comp
                self.compensation_paid += total_comp
                for u in users:
                    u.compensation_received += comp_per_user
                    u.wealth_or_cost += comp_per_user

        elif self.stakeholder_type == "user":
            # User posturing & litigation seeking damages
            if self.rec_posturing >= 4:
                self.regulatory_pressure = clamp(self.regulatory_pressure + 1)
            if self.rec_correcting >= 3:
                # Switching vendors or adopting privacy protections reduces user threat
                self.threat_level = clamp(self.threat_level - 1)

    # -----------------------------------------------------------------
    # STAGE 5: OUTCOMES (Systemic Equilibrium & Long-Term Legacy)
    # -----------------------------------------------------------------
    def update_dynamic_outcomes(self):
        """
        Dynamically computes the 4 terminal outcome dimension scores (1-5 scale)
        based on the agent's emergent simulation trajectory rather than static presets:
          - Costs: Economic/financial burden (1 = severe loss, 5 = favorable/minimal cost)
          - Transformations: Depth of structural reform / operational change (1 = static, 5 = major transformation)
          - Remedies: Regulatory compliance / user redress / restitution fulfillment (1 = unresolved, 5 = full redress)
          - Preservation: Retention of operational capacity and institutional viability (1 = compromised, 5 = intact)
        """
        if self.stakeholder_type == "producer":
            # 1. Costs: 1 = severe financial burden, 5 = minimal/favorable cost
            net_burden = -self.wealth_or_cost
            if net_burden >= 50000:
                self.out_costs = 1
            elif net_burden >= 30000:
                self.out_costs = 2
            elif net_burden >= 15000:
                self.out_costs = 3
            elif net_burden >= 5000:
                self.out_costs = 4
            else:
                self.out_costs = 5

            # 2. Transformations: Threat reduction and capacity improvement from breach peak
            threat_reduction = max(0, 5 - self.threat_level)
            self.out_transformations = clamp(1 + threat_reduction)

            # 3. Remedies: Consent order compliance and user restitution
            remedy_score = 1
            if self.rec_correcting >= 4:
                remedy_score += 1
            if self.threat_level <= 2:
                remedy_score += 1
            if self.compensation_paid > 0:
                remedy_score += 1
            if self.operational_capacity >= 4:
                remedy_score += 1
            self.out_remedies = clamp(remedy_score)

            # 4. Preservation: Operational survival and stability
            self.out_preservation = clamp(self.operational_capacity)

        elif self.stakeholder_type == "regulator":
            # 1. Costs: Regulatory cost recovery from fines collected
            if self.wealth_or_cost >= 5000:
                self.out_costs = 5
            elif self.wealth_or_cost >= 2000:
                self.out_costs = 4
            elif self.wealth_or_cost > 0:
                self.out_costs = 3
            else:
                self.out_costs = 2

            # 2. Transformations: Institutional regulatory evolution
            self.out_transformations = clamp(self.regulatory_pressure - (1 if self.operational_capacity <= 2 else 0))

            # 3. Remedies: Stringency of corrective enforcement mandates imposed
            self.out_remedies = clamp(self.rec_correcting)

            # 4. Preservation: Retention of regulatory authority and capacity
            self.out_preservation = clamp(self.operational_capacity)

        elif self.stakeholder_type == "user":
            # 1. Costs: User residual harm vs. restitution received
            if self.compensation_received >= 1000:
                self.out_costs = 4
            elif self.compensation_received > 0:
                self.out_costs = 3
            elif self.threat_level <= 2:
                self.out_costs = 2
            else:
                self.out_costs = 1

            # 2. Transformations: User security hardening and alternative adoption
            self.out_transformations = clamp(self.op_securing - (1 if self.threat_level >= 4 else 0))

            # 3. Remedies: Redress achieved through litigation or vendor remediation
            user_remedy = 1
            if self.threat_level <= 2:
                user_remedy += 2
            if self.compensation_received > 0:
                user_remedy += 2
            self.out_remedies = clamp(user_remedy)

            # 4. Preservation: Retention of client operations and user viability
            self.out_preservation = clamp(self.operational_capacity)

    def step_outcomes(self):
        """
        Models long-term structural outcomes:
        - Producer completes residual security hardening and capacity stabilization.
        - Regulators institutionalize post-enforcement oversight.
        - Users adapt to post-incident security baselines.
        - Dynamically computes terminal outcome dimension scores from emergent simulation history.
        """
        if self.stakeholder_type == "producer":
            if self.rec_correcting >= 3:
                self.threat_level = clamp(self.threat_level - 1)
            if self.rec_complying >= 4:
                self.operational_capacity = clamp(self.operational_capacity + 1)

        elif self.stakeholder_type == "regulator":
            if self.rec_correcting >= 4:
                self.regulatory_pressure = clamp(self.regulatory_pressure + 1)

        elif self.stakeholder_type == "user":
            if self.rec_correcting >= 3:
                self.threat_level = clamp(self.threat_level - 1)

        # Update dynamic outcome scores based on actual emergent simulation state
        self.update_dynamic_outcomes()
