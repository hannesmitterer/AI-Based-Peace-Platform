"""
Lex Amoris API
Flask API endpoints for Lex Amoris Security Platform.

SECURITY WARNING: This API lacks authentication and authorization.
Before deploying to production, implement proper security:
- API key authentication or JWT tokens
- Role-based access control (RBAC)
- Rate limiting per authenticated user
- Audit logging of all operations
See documentation for security implementation guide.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime

from lex_amoris_integration import get_platform

app = Flask(__name__)

# Configure CORS origins - make this environment-configurable for production
allowed_origins_env = os.getenv("LEX_AMORIS_ALLOWED_ORIGINS")
if allowed_origins_env:
    cors_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    # Default origins for development
    cors_origins = ["https://hannesmitterer.github.io", "http://localhost:3000"]

# In production, filter out localhost origins
app_env = os.getenv("LEX_AMORIS_ENV", os.getenv("FLASK_ENV", "production")).lower()
if app_env == "production":
    # Remove localhost origins in production
    cors_origins = [
        origin for origin in cors_origins
        if not origin.startswith("http://localhost") and not origin.startswith("https://localhost")
    ]
    logging.info(f"Production mode: CORS origins set to {cors_origins}")

CORS(app, origins=cors_origins)


@app.route('/api/lex-amoris/status', methods=['GET'])
def get_platform_status():
    """Get comprehensive platform status"""
    try:
        platform = get_platform()
        status = platform.get_platform_status()
        return jsonify(status), 200
    except Exception as e:
        # Log full error details server-side
        logging.error(f"Error getting platform status: {str(e)}", exc_info=True)
        # Return generic error to client
        return jsonify({
            "error": "Internal server error",
            "message": "Failed to retrieve platform status"
        }), 500


@app.route('/api/lex-amoris/process', methods=['POST'])
def process_request():
    """
    Process a request through Lex Amoris security platform.
    
    Body:
    {
        "data": {...},  // Request data to validate
        "origin_ip": "1.2.3.4",  // Optional
        "sender_id": "user-123"  // Optional
    }
    """
    try:
        body = request.get_json()
        if not body or 'data' not in body:
            return jsonify({"error": "Missing 'data' field"}), 400
        
        platform = get_platform()
        result = platform.process_request(
            request_data=body['data'],
            origin_ip=body.get('origin_ip'),
            sender_id=body.get('sender_id')
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/lex-amoris/rhythm/validate', methods=['POST'])
def validate_rhythm():
    """
    Validate packet rhythm directly.
    
    Body:
    {
        "packet_data": {...},
        "origin_ip": "1.2.3.4"  // Optional
    }
    """
    try:
        body = request.get_json()
        if not body or 'packet_data' not in body:
            return jsonify({"error": "Missing 'packet_data' field"}), 400
        
        platform = get_platform()
        result = platform.rhythm_validator.validate_packet(
            packet_data=body['packet_data'],
            origin_ip=body.get('origin_ip')
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/lex-amoris/rhythm/blacklist', methods=['GET'])
def get_blacklist():
    """Get current blacklist status"""
    try:
        platform = get_platform()
        status = platform.rhythm_validator.get_blacklist_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/lex-amoris/rhythm/blacklist/clear', methods=['POST'])
def clear_blacklist():
    """Clear blacklist (admin operation)"""
    try:
        platform = get_platform()
        result = platform.rhythm_validator.clear_blacklist()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/lex-amoris/security/status', methods=['GET'])
def get_security_status():
    """Get lazy security status"""
    try:
        platform = get_platform()
        status = platform.lazy_security.get_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/lex-amoris/security/scan', methods=['POST'])
def trigger_security_scan():
    """Trigger environmental security scan"""
    try:
        platform = get_platform()
        result = platform.lazy_security.update_security_state()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/lex-amoris/backup/status', methods=['GET'])
def get_backup_status():
    """Get IPFS backup status"""
    try:
        platform = get_platform()
        status = platform.ipfs_backup.get_backup_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/lex-amoris/backup/create', methods=['POST'])
def create_backup():
    """Create backup snapshot"""
    try:
        platform = get_platform()
        result = platform.create_backup_snapshot()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/lex-amoris/backup/list', methods=['GET'])
def list_backups():
    """
    List backups.
    
    Query params:
    - type: Filter by backup type (optional)
    - limit: Max results (default 50, range 1-1000)
    """
    try:
        backup_type = request.args.get('type')
        limit_param = request.args.get('limit', '50')
        
        # Validate limit parameter
        try:
            limit = int(limit_param)
        except ValueError:
            return jsonify({
                "error": "Invalid 'limit' parameter",
                "message": "The 'limit' parameter must be an integer between 1 and 1000"
            }), 400
        
        if limit < 1 or limit > 1000:
            return jsonify({
                "error": "Parameter out of range",
                "message": "The 'limit' parameter must be between 1 and 1000"
            }), 400
        
        platform = get_platform()
        backups = platform.ipfs_backup.list_backups(
            backup_type=backup_type,
            limit=limit
        )
        
        return jsonify({
            "backups": backups,
            "count": len(backups)
        }), 200
    except Exception as e:
        logging.error(f"Error listing backups: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": "Failed to list backups"
        }), 500


@app.route('/api/lex-amoris/rescue/request', methods=['POST'])
def request_rescue():
    """
    Request rescue/unblock for a blocked node.
    
    Body:
    {
        "sender_id": "user-123",
        "node_id": "node-456",
        "reason": "False positive detection",
        "evidence": {...},
        "priority": "NORMAL"  // LOW, NORMAL, HIGH, CRITICAL
    }
    """
    try:
        body = request.get_json()
        
        required_fields = ['sender_id', 'node_id', 'reason', 'evidence']
        for field in required_fields:
            if field not in body:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        platform = get_platform()
        result = platform.request_rescue(
            sender_id=body['sender_id'],
            node_id=body['node_id'],
            reason=body['reason'],
            evidence=body['evidence'],
            priority=body.get('priority', 'NORMAL')
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/lex-amoris/rescue/status', methods=['GET'])
def get_rescue_status():
    """Get rescue channel status"""
    try:
        platform = get_platform()
        status = platform.rescue_channel.get_rescue_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/lex-amoris/endpoints', methods=['GET'])
def list_endpoints():
    """List all Lex Amoris API endpoints"""
    rules = []
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith("/api/lex-amoris"):
            rules.append({
                "endpoint": rule.rule,
                "methods": list(rule.methods - {'HEAD', 'OPTIONS'})
            })
    return jsonify(sorted(rules, key=lambda x: x["endpoint"]))


@app.route('/api/lex-amoris/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "platform": "Lex Amoris Security Platform",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
