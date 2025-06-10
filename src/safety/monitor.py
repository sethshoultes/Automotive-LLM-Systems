"""
Safety Monitor - System safety validation and monitoring
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Callable, Any

from interfaces.vehicle import VehicleManager, VehicleParameter


class SafetyLevel(Enum):
    """Safety levels for different operations."""
    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class SafetyViolationType(Enum):
    """Types of safety violations."""
    TEMPERATURE_LIMIT = "temperature_limit"
    PRESSURE_LIMIT = "pressure_limit"
    SPEED_LIMIT = "speed_limit"
    RPM_LIMIT = "rpm_limit"
    ELECTRICAL_FAULT = "electrical_fault"
    COMMUNICATION_LOSS = "communication_loss"
    SENSOR_MALFUNCTION = "sensor_malfunction"
    USER_SAFETY = "user_safety"
    SYSTEM_INTEGRITY = "system_integrity"


@dataclass
class SafetyRule:
    """Defines a safety rule with limits and actions."""
    name: str
    parameter: str
    min_value: Optional[float]
    max_value: Optional[float]
    safety_level: SafetyLevel
    violation_type: SafetyViolationType
    action_required: bool
    description: str


@dataclass
class SafetyViolation:
    """Represents a safety rule violation."""
    rule_name: str
    parameter: str
    current_value: float
    limit_value: float
    safety_level: SafetyLevel
    violation_type: SafetyViolationType
    timestamp: float
    description: str
    action_taken: Optional[str] = None


@dataclass
class CommandValidationResult:
    """Result of command safety validation."""
    allowed: bool
    safety_level: SafetyLevel
    warnings: List[str]
    required_confirmations: List[str]
    blocked_reason: Optional[str] = None


class SafetyMonitor:
    """Central safety monitoring and validation system."""
    
    def __init__(self, settings, vehicle_manager: Optional[VehicleManager] = None):
        self.settings = settings
        self.vehicle_manager = vehicle_manager
        self.logger = logging.getLogger(__name__)
        
        # Safety state
        self.current_safety_level = SafetyLevel.SAFE
        self.active_violations: List[SafetyViolation] = []
        self.violation_history: List[SafetyViolation] = []
        
        # Emergency state
        self.emergency_mode = False
        self.emergency_callbacks: List[Callable] = []
        
        # Monitoring control
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.monitoring_interval = 1.0  # seconds
        
        # Safety rules
        self.safety_rules = self._initialize_safety_rules()
        
        # Statistics
        self.stats = {
            "violations_detected": 0,
            "commands_validated": 0,
            "commands_blocked": 0,
            "emergency_activations": 0
        }
    
    def _initialize_safety_rules(self) -> List[SafetyRule]:
        """Initialize safety rules for vehicle systems."""
        return [
            # Engine safety rules
            SafetyRule(
                name="engine_temp_critical",
                parameter="engine_temp",
                min_value=None,
                max_value=110.0,  # °C
                safety_level=SafetyLevel.CRITICAL,
                violation_type=SafetyViolationType.TEMPERATURE_LIMIT,
                action_required=True,
                description="Engine temperature exceeds critical limit"
            ),
            SafetyRule(
                name="engine_temp_warning",
                parameter="engine_temp",
                min_value=None,
                max_value=105.0,  # °C
                safety_level=SafetyLevel.WARNING,
                violation_type=SafetyViolationType.TEMPERATURE_LIMIT,
                action_required=False,
                description="Engine temperature high"
            ),
            SafetyRule(
                name="engine_rpm_limit",
                parameter="engine_rpm",
                min_value=None,
                max_value=7000.0,  # RPM
                safety_level=SafetyLevel.CRITICAL,
                violation_type=SafetyViolationType.RPM_LIMIT,
                action_required=True,
                description="Engine RPM exceeds redline"
            ),
            SafetyRule(
                name="oil_pressure_critical",
                parameter="oil_pressure",
                min_value=15.0,  # PSI
                max_value=None,
                safety_level=SafetyLevel.CRITICAL,
                violation_type=SafetyViolationType.PRESSURE_LIMIT,
                action_required=True,
                description="Oil pressure critically low"
            ),
            
            # Performance limits
            SafetyRule(
                name="boost_pressure_limit",
                parameter="boost_pressure",
                min_value=None,
                max_value=20.0,  # PSI (configurable per vehicle)
                safety_level=SafetyLevel.WARNING,
                violation_type=SafetyViolationType.PRESSURE_LIMIT,
                action_required=False,
                description="Boost pressure approaching limit"
            ),
            
            # HVAC safety rules
            SafetyRule(
                name="hvac_temp_max",
                parameter="hvac_temp_set",
                min_value=None,
                max_value=35.0,  # °C
                safety_level=SafetyLevel.CAUTION,
                violation_type=SafetyViolationType.TEMPERATURE_LIMIT,
                action_required=False,
                description="HVAC temperature set very high"
            ),
            SafetyRule(
                name="hvac_temp_min", 
                parameter="hvac_temp_set",
                min_value=15.0,  # °C
                max_value=None,
                safety_level=SafetyLevel.CAUTION,
                violation_type=SafetyViolationType.TEMPERATURE_LIMIT,
                action_required=False,
                description="HVAC temperature set very low"
            ),
            
            # Speed-based restrictions
            SafetyRule(
                name="high_speed_limit",
                parameter="vehicle_speed",
                min_value=None,
                max_value=80.0,  # km/h for certain operations
                safety_level=SafetyLevel.WARNING,
                violation_type=SafetyViolationType.SPEED_LIMIT,
                action_required=False,
                description="Vehicle speed too high for certain operations"
            )
        ]
    
    async def initialize(self) -> bool:
        """Initialize safety monitoring system."""
        try:
            self.logger.info("🛡️ Initializing Safety Monitor...")
            
            # Load custom safety rules from config if available
            await self._load_custom_safety_rules()
            
            # Start monitoring if vehicle manager is available
            if self.vehicle_manager:
                await self.start_monitoring()
            
            self.logger.info(f"✅ Safety Monitor initialized with {len(self.safety_rules)} rules")
            return True
            
        except Exception as e:
            self.logger.error(f"Safety Monitor initialization failed: {e}")
            return False
    
    async def _load_custom_safety_rules(self) -> None:
        """Load vehicle-specific safety rules from configuration."""
        # In a full implementation, would load from config files
        # For now, use defaults
        pass
    
    async def start_monitoring(self) -> None:
        """Start continuous safety monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("🔍 Safety monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop safety monitoring."""
        self.monitoring_active = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("⏹️ Safety monitoring stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main safety monitoring loop."""
        while self.monitoring_active:
            try:
                # Check all safety rules
                await self._check_safety_rules()
                
                # Update overall safety level
                self._update_safety_level()
                
                # Handle any emergency conditions
                if self.current_safety_level == SafetyLevel.EMERGENCY:
                    await self._handle_emergency()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Safety monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _check_safety_rules(self) -> None:
        """Check all safety rules against current vehicle state."""
        if not self.vehicle_manager:
            return
        
        current_violations = []
        
        for rule in self.safety_rules:
            try:
                # Get current parameter value
                param = await self.vehicle_manager.get_parameter(rule.parameter)
                if not param:
                    continue
                
                violation = self._check_rule_violation(rule, param)
                if violation:
                    current_violations.append(violation)
                    self.stats["violations_detected"] += 1
                    
                    # Log violation
                    self.logger.warning(f"⚠️ Safety violation: {violation.description}")
                    
                    # Take action if required
                    if rule.action_required:
                        await self._take_safety_action(violation)
            
            except Exception as e:
                self.logger.error(f"Error checking safety rule {rule.name}: {e}")
        
        # Update active violations
        self.active_violations = current_violations
        self.violation_history.extend(current_violations)
        
        # Keep violation history manageable
        if len(self.violation_history) > 1000:
            self.violation_history = self.violation_history[-500:]
    
    def _check_rule_violation(self, rule: SafetyRule, param: VehicleParameter) -> Optional[SafetyViolation]:
        """Check if a parameter violates a safety rule."""
        value = float(param.value)
        
        # Check maximum limit
        if rule.max_value is not None and value > rule.max_value:
            return SafetyViolation(
                rule_name=rule.name,
                parameter=rule.parameter,
                current_value=value,
                limit_value=rule.max_value,
                safety_level=rule.safety_level,
                violation_type=rule.violation_type,
                timestamp=time.time(),
                description=f"{rule.description}: {value} > {rule.max_value}"
            )
        
        # Check minimum limit
        if rule.min_value is not None and value < rule.min_value:
            return SafetyViolation(
                rule_name=rule.name,
                parameter=rule.parameter,
                current_value=value,
                limit_value=rule.min_value,
                safety_level=rule.safety_level,
                violation_type=rule.violation_type,
                timestamp=time.time(),
                description=f"{rule.description}: {value} < {rule.min_value}"
            )
        
        return None
    
    async def _take_safety_action(self, violation: SafetyViolation) -> None:
        """Take appropriate action for a safety violation."""
        action_taken = None
        
        if violation.violation_type == SafetyViolationType.TEMPERATURE_LIMIT:
            if violation.parameter == "engine_temp":
                action_taken = "Engine protection mode activated"
                # In real implementation, would limit power, increase cooling
                
        elif violation.violation_type == SafetyViolationType.PRESSURE_LIMIT:
            if violation.parameter == "oil_pressure":
                action_taken = "Engine shutdown protection activated"
                # In real implementation, would limit RPM or shut down
            elif violation.parameter == "boost_pressure":
                action_taken = "Boost pressure limited"
                # Would reduce boost pressure
                
        elif violation.violation_type == SafetyViolationType.RPM_LIMIT:
            action_taken = "Rev limiter activated"
            # Would cut ignition/fuel to limit RPM
        
        if action_taken:
            violation.action_taken = action_taken
            self.logger.critical(f"🚨 Safety action: {action_taken}")
    
    def _update_safety_level(self) -> None:
        """Update overall system safety level based on active violations."""
        if not self.active_violations:
            self.current_safety_level = SafetyLevel.SAFE
            return
        
        # Find highest severity violation
        max_level = SafetyLevel.SAFE
        for violation in self.active_violations:
            if violation.safety_level.value == "emergency":
                max_level = SafetyLevel.EMERGENCY
                break
            elif violation.safety_level.value == "critical" and max_level.value != "emergency":
                max_level = SafetyLevel.CRITICAL
            elif violation.safety_level.value == "warning" and max_level.value not in ["emergency", "critical"]:
                max_level = SafetyLevel.WARNING
            elif violation.safety_level.value == "caution" and max_level.value == "safe":
                max_level = SafetyLevel.CAUTION
        
        if max_level != self.current_safety_level:
            self.logger.info(f"🔄 Safety level changed: {self.current_safety_level.value} -> {max_level.value}")
            self.current_safety_level = max_level
    
    async def _handle_emergency(self) -> None:
        """Handle emergency safety conditions."""
        if not self.emergency_mode:
            self.emergency_mode = True
            self.stats["emergency_activations"] += 1
            self.logger.critical("🚨 EMERGENCY MODE ACTIVATED")
            
            # Notify all emergency callbacks
            for callback in self.emergency_callbacks:
                try:
                    await callback()
                except Exception as e:
                    self.logger.error(f"Emergency callback error: {e}")
    
    async def validate_command(self, 
                              intent_type: str, 
                              parameter: str, 
                              value: Any,
                              vehicle_state: Optional[Dict[str, Any]] = None) -> CommandValidationResult:
        """Validate if a command is safe to execute."""
        self.stats["commands_validated"] += 1
        
        warnings = []
        confirmations = []
        safety_level = SafetyLevel.SAFE
        
        try:
            # Check if in emergency mode
            if self.emergency_mode:
                self.stats["commands_blocked"] += 1
                return CommandValidationResult(
                    allowed=False,
                    safety_level=SafetyLevel.EMERGENCY,
                    warnings=[],
                    required_confirmations=[],
                    blocked_reason="System in emergency mode - only emergency commands allowed"
                )
            
            # Vehicle speed restrictions
            vehicle_speed = self._get_vehicle_speed(vehicle_state)
            if vehicle_speed and vehicle_speed > 5.0:  # km/h
                if intent_type == "engine_management":
                    warnings.append("Engine modifications while moving can be dangerous")
                    confirmations.append("Confirm you want to modify engine parameters while driving")
                    safety_level = SafetyLevel.WARNING
                
                if parameter in ["boost_pressure", "fuel_trim", "ignition_timing"]:
                    if vehicle_speed > 50.0:
                        self.stats["commands_blocked"] += 1
                        return CommandValidationResult(
                            allowed=False,
                            safety_level=SafetyLevel.CRITICAL,
                            warnings=[],
                            required_confirmations=[],
                            blocked_reason="Engine tuning not allowed at highway speeds"
                        )
            
            # Parameter-specific validations
            if parameter == "boost_pressure":
                if isinstance(value, (int, float)) and value > 15.0:
                    warnings.append(f"Boost pressure {value} PSI is high - ensure engine can handle it")
                    confirmations.append("Confirm boost pressure increase is safe for your engine")
                    safety_level = SafetyLevel.CAUTION
                    
                if isinstance(value, (int, float)) and value > 20.0:
                    self.stats["commands_blocked"] += 1
                    return CommandValidationResult(
                        allowed=False,
                        safety_level=SafetyLevel.CRITICAL,
                        warnings=[],
                        required_confirmations=[],
                        blocked_reason="Boost pressure exceeds maximum safe limit"
                    )
            
            elif parameter == "hvac_temp_set":
                if isinstance(value, (int, float)):
                    if value > 35.0:
                        warnings.append("High cabin temperature may cause discomfort")
                        safety_level = SafetyLevel.CAUTION
                    elif value < 15.0:
                        warnings.append("Low cabin temperature may cause discomfort")
                        safety_level = SafetyLevel.CAUTION
            
            elif parameter == "engine_rpm":
                if isinstance(value, (int, float)) and value > 6000:
                    warnings.append("High RPM operation can cause engine damage")
                    confirmations.append("Confirm high RPM operation is safe")
                    safety_level = SafetyLevel.WARNING
            
            # Check against active safety violations
            for violation in self.active_violations:
                if violation.parameter == parameter:
                    if violation.safety_level in [SafetyLevel.CRITICAL, SafetyLevel.EMERGENCY]:
                        self.stats["commands_blocked"] += 1
                        return CommandValidationResult(
                            allowed=False,
                            safety_level=violation.safety_level,
                            warnings=[],
                            required_confirmations=[],
                            blocked_reason=f"Parameter {parameter} has active safety violation"
                        )
                    else:
                        warnings.append(f"Active safety concern with {parameter}: {violation.description}")
            
            return CommandValidationResult(
                allowed=True,
                safety_level=safety_level,
                warnings=warnings,
                required_confirmations=confirmations
            )
            
        except Exception as e:
            self.logger.error(f"Command validation error: {e}")
            self.stats["commands_blocked"] += 1
            return CommandValidationResult(
                allowed=False,
                safety_level=SafetyLevel.CRITICAL,
                warnings=[],
                required_confirmations=[],
                blocked_reason="Safety validation system error"
            )
    
    def _get_vehicle_speed(self, vehicle_state: Optional[Dict[str, Any]]) -> Optional[float]:
        """Extract vehicle speed from state data."""
        if not vehicle_state:
            return None
        
        # Try different possible keys for vehicle speed
        speed_keys = ["vehicle_speed", "speed", "mph", "kph"]
        for key in speed_keys:
            if key in vehicle_state:
                return float(vehicle_state[key])
        
        return None
    
    async def emergency_protocol(self) -> None:
        """Execute emergency safety protocol."""
        self.logger.critical("🚨 EXECUTING EMERGENCY SAFETY PROTOCOL")
        
        self.emergency_mode = True
        self.current_safety_level = SafetyLevel.EMERGENCY
        
        # Emergency actions would include:
        # - Disable all performance modifications
        # - Return systems to safe defaults
        # - Activate emergency lighting
        # - Log emergency event
        
        emergency_action = {
            "timestamp": time.time(),
            "reason": "Emergency protocol activated",
            "active_violations": len(self.active_violations),
            "safety_level": self.current_safety_level.value
        }
        
        self.logger.critical(f"Emergency action logged: {emergency_action}")
    
    def register_emergency_callback(self, callback: Callable) -> None:
        """Register callback for emergency conditions."""
        self.emergency_callbacks.append(callback)
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety system status."""
        return {
            "safety_level": self.current_safety_level.value,
            "emergency_mode": self.emergency_mode,
            "active_violations": len(self.active_violations),
            "monitoring_active": self.monitoring_active,
            "recent_violations": [
                {
                    "rule": v.rule_name,
                    "parameter": v.parameter,
                    "current_value": v.current_value,
                    "limit_value": v.limit_value,
                    "level": v.safety_level.value,
                    "description": v.description
                }
                for v in self.active_violations
            ],
            "stats": self.stats.copy()
        }
    
    async def health_check(self) -> bool:
        """Perform safety system health check."""
        try:
            # Check if monitoring is running properly
            if self.monitoring_active and (not self.monitoring_task or self.monitoring_task.done()):
                self.logger.error("Safety monitoring task has stopped")
                return False
            
            # Check for critical violations
            critical_violations = [
                v for v in self.active_violations 
                if v.safety_level in [SafetyLevel.CRITICAL, SafetyLevel.EMERGENCY]
            ]
            
            if critical_violations:
                self.logger.warning(f"Health check: {len(critical_violations)} critical violations active")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Safety health check failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get safety monitoring statistics."""
        return self.stats.copy()
    
    async def shutdown(self) -> None:
        """Shutdown safety monitoring system."""
        self.logger.info("🛑 Shutting down Safety Monitor...")
        
        await self.stop_monitoring()
        
        # Log final safety state
        if self.active_violations:
            self.logger.warning(f"Shutdown with {len(self.active_violations)} active violations")
        
        self.logger.info("✅ Safety Monitor shutdown complete")