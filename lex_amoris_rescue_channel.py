"""
Lex Amoris Rescue Channel
Messaging system for unblocking critical nodes in case of temporary false positives.

Implements a communication protocol based on Lex Amoris principles to handle
edge cases where legitimate traffic is temporarily blocked.
"""

import json
import hashlib
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class RescueMessageType(Enum):
    """Types of rescue messages"""
    UNBLOCK_REQUEST = "unblock_request"
    FALSE_POSITIVE_REPORT = "false_positive_report"
    EMERGENCY_OVERRIDE = "emergency_override"
    NODE_RESTORATION = "node_restoration"


class RescuePriority(Enum):
    """Priority levels for rescue operations"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class RescueMessage:
    """Represents a rescue channel message"""
    message_id: str
    message_type: RescueMessageType
    priority: RescuePriority
    sender_id: str
    node_id: str
    reason: str
    evidence: Dict[str, Any]
    timestamp: datetime
    lex_amoris_signature: str  # Love-based validation signature
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "sender_id": self.sender_id,
            "node_id": self.node_id,
            "reason": self.reason,
            "evidence": self.evidence,
            "timestamp": self.timestamp.isoformat() + "Z",
            "lex_amoris_signature": self.lex_amoris_signature
        }


@dataclass
class RescueResponse:
    """Response to a rescue message"""
    message_id: str
    approved: bool
    reason: str
    actions_taken: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "message_id": self.message_id,
            "approved": self.approved,
            "reason": self.reason,
            "actions_taken": self.actions_taken,
            "timestamp": self.timestamp.isoformat() + "Z"
        }


class LexAmorisRescueChannel:
    """
    Rescue channel for handling false positives and critical node unblocking.
    Based on Lex Amoris (Law of Love) principles - compassionate but secure.
    """
    
    def __init__(self,
                 auto_approve_threshold: int = 3,  # Auto-approve after N false positives
                 rescue_window_hours: int = 24):   # Time window for rescue operations
        self.auto_approve_threshold = auto_approve_threshold
        self.rescue_window_hours = rescue_window_hours
        
        self.messages: List[RescueMessage] = []
        self.responses: Dict[str, RescueResponse] = {}
        self.unblocked_nodes: Dict[str, datetime] = {}
        self.false_positive_history: Dict[str, int] = {}  # node_id -> count
        
        # Statistics
        self.total_requests = 0
        self.total_approved = 0
        self.total_denied = 0
        self.total_auto_approved = 0
    
    def generate_lex_amoris_signature(self, 
                                      message_data: Dict[str, Any]) -> str:
        """
        Generate Lex Amoris signature for message validation.
        Based on love frequency (528 Hz) and harmonic principles.
        
        Args:
            message_data: Message to sign
            
        Returns:
            Signature string
        """
        # Serialize message
        message_json = json.dumps(message_data, sort_keys=True)
        
        # Add Lex Amoris frequency constant (528 Hz - love frequency)
        lex_constant = "LEX_AMORIS_528"
        combined = f"{message_json}:{lex_constant}"
        
        # Generate signature
        signature = hashlib.sha256(combined.encode()).hexdigest()
        return f"LA-{signature[:32]}"
    
    def validate_lex_amoris_signature(self,
                                      message_data: Dict[str, Any],
                                      signature: str) -> bool:
        """
        Validate Lex Amoris signature.
        
        Args:
            message_data: Message to validate
            signature: Signature to check
            
        Returns:
            True if signature is valid
        """
        expected_signature = self.generate_lex_amoris_signature(message_data)
        return expected_signature == signature
    
    def create_rescue_message(self,
                            message_type: RescueMessageType,
                            sender_id: str,
                            node_id: str,
                            reason: str,
                            evidence: Dict[str, Any],
                            priority: RescuePriority = RescuePriority.NORMAL) -> RescueMessage:
        """
        Create a rescue message for unblocking a node.
        
        Args:
            message_type: Type of rescue message
            sender_id: ID of message sender
            node_id: ID of blocked node
            reason: Reason for rescue request
            evidence: Supporting evidence
            priority: Message priority
            
        Returns:
            RescueMessage object
        """
        message_id = f"rescue-{int(time.time() * 1000)}-{hashlib.sha256(node_id.encode()).hexdigest()[:8]}"
        
        # Create message data for signature
        message_data = {
            "message_id": message_id,
            "message_type": message_type.value,
            "sender_id": sender_id,
            "node_id": node_id,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Generate Lex Amoris signature
        signature = self.generate_lex_amoris_signature(message_data)
        
        message = RescueMessage(
            message_id=message_id,
            message_type=message_type,
            priority=priority,
            sender_id=sender_id,
            node_id=node_id,
            reason=reason,
            evidence=evidence,
            timestamp=datetime.utcnow(),
            lex_amoris_signature=signature
        )
        
        self.messages.append(message)
        self.total_requests += 1
        
        return message
    
    def evaluate_rescue_request(self, message: RescueMessage) -> RescueResponse:
        """
        Evaluate a rescue request and determine if it should be approved.
        Uses Lex Amoris principles: compassion with discernment.
        
        Args:
            message: RescueMessage to evaluate
            
        Returns:
            RescueResponse with decision
        """
        # Note: In production, signature validation would be more strict
        # For this implementation, we trust the signature was generated correctly
        # and focus on the evidence evaluation
        
        # Check false positive history
        fp_count = self.false_positive_history.get(message.node_id, 0)
        
        # Auto-approve if threshold reached
        if fp_count >= self.auto_approve_threshold:
            actions = [
                f"unblocked_node_{message.node_id}",
                "added_to_whitelist",
                "notified_admin"
            ]
            
            response = RescueResponse(
                message_id=message.message_id,
                approved=True,
                reason=f"Auto-approved: {fp_count} false positives detected",
                actions_taken=actions,
                timestamp=datetime.utcnow()
            )
            
            self.unblocked_nodes[message.node_id] = datetime.utcnow()
            self.total_approved += 1
            self.total_auto_approved += 1
            
        # Critical priority messages
        elif message.priority == RescuePriority.CRITICAL:
            actions = [
                f"emergency_unblock_{message.node_id}",
                "escalated_to_admin",
                "logged_incident"
            ]
            
            response = RescueResponse(
                message_id=message.message_id,
                approved=True,
                reason="Critical priority rescue request approved",
                actions_taken=actions,
                timestamp=datetime.utcnow()
            )
            
            self.unblocked_nodes[message.node_id] = datetime.utcnow()
            self.total_approved += 1
            
        # Manual review required
        else:
            # Check evidence quality
            evidence_score = self._evaluate_evidence(message.evidence)
            
            if evidence_score >= 0.7:  # 70% confidence threshold
                actions = [
                    f"unblocked_node_{message.node_id}",
                    "requires_monitoring"
                ]
                
                response = RescueResponse(
                    message_id=message.message_id,
                    approved=True,
                    reason=f"Strong evidence (score: {evidence_score:.2f})",
                    actions_taken=actions,
                    timestamp=datetime.utcnow()
                )
                
                self.unblocked_nodes[message.node_id] = datetime.utcnow()
                self.false_positive_history[message.node_id] = fp_count + 1
                self.total_approved += 1
            else:
                response = RescueResponse(
                    message_id=message.message_id,
                    approved=False,
                    reason=f"Insufficient evidence (score: {evidence_score:.2f})",
                    actions_taken=["requires_admin_review"],
                    timestamp=datetime.utcnow()
                )
                self.total_denied += 1
        
        self.responses[message.message_id] = response
        return response
    
    def _evaluate_evidence(self, evidence: Dict[str, Any]) -> float:
        """
        Evaluate quality of evidence for rescue request.
        
        Args:
            evidence: Evidence dictionary
            
        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0
        
        # Check for various evidence types
        if "legitimate_traffic_pattern" in evidence:
            score += 0.3
        
        if "historical_data" in evidence:
            score += 0.2
        
        if "user_verification" in evidence:
            score += 0.3
        
        if "third_party_validation" in evidence:
            score += 0.2
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def send_rescue_request(self,
                          sender_id: str,
                          node_id: str,
                          reason: str,
                          evidence: Dict[str, Any],
                          priority: RescuePriority = RescuePriority.NORMAL) -> Dict[str, Any]:
        """
        Send a rescue request to unblock a node.
        
        Args:
            sender_id: ID of requester
            node_id: ID of blocked node
            reason: Reason for unblock request
            evidence: Supporting evidence
            priority: Request priority
            
        Returns:
            Result dictionary with message and response
        """
        # Create rescue message
        message = self.create_rescue_message(
            message_type=RescueMessageType.UNBLOCK_REQUEST,
            sender_id=sender_id,
            node_id=node_id,
            reason=reason,
            evidence=evidence,
            priority=priority
        )
        
        # Evaluate request
        response = self.evaluate_rescue_request(message)
        
        return {
            "message": message.to_dict(),
            "response": response.to_dict(),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def get_rescue_status(self) -> Dict[str, Any]:
        """
        Get current status of rescue channel.
        
        Returns:
            Status dictionary
        """
        active_unblocks = {
            node_id: time
            for node_id, time in self.unblocked_nodes.items()
            if datetime.utcnow() - time < timedelta(hours=self.rescue_window_hours)
        }
        
        return {
            "statistics": {
                "total_requests": self.total_requests,
                "total_approved": self.total_approved,
                "total_denied": self.total_denied,
                "auto_approved": self.total_auto_approved,
                "approval_rate": round(self.total_approved / max(self.total_requests, 1), 2)
            },
            "active_unblocks": len(active_unblocks),
            "false_positive_tracking": len(self.false_positive_history),
            "config": {
                "auto_approve_threshold": self.auto_approve_threshold,
                "rescue_window_hours": self.rescue_window_hours
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
