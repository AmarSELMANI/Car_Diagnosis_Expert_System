# engine/inference_engine.py
import pandas as pd
import json


class ExpertSystem:
    def __init__(self, rules_file, questions_file):
        with open(rules_file, "r") as f:
            rules_data = json.load(f)
        self.rules = pd.DataFrame(rules_data)
        with open(questions_file, "r") as f:
            self.questions = json.load(f)
        self.facts = {}
        self.fired_rules = []  # Track which rules have fired and in what order
        self.reasoning_chain = {}  # Map facts to the rules that inferred them
        self.asked_questions = set()
        self.answers = []

    def add_initial_facts(self, user_inputs: dict):
        self.facts.update(user_inputs)
        # Mark initial facts as provided by user (not inferred)
        for key in user_inputs:
            self.reasoning_chain[key] = {"source": "user_input", "rule": None}

    def rule_conditions_met(self, conditions: dict) -> bool:
        for condition, value in conditions.items():
            # If the prerequisite value is a list, treat it as an OR (any match)
            if isinstance(value, (list, tuple)):
                if self.facts.get(condition) not in value:
                    return False
            else:
                if self.facts.get(condition) != value:
                    return False
        return True

    def run_inference(self):
        """
        Forward-chaining inference engine.
        Keeps firing rules until no new facts are inferred.
        Tracks rule firing order and reasoning chain.
        """
        new_fact_added = True
        while new_fact_added:
            new_fact_added = False
            for _, rule in self.rules.iterrows():
                rule_id = rule["id"]
                # Skip if this rule has already been fired
                if rule_id in [fr["rule_id"] for fr in self.fired_rules]:
                    continue
                
                conditions = rule["conditions"]
                conclusion = rule["conclusion"]
                
                if self.rule_conditions_met(conditions):
                    # Fire the rule
                    for key, value in conclusion.items():
                        if key not in self.facts:
                            self.facts[key] = value
                            # Track that this fact was inferred by this rule
                            self.reasoning_chain[key] = {
                                "source": "inferred",
                                "rule": rule_id,
                                "description": rule.get("description", "")
                            }
                            new_fact_added = True
                    
                    # Record the rule firing
                    self.fired_rules.append({
                        "rule_id": rule_id,
                        "description": rule.get("description", ""),
                        "inferred_facts": list(conclusion.keys())
                    })

    def get_results(self):
        """
        Returns:
        - diagnoses: list of problem diagnoses (should be 1 or 0)
        - fired_rules: list of fired rule IDs in order (e.g., ["R1", "R2"])
        - reasoning: list of reasoning strings showing the chain
        """
        diagnoses = []
        for key, value in self.facts.items():
            if key == "problem":
                diagnoses.append(value)
        
        # Build reasoning chain explanation
        reasoning = self._build_reasoning_explanation(diagnoses)
        
        return diagnoses, reasoning

    def _build_reasoning_explanation(self, diagnoses):
        """
        Build a human-readable reasoning chain.
        Shows: symptoms -> intermediate faults -> final problem
        """
        explanations = []
        
        if not self.fired_rules:
            return ["No rules were fired. The symptoms did not match any diagnostic patterns."]
        
        # Add rule firing sequence
        rule_sequence = " → ".join([fr["rule_id"] for fr in self.fired_rules])
        explanations.append(f"Rule sequence: {rule_sequence}")
        
        # Add detailed rule descriptions
        for fired_rule in self.fired_rules:
            rule_id = fired_rule["rule_id"]
            description = fired_rule["description"]
            inferred_facts = ", ".join(fired_rule["inferred_facts"])
            explanations.append(f"{rule_id}: {description} → {inferred_facts}")
        
        # Build symptom → fault → problem chain
        if diagnoses:
            chain_str = self._build_symptom_chain(diagnoses[0])
            if chain_str:
                explanations.append(f"\nDiagnosis chain:\n{chain_str}")
        
        return explanations

    def _build_symptom_chain(self, diagnosis):
        """
        Trace back from the diagnosis to show the symptom chain.
        Example: engine_does_not_crank + headlights_dim → battery_discharged → Battery Failure
        """
        # Find the problem rule (the one that concluded with the diagnosis)
        problem_rule_id = None
        for key, chain_info in self.reasoning_chain.items():
            if key == "problem" and self.facts.get(key) == diagnosis:
                problem_rule_id = chain_info.get("rule")
                break
        
        if not problem_rule_id:
            return ""
        
        # Trace backwards through the rule chain
        chain_parts = []
        
        # Get symptoms (user inputs)
        symptoms = []
        for key, chain_info in self.reasoning_chain.items():
            if chain_info.get("source") == "user_input" and self.facts.get(key) == True:
                symptoms.append(key)
        
        if symptoms:
            chain_parts.append(" + ".join(symptoms))
        
        # Get intermediate faults
        intermediate_faults = []
        for key, chain_info in self.reasoning_chain.items():
            if chain_info.get("source") == "inferred":
                rule_id = chain_info.get("rule")
                # Check if this is an intermediate fault (not the final problem)
                if rule_id and key != "problem" and self.facts.get(key) == True:
                    # Only include if it's used by another rule
                    used_in_rule = False
                    for fired_rule in self.fired_rules:
                        if fired_rule["rule_id"] != rule_id:
                            # Check if this fact is used as a condition
                            rule_data = self.rules[self.rules["id"] == fired_rule["rule_id"]]
                            if not rule_data.empty:
                                conditions = rule_data.iloc[0]["conditions"]
                                if key in conditions:
                                    used_in_rule = True
                                    break
                    if used_in_rule or key in intermediate_faults:
                        intermediate_faults.append(key)
        
        if intermediate_faults:
            chain_parts.extend(intermediate_faults)
        
        if chain_parts:
            chain_parts.append(diagnosis)
        
        return " → ".join(chain_parts)

    def get_next_question(self):
        for question in self.questions:
            if question["id"] in self.asked_questions:
                continue
            prerequisite = question.get("prerequisite", {})
            if self.rule_conditions_met(prerequisite):
                return question
        return None

    def mark_question_asked(self, question_id):
        self.asked_questions.add(question_id)


# ---------- helper used by the GUI ----------

def run_inference(facts: dict) -> dict:
    """
    Takes raw GUI facts and returns a dict:
    {
        'diagnosis': str,
        'reasoning': [str],
        'rules_fired': [str]
    }
    """
    system = ExpertSystem("engine/rules.json", "engine/questions.json")
    system.add_initial_facts(facts)
    system.run_inference()
    diagnoses, reasoning = system.get_results()

    # No diagnosis inferred -> return polite generic message
    if not diagnoses:
        return {
            "diagnosis": "No specific problem could be identified from the selected symptoms.",
            "reasoning": [
                "The current combination of symptoms did not match any diagnostic rule in the knowledge base.",
                "Please review the symptoms and try again, or consult a professional mechanic."
            ],
            "rules_fired": []
        }

    # At least one diagnosis found
    rules_fired = [fr["rule_id"] for fr in system.fired_rules]
    return {
        "diagnosis": diagnoses[0],
        "reasoning": reasoning,
        "rules_fired": rules_fired
    }
