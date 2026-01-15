"""
Lazy Security Module
Energy-based protection system activated only when environmental scan detects pressure.

Based on Rotesschild scan technology - activates protections when electromagnetic
pressure exceeds 50 mV/m threshold.
"""

import time
import random
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class SecurityLevel(Enum):
    """Security activation levels"""
    DORMANT = 0  # No active protection
    MONITORING = 1  # Passive monitoring only
    ACTIVE = 2  # Full protection active
    CRITICAL = 3  # Maximum security


@dataclass
class EnvironmentalScan:
    """Results from Rotesschild environmental scan"""
    pressure_mv_m: float  # Electromagnetic pressure in mV/m
    timestamp: datetime
    location: str
    scan_quality: float  # 0-1, quality of scan
    
    def exceeds_threshold(self, threshold: float = 50.0) -> bool:
        """Check if pressure exceeds activation threshold"""
        return self.pressure_mv_m > threshold


class LazySecurity:
    """
    Energy-efficient security system that activates only when needed.
    Monitors environmental pressure and activates protection algorithms accordingly.
    """
    
    def __init__(self,
                 activation_threshold: float = 50.0,  # mV/m
                 scan_interval: int = 60,  # seconds
                 energy_budget: float = 100.0):  # arbitrary energy units
        self.activation_threshold = activation_threshold
        self.scan_interval = scan_interval
        self.energy_budget = energy_budget
        self.current_energy = energy_budget
        
        self.security_level = SecurityLevel.DORMANT
        self.last_scan: Optional[EnvironmentalScan] = None
        self.scan_history: List[EnvironmentalScan] = []
        self.protection_modules: Dict[str, Callable] = {}
        self.active_protections: set = set()
        
        # Statistics
        self.total_scans = 0
        self.total_activations = 0
        self.energy_saved = 0.0
        self.threats_blocked = 0
        
    def register_protection_module(self, 
                                   name: str, 
                                   module: Callable,
                                   energy_cost: float = 1.0):
        """
        Register a protection module to be activated when needed.
        
        Args:
            name: Module identifier
            module: Callable protection function
            energy_cost: Energy units consumed per activation
        """
        self.protection_modules[name] = {
            "function": module,
            "energy_cost": energy_cost,
            "activations": 0,
            "blocks": 0
        }
    
    def perform_rotesschild_scan(self, 
                                 location: str = "default") -> EnvironmentalScan:
        """
        Perform environmental electromagnetic pressure scan.
        In production, this would interface with actual sensors.
        
        Args:
            location: Scan location identifier
            
        Returns:
            EnvironmentalScan object with results
        """
        # Simulate sensor reading (in production, read from actual sensors)
        # Use time-based variation for realistic simulation
        base_pressure = 30.0
        variation = random.uniform(-20.0, 40.0)
        time_factor = abs(time.time() % 100 - 50) / 50.0  # 0 to 1
        
        pressure = base_pressure + (variation * time_factor)
        quality = random.uniform(0.85, 1.0)
        
        scan = EnvironmentalScan(
            pressure_mv_m=pressure,
            timestamp=datetime.utcnow(),
            location=location,
            scan_quality=quality
        )
        
        self.last_scan = scan
        self.scan_history.append(scan)
        self.total_scans += 1
        
        # Keep only recent history
        if len(self.scan_history) > 100:
            self.scan_history.pop(0)
        
        return scan
    
    def evaluate_security_level(self, scan: EnvironmentalScan) -> SecurityLevel:
        """
        Determine appropriate security level based on scan results.
        
        Args:
            scan: Recent environmental scan
            
        Returns:
            Appropriate SecurityLevel
        """
        pressure = scan.pressure_mv_m
        
        if pressure < self.activation_threshold * 0.5:
            return SecurityLevel.DORMANT
        elif pressure < self.activation_threshold:
            return SecurityLevel.MONITORING
        elif pressure < self.activation_threshold * 1.5:
            return SecurityLevel.ACTIVE
        else:
            return SecurityLevel.CRITICAL
    
    def activate_protections(self, level: SecurityLevel):
        """
        Activate appropriate protection modules based on security level.
        
        Args:
            level: Target security level
        """
        if level == SecurityLevel.DORMANT:
            # Deactivate all protections
            self.active_protections.clear()
            
        elif level == SecurityLevel.MONITORING:
            # Only passive monitoring
            self.active_protections = {"monitoring"}
            
        elif level == SecurityLevel.ACTIVE:
            # Activate core protections
            self.active_protections = {"monitoring", "rhythm_validation", "rate_limiting"}
            
        elif level == SecurityLevel.CRITICAL:
            # Activate all available protections
            self.active_protections = set(self.protection_modules.keys())
        
        if level != SecurityLevel.DORMANT:
            self.total_activations += 1
    
    def update_security_state(self) -> Dict[str, Any]:
        """
        Perform scan and update security state accordingly.
        This is the main lazy security logic.
        
        Returns:
            Status dict with scan results and actions taken
        """
        # Perform environmental scan
        scan = self.perform_rotesschild_scan()
        
        # Evaluate required security level
        required_level = self.evaluate_security_level(scan)
        
        # Calculate energy savings if staying dormant
        previous_level = self.security_level
        if previous_level == SecurityLevel.DORMANT and required_level == SecurityLevel.DORMANT:
            # Count energy saved by not activating
            potential_energy_cost = sum(
                m["energy_cost"] for m in self.protection_modules.values()
            )
            self.energy_saved += potential_energy_cost
        
        # Update security level and activate/deactivate protections
        self.security_level = required_level
        self.activate_protections(required_level)
        
        # Regenerate energy when dormant
        if required_level == SecurityLevel.DORMANT:
            self.current_energy = min(
                self.energy_budget,
                self.current_energy + 1.0
            )
        
        return {
            "scan": {
                "pressure_mv_m": scan.pressure_mv_m,
                "threshold": self.activation_threshold,
                "exceeds_threshold": scan.exceeds_threshold(self.activation_threshold),
                "location": scan.location,
                "quality": scan.scan_quality,
                "timestamp": scan.timestamp.isoformat() + "Z"
            },
            "security": {
                "previous_level": previous_level.name,
                "current_level": required_level.name,
                "active_protections": list(self.active_protections),
                "energy_remaining": self.current_energy,
                "energy_budget": self.energy_budget
            },
            "statistics": {
                "total_scans": self.total_scans,
                "total_activations": self.total_activations,
                "energy_saved": self.energy_saved,
                "threats_blocked": self.threats_blocked
            }
        }
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request through lazy security system.
        Only applies active protections based on current security level.
        
        Args:
            request_data: Request to process
            
        Returns:
            Processing result
        """
        # If dormant, allow everything through (lazy mode)
        if self.security_level == SecurityLevel.DORMANT:
            return {
                "allowed": True,
                "reason": "security_dormant",
                "energy_saved": True,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        
        # Apply active protections
        for protection_name in self.active_protections:
            if protection_name in self.protection_modules:
                module_info = self.protection_modules[protection_name]
                module_func = module_info["function"]
                
                # Consume energy
                if self.current_energy >= module_info["energy_cost"]:
                    self.current_energy -= module_info["energy_cost"]
                    
                    # Run protection module
                    try:
                        result = module_func(request_data)
                        module_info["activations"] += 1
                        
                        if not result.get("allowed", True):
                            module_info["blocks"] += 1
                            self.threats_blocked += 1
                            return {
                                "allowed": False,
                                "reason": f"blocked_by_{protection_name}",
                                "details": result,
                                "timestamp": datetime.utcnow().isoformat() + "Z"
                            }
                    except Exception as e:
                        # Protection module error, log but continue
                        pass
        
        return {
            "allowed": True,
            "reason": "passed_all_protections",
            "protections_applied": list(self.active_protections),
            "security_level": self.security_level.name,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of lazy security system"""
        return {
            "security_level": self.security_level.name,
            "active_protections": list(self.active_protections),
            "activation_threshold_mv_m": self.activation_threshold,
            "last_scan": {
                "pressure_mv_m": self.last_scan.pressure_mv_m if self.last_scan else None,
                "timestamp": self.last_scan.timestamp.isoformat() + "Z" if self.last_scan else None
            } if self.last_scan else None,
            "energy": {
                "current": self.current_energy,
                "budget": self.energy_budget,
                "saved": self.energy_saved
            },
            "statistics": {
                "total_scans": self.total_scans,
                "total_activations": self.total_activations,
                "threats_blocked": self.threats_blocked
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
