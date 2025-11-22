from fastapi import FastAPI
from pydantic import BaseModel
from quantum_consensus_aggregator import aggregate_quantum_results
from models import InputEnvelope, OutputEnvelope, Request

app = FastAPI()

@app.post("/euystacio/input", response_model=OutputEnvelope)
async def receive_input(env: InputEnvelope, request: Request):
    # 1. INITIAL GATEWAY VALIDATION (Euystacio Helmi AI Role)
    if not env.is_valid_user_intent():
        return OutputEnvelope(status="REJECTED", message="Initial intent failed validation.", data={})

    # 2. COLLECTIVE EXECUTION (Simulated Placeholder)
    # The agent outputs are the results gathered from the 'Collective' agents.
    agent_outputs = [
        {"trust_index": 0.95, "status": "VALID", "resolution": "Path_A: Collaborate and Allocate Resources"},
        {"trust_index": 0.88, "status": "VALID", "resolution": "Path_A: Collaborate and Allocate Resources"},
        {"trust_index": 0.70, "status": "VALID", "resolution": "Path_B: Delayed Action Protocol"},
        {"trust_index": 0.00, "status": "INVALID", "resolution": "Path_C: Error/Corruption Detected"}
    ]

    try:
        # 3. CONSUS AGGREGATION PROTOCOL (CAP) 🤝
        final_consensus_data = aggregate_quantum_results(agent_outputs)

        # 4. AXIOMATIC ALIGNMENT CHECK (Performed within aggregate_quantum_results)
        # (Ensured by the aggregate function logic)

        # 5. FINAL REPORT CONSTRUCTION
        return OutputEnvelope(
            status=final_consensus_data['final_status'],
            message="Consus Achieved. Action Resolution Vetted.",
            data={
                "collective_resolution": final_consensus_data['consensus_resolution'],
                "collective_trust_level": final_consensus_data['collective_trust_level'],
                "axiomatic_alignment": final_consensus_data['axiomatic_alignment'],
                "initial_request_id": env.request_id
            }
        )

    except (RuntimeError, ValueError) as e:
        # Catches CAP Failure or Axiomatic Violation
        return OutputEnvelope(
            status="CRITICAL_HALT",
            message=f"Consensus Failure: {str(e)}",
            data={"request_id": env.request_id}
        )
