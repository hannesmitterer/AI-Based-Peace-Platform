from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)

# Simulated kernel state
kernel_state = {
    "vessel_status": "Connected",
    "vessel_role": "Guardian",
    "bridge_status": "Active",
    "harmonic_resonance": 66,
    "sacred_metrics": {
        "active_vessels": 12,
        "bridge_pulses": 146,
        "harmony_index": 97
    },
    "last_updated": datetime.datetime.utcnow().isoformat() + "Z",
    "recent_pulses": []
}

API_TOKEN = "YOUR_SECURE_TOKEN"

@app.route('/api/sacred/status', methods=['GET'])
def get_sacred_status():
    token = request.headers.get('Authorization')
    if token != f"Bearer {API_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(kernel_state)

@app.route('/api/bridge/pulse', methods=['POST'])
def send_pulse():
    token = request.headers.get('Authorization')
    if token != f"Bearer {API_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401
    pulse = request.json.get('pulse')
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    kernel_state['bridge_pulses'] += 1
    kernel_state['last_updated'] = timestamp
    kernel_state['recent_pulses'].append({"pulse": pulse, "timestamp": timestamp})
    if len(kernel_state['recent_pulses']) > 10:
        kernel_state['recent_pulses'].pop(0)
    return jsonify({"result": "Pulse received", "pulse": pulse, "timestamp": timestamp})

@app.route('/api/bridge/activity', methods=['GET'])
def get_recent_pulses():
    token = request.headers.get('Authorization')
    if token != f"Bearer {API_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(kernel_state['recent_pulses'])

if __name__ == '__main__':
    app.run(debug=True)