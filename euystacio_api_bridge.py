"""
Bridge module for integrating Euystacio kernel APIs with the AI-Based Peace Platform.
This file is additive and does NOT overwrite existing backend code.
"""

from flask import Blueprint, jsonify, request
import datetime
from euystacio_blacklist import (
    add_node_to_blacklist, add_entity_to_blacklist, add_pattern_to_blacklist,
    is_node_blocked, is_entity_blocked, check_input_against_blacklist,
    get_blacklist_status, remove_node_from_blacklist, remove_entity_from_blacklist,
    _permanent_blacklist
)

euystacio_bridge = Blueprint('euystacio_bridge', __name__)

# Simulated kernel state for demonstration; replace with real kernel integration.
euystacio_state = {
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

@euystacio_bridge.route('/api/sacred/status', methods=['GET'])
def get_sacred_status():
    return jsonify(euystacio_state)

@euystacio_bridge.route('/api/bridge/pulse', methods=['POST'])
def send_pulse():
    pulse = request.json.get('pulse')
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    euystacio_state['sacred_metrics']['bridge_pulses'] += 1
    euystacio_state['last_updated'] = timestamp
    euystacio_state['recent_pulses'].append({"pulse": pulse, "timestamp": timestamp})
    if len(euystacio_state['recent_pulses']) > 10:
        euystacio_state['recent_pulses'].pop(0)
    return jsonify({"result": "Pulse received", "pulse": pulse, "timestamp": timestamp})

@euystacio_bridge.route('/api/bridge/activity', methods=['GET'])
def get_recent_pulses():
    return jsonify(euystacio_state['recent_pulses'])

# Blacklist Management Endpoints

@euystacio_bridge.route('/api/blacklist/status', methods=['GET'])
def get_blacklist_status_endpoint():
    """Get comprehensive blacklist status"""
    try:
        status = get_blacklist_status()
        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@euystacio_bridge.route('/api/blacklist/node/add', methods=['POST'])
def add_node_endpoint():
    """Add node to permanent blacklist"""
    try:
        data = request.json
        node_id = data.get('node_id')
        reason = data.get('reason', 'Suspicious activity detected')
        severity = data.get('severity', 'high')
        metadata = data.get('metadata', {})
        
        if not node_id:
            return jsonify({
                "success": False,
                "error": "node_id is required"
            }), 400
        
        result = add_node_to_blacklist(node_id, reason, severity, metadata)
        
        return jsonify({
            "success": result,
            "message": f"Node {node_id} added to blacklist",
            "data": {
                "node_id": node_id,
                "reason": reason,
                "severity": severity
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@euystacio_bridge.route('/api/blacklist/entity/add', methods=['POST'])
def add_entity_endpoint():
    """Add entity to permanent blacklist"""
    try:
        data = request.json
        entity_id = data.get('entity_id')
        reason = data.get('reason', 'Suspicious activity detected')
        severity = data.get('severity', 'high')
        metadata = data.get('metadata', {})
        
        if not entity_id:
            return jsonify({
                "success": False,
                "error": "entity_id is required"
            }), 400
        
        result = add_entity_to_blacklist(entity_id, reason, severity, metadata)
        
        return jsonify({
            "success": result,
            "message": f"Entity {entity_id} added to blacklist",
            "data": {
                "entity_id": entity_id,
                "reason": reason,
                "severity": severity
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@euystacio_bridge.route('/api/blacklist/pattern/add', methods=['POST'])
def add_pattern_endpoint():
    """Add suspicious pattern to permanent blacklist"""
    try:
        data = request.json
        pattern = data.get('pattern')
        reason = data.get('reason', 'Malicious pattern detected')
        severity = data.get('severity', 'medium')
        metadata = data.get('metadata', {})
        
        if not pattern:
            return jsonify({
                "success": False,
                "error": "pattern is required"
            }), 400
        
        result = add_pattern_to_blacklist(pattern, reason, severity, metadata)
        
        return jsonify({
            "success": result,
            "message": "Pattern added to blacklist",
            "data": {
                "pattern": pattern,
                "reason": reason,
                "severity": severity
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@euystacio_bridge.route('/api/blacklist/check', methods=['POST'])
def check_blacklist_endpoint():
    """Check if input is blocked by blacklist"""
    try:
        data = request.json
        check_result = check_input_against_blacklist(data)
        
        return jsonify({
            "success": True,
            "blocked": check_result['blocked'],
            "reasons": check_result['reasons'],
            "severity": check_result['severity']
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@euystacio_bridge.route('/api/blacklist/node/check/<node_id>', methods=['GET'])
def check_node_endpoint(node_id):
    """Check if specific node is blacklisted"""
    try:
        blocked = is_node_blocked(node_id)
        return jsonify({
            "success": True,
            "node_id": node_id,
            "blocked": blocked
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@euystacio_bridge.route('/api/blacklist/entity/check/<entity_id>', methods=['GET'])
def check_entity_endpoint(entity_id):
    """Check if specific entity is blacklisted"""
    try:
        blocked = is_entity_blocked(entity_id)
        return jsonify({
            "success": True,
            "entity_id": entity_id,
            "blocked": blocked
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@euystacio_bridge.route('/api/blacklist/nodes', methods=['GET'])
def get_blocked_nodes_endpoint():
    """Get list of all blocked nodes"""
    try:
        include_removed = request.args.get('include_removed', 'false').lower() == 'true'
        nodes = _permanent_blacklist.get_blocked_nodes(include_removed)
        
        return jsonify({
            "success": True,
            "count": len(nodes),
            "nodes": nodes
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@euystacio_bridge.route('/api/blacklist/entities', methods=['GET'])
def get_blocked_entities_endpoint():
    """Get list of all blocked entities"""
    try:
        include_removed = request.args.get('include_removed', 'false').lower() == 'true'
        entities = _permanent_blacklist.get_blocked_entities(include_removed)
        
        return jsonify({
            "success": True,
            "count": len(entities),
            "entities": entities
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@euystacio_bridge.route('/api/blacklist/node/remove', methods=['POST'])
def remove_node_endpoint():
    """Remove node from blacklist (requires authorization)"""
    try:
        data = request.json
        node_id = data.get('node_id')
        authorized_by = data.get('authorized_by', 'api_user')
        
        if not node_id:
            return jsonify({
                "success": False,
                "error": "node_id is required"
            }), 400
        
        result = remove_node_from_blacklist(node_id, authorized_by)
        
        if result:
            return jsonify({
                "success": True,
                "message": f"Node {node_id} removed from blacklist",
                "data": {
                    "node_id": node_id,
                    "authorized_by": authorized_by
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Node {node_id} not found in blacklist"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@euystacio_bridge.route('/api/blacklist/entity/remove', methods=['POST'])
def remove_entity_endpoint():
    """Remove entity from blacklist (requires authorization)"""
    try:
        data = request.json
        entity_id = data.get('entity_id')
        authorized_by = data.get('authorized_by', 'api_user')
        
        if not entity_id:
            return jsonify({
                "success": False,
                "error": "entity_id is required"
            }), 400
        
        result = remove_entity_from_blacklist(entity_id, authorized_by)
        
        if result:
            return jsonify({
                "success": True,
                "message": f"Entity {entity_id} removed from blacklist",
                "data": {
                    "entity_id": entity_id,
                    "authorized_by": authorized_by
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Entity {entity_id} not found in blacklist"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

