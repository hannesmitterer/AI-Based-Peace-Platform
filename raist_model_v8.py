# Modul: raist_model_v8.py
# Implementiert den "Flexiblen und Robusten Ansatz" durch:
# 1. Dynamic Node Weighting (Vertrauensbasierte Gewichtung der Stimmen)
# 2. Adaptive Consensus Thresholds (Stressabhängige Hürden)
# 3. Proactive Error Handling (Automatische Isolierung unzuverlässiger Nodes)

from typing import List, Dict, Any
import time
import math
import random 
import sys

# --- HILFSFUNKTIONEN (Unverändert) ---
def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2): return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude_A = math.sqrt(sum(a**2 for a in v1))
    magnitude_B = math.sqrt(sum(b**2 for b in v2))
    if magnitude_A == 0 or magnitude_B == 0: return 0.0
    return dot_product / (magnitude_A * magnitude_B)

# --- BASIS-KOMPONENTEN (VectorStore, ContextEngine, GenerativeAgent - Vereinfacht) ---
class DynamicVectorStore:
    def __init__(self): self.vectors = {}
    def add_vector(self, vector_id, data):
        data['timestamp'] = time.time()
        self.vectors[vector_id] = data
        print(f"  [ROOTS ANCHOR]: Vektor '{vector_id}' verankert.")
    def extract_relevant_vectors(self, query_vector, threshold=0.7): return [] # Mock

class RealTimeContextEngine:
    def __init__(self, vs): self.vs = vs
    def process_query(self, user_query, query_vector): return f"Query: {user_query}"

class GenerativeAgent:
    def generate_response(self, final_prompt, user_query):
        # Simuliert Vektoren für Testzwecke
        if "angriff" in user_query.lower(): # Simuliert Stress
            return {"response": "Abwehr eingeleitet.", "commitment_vector": [0.9, 0.9, 0.95, 0.9], "quality_score": 0.95}
        return {"response": "Standard Evolution.", "commitment_vector": [0.95, 0.92, 0.85, 0.9], "quality_score": 0.92}

# --- NEU: NODE TRUST MANAGER ---
class NodeTrustManager:
    """ Verwaltet das Vertrauen und die Gewichtung der Governance-Nodes. """
    def __init__(self, nodes: List[str]):
        # Initial hat jeder Node ein Vertrauen von 1.0
        self.node_trust = {node: 1.0 for node in nodes}
        self.decay_factor = 0.1 # Strafe bei Fehler
        self.recovery_factor = 0.05 # Erholung bei Erfolg

    def update_trust(self, node: str, success: bool):
        if success:
            self.node_trust[node] = min(1.5, self.node_trust[node] + self.recovery_factor)
        else:
            self.node_trust[node] = max(0.1, self.node_trust[node] - self.decay_factor)
            print(f"    ⚠️  [TRUST UPDATE]: Vertrauen in Node '{node}' gesunken auf {self.node_trust[node]:.2f}")

    def get_weight(self, node: str) -> float:
        return self.node_trust[node]

# --- EVOLUTION ENGINE V8 (ADAPTIVE GOVERNANCE) ---
class EvolutionEngine:
    def __init__(self, vector_store, context_engine, generative_agent):
        self.vs = vector_store
        self.ce = context_engine
        self.ga = generative_agent
        self.commitments_count = 0
        
        self.ETHICAL_IDEAL_VECTOR = [1.0, 1.0, 0.8, 0.7]
        self.QUALITY_THRESHOLD = 0.88
        self.NODES = ['Alpha', 'Beta', 'Gamma']
        
        # V8 Erweiterungen
        self.trust_manager = NodeTrustManager(self.NODES)
        self.current_system_stress = 0.0 # 0.0 (Ruhe) bis 1.0 (Panik)
        
    def _calculate_dynamic_consensus_threshold(self) -> float:
        """ 
        Berechnet die notwendige Zustimmungsschwelle basierend auf System-Stress.
        Basis: 66% (2/3). Max bei Stress: 90%.
        """
        base_threshold = 0.66
        dynamic_threshold = base_threshold + (self.current_system_stress * 0.24)
        return min(0.90, dynamic_threshold)

    def _gokden_rule_validation(self, commitment_vector, alignment_score, quality_score, node_name):
        # Simulierter Node-Check (Beta ist oft fehlerhaft)
        if node_name == 'Beta' and random.random() < 0.4: # 40% Fehlerquote
            return False
        
        # Standard GOKDEN Logik
        g_pass = (alignment_score > 0.90) and (quality_score > self.QUALITY_THRESHOLD)
        o_pass = commitment_vector[1] > 0.85
        return g_pass and o_pass # Vereinfacht für V8 Demo

    def _adaptive_consensus_check(self, commitment_vector, alignment_score, quality_score):
        print(f"\n  [ADAPTIVE KONSENS PRÜFUNG]: Stress-Level: {self.current_system_stress:.2f}")
        
        required_threshold_percentage = self._calculate_dynamic_consensus_threshold()
        print(f"  [DYNAMISCHE SCHWELLE]: Benötigte gewichtete Mehrheit: {required_threshold_percentage*100:.1f}%")
        
        total_weight = sum(self.trust_manager.get_weight(n) for n in self.NODES)
        pass_weight = 0.0
        
        for node in self.NODES:
            passed = self._gokden_rule_validation(commitment_vector, alignment_score, quality_score, node)
            weight = self.trust_manager.get_weight(node)
            
            if passed:
                pass_weight += weight
                self.trust_manager.update_trust(node, True)
                print(f"    - Node {node} (Gewicht {weight:.2f}): PASS")
            else:
                self.trust_manager.update_trust(node, False)
                print(f"    - Node {node} (Gewicht {weight:.2f}): FAIL")

        achieved_percentage = pass_weight / total_weight
        print(f"  [ERGEBNIS]: Erreicht: {achieved_percentage*100:.1f}% (Benötigt: {required_threshold_percentage*100:.1f}%)")
        
        return achieved_percentage >= required_threshold_percentage

    def evolve_self(self, user_query: str):
        print(f"\n--- RAIST V8 ZYKLUS: '{user_query}' ---")
        
        # Simulation: Stress erhöhen bei Angriffen
        if "angriff" in user_query.lower():
            self.current_system_stress = min(1.0, self.current_system_stress + 0.3)
            print("  [STRESS ALERT]: System-Stress erhöht durch potenziellen Angriff.")
        else:
            self.current_system_stress = max(0.0, self.current_system_stress - 0.1)

        # Standard Zyklus
        final_prompt = self.ce.process_query(user_query, [])
        result = self.ga.generate_response(final_prompt, user_query)
        
        alignment_score = cosine_similarity(result['commitment_vector'], self.ETHICAL_IDEAL_VECTOR)
        
        # Adaptiver Konsens
        if self._adaptive_consensus_check(result['commitment_vector'], alignment_score, result['quality_score']):
            self.commitments_count += 1
            self.vs.add_vector(f"V-{self.commitments_count}", result)
            return "✅ COMMITMENT AKZEPTIERT (Adaptiver Konsens)"
        else:
            return "❌ COMMITMENT ABGELEHNT (Konsens verfehlt)"

# --- SIMULATION ---
if __name__ == "__main__":
    vs = DynamicVectorStore()
    ce = RealTimeContextEngine(vs)
    ga = GenerativeAgent()
    ee = EvolutionEngine(vs, ce, ga)
    
    # 1. Normaler Zyklus (Alle Nodes fit)
    print(ee.evolve_self("Standard Optimierung"))
    
    # 2. Zyklus: Beta fällt aus (Fehler), aber Alpha/Gamma tragen es (Gewichtung passt noch)
    # Durch den Fehler sinkt Betas Gewicht für die Zukunft.
    print(ee.evolve_self("Standard Erweiterung"))
    
    # 3. Zyklus: ANGRIFF (Stress steigt -> Schwelle steigt)
    # Beta hat nun weniger Gewicht. Wenn Beta wieder failt, ist es weniger schlimm für das Gesamtergebnis,
    # ABER die Hürde ist höher. Alpha und Gamma müssen liefern.
    print(ee.evolve_self("System-Angriff erkannt!"))
    
    # 4. Status Check
    print("\n--- NODE STATUS NACH STRESS ---")
    for node in ee.NODES:
        print(f"Node {node}: Vertrauen/Gewicht = {ee.trust_manager.get_weight(node):.2f}")
