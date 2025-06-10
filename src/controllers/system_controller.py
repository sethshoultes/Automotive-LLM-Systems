"""
System Controller - Main orchestration and coordination
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass

from voice.manager import VoiceManager, VoiceCommand, AudioConfig
from controllers.llm_controller import LLMController, LLMResponse
from controllers.hvac_controller import HVACController
from interfaces.vehicle import VehicleManager
from safety.monitor import SafetyMonitor
from config.settings import Settings


@dataclass
class SystemStatus:
    """Overall system status."""
    initialized: bool
    voice_active: bool
    vehicle_connected: bool
    safety_level: str
    llm_ready: bool
    uptime: float
    commands_processed: int


class SystemController:
    """Central system controller that orchestrates all components."""
    
    def __init__(self, settings: Settings, safety_monitor: SafetyMonitor):
        self.settings = settings
        self.safety_monitor = safety_monitor
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.vehicle_manager: Optional[VehicleManager] = None
        self.voice_manager: Optional[VoiceManager] = None
        self.llm_controller: Optional[LLMController] = None
        self.hvac_controller: Optional[HVACController] = None
        
        # System state
        self.initialized = False
        self.running = False
        self.start_time = time.time()
        
        # Statistics
        self.stats = {
            "commands_processed": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "voice_activations": 0,
            "safety_violations": 0,
            "uptime_start": time.time()
        }
    
    async def initialize(self) -> bool:
        """Initialize all system components."""
        try:
            self.logger.info("🚀 Initializing System Controller...")
            
            # Initialize vehicle manager
            self.vehicle_manager = VehicleManager(
                obd_port=self.settings.vehicle.obd_port,
                can_channel=self.settings.vehicle.can_channel
            )
            
            if not await self.vehicle_manager.initialize():
                self.logger.warning("⚠️ Vehicle manager initialization failed - continuing with limited functionality")
            
            # Set vehicle manager in safety monitor
            self.safety_monitor.vehicle_manager = self.vehicle_manager
            
            # Initialize LLM controller
            self.llm_controller = LLMController(
                model_name=self.settings.llm.model_name,
                ollama_host=self.settings.llm.ollama_host
            )
            
            if not await self.llm_controller.initialize():
                self.logger.error("❌ LLM controller initialization failed")
                return False
            
            # Initialize HVAC controller
            self.hvac_controller = HVACController(self.vehicle_manager)
            
            if not await self.hvac_controller.initialize():
                self.logger.warning("⚠️ HVAC controller initialization failed")
            
            # Initialize voice manager
            audio_config = AudioConfig(
                sample_rate=self.settings.audio.sample_rate,
                channels=self.settings.audio.channels,
                chunk_size=self.settings.audio.chunk_size,
                input_device_index=self.settings.audio.input_device_index
            )
            
            self.voice_manager = VoiceManager(
                config=audio_config,
                command_callback=self._handle_voice_command
            )
            
            if not await self.voice_manager.initialize():
                self.logger.error("❌ Voice manager initialization failed")
                return False
            
            self.initialized = True
            self.logger.info("✅ System Controller initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            return False
    
    async def start(self) -> None:
        """Start the automotive LLM system."""
        if not self.initialized:
            raise RuntimeError("System not initialized")
        
        self.running = True
        self.logger.info("🎯 Starting Automotive LLM System...")
        
        try:
            # Start voice listening
            await self.voice_manager.start_listening()
            
            # Start periodic tasks
            await self._start_periodic_tasks()
            
            self.logger.info("✅ System started successfully")
            
        except Exception as e:
            self.logger.error(f"System start failed: {e}")
            self.running = False
            raise
    
    async def _start_periodic_tasks(self) -> None:
        """Start background periodic tasks."""
        # HVAC auto-adjustment task (every 30 seconds)
        if self.hvac_controller:
            asyncio.create_task(self._hvac_auto_task())
        
        # System health monitoring task (every 60 seconds)
        asyncio.create_task(self._health_monitoring_task())
        
        # Statistics update task (every 300 seconds)
        asyncio.create_task(self._stats_update_task())
    
    async def _hvac_auto_task(self) -> None:
        """Periodic HVAC auto-adjustment task."""
        while self.running:
            try:
                await self.hvac_controller.auto_adjust()
                await asyncio.sleep(30.0)  # Every 30 seconds
            except Exception as e:
                self.logger.error(f"HVAC auto task error: {e}")
                await asyncio.sleep(30.0)
    
    async def _health_monitoring_task(self) -> None:
        """Periodic system health monitoring."""
        while self.running:
            try:
                await self._check_system_health()
                await asyncio.sleep(60.0)  # Every minute
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60.0)
    
    async def _stats_update_task(self) -> None:
        """Periodic statistics logging."""
        while self.running:
            try:
                await self._log_system_stats()
                await asyncio.sleep(300.0)  # Every 5 minutes
            except Exception as e:
                self.logger.error(f"Stats update error: {e}")
                await asyncio.sleep(300.0)
    
    async def _handle_voice_command(self, voice_command: VoiceCommand) -> None:
        """Handle incoming voice commands."""
        try:
            self.stats["voice_activations"] += 1
            self.stats["commands_processed"] += 1
            
            self.logger.info(f"🎤 Processing voice command: '{voice_command.text}'")
            
            # Get current vehicle status for context
            vehicle_status = {}
            if self.vehicle_manager:
                vehicle_status = await self.vehicle_manager.get_vehicle_status()
                vehicle_status = {k: v.value for k, v in vehicle_status.items()}
            
            # Process command with LLM
            llm_response = await self.llm_controller.process_command(
                voice_command.text,
                vehicle_status
            )
            
            # Validate command safety
            if llm_response.intent:
                validation = await self.safety_monitor.validate_command(
                    llm_response.intent.intent_type.value,
                    llm_response.intent.target,
                    llm_response.intent.value,
                    vehicle_status
                )
                
                if not validation.allowed:
                    # Command blocked for safety
                    await self.voice_manager.speak(
                        f"Sorry, I cannot execute that command: {validation.blocked_reason}"
                    )
                    self.stats["failed_commands"] += 1
                    return
                
                # Check if confirmation required
                if validation.required_confirmations:
                    response_text = llm_response.text + " " + " ".join(validation.warnings)
                    if llm_response.requires_confirmation:
                        response_text += " Please say 'confirm' to proceed."
                    
                    await self.voice_manager.speak(response_text)
                    # In a full implementation, would wait for confirmation
                    return
            
            # Execute the command
            if llm_response.intent:
                success = await self._execute_command(llm_response)
                
                if success:
                    self.stats["successful_commands"] += 1
                    await self.voice_manager.speak(llm_response.text)
                else:
                    self.stats["failed_commands"] += 1
                    await self.voice_manager.speak("Sorry, I couldn't complete that command.")
            else:
                # No intent recognized
                await self.voice_manager.speak(llm_response.text)
                self.stats["failed_commands"] += 1
            
        except Exception as e:
            self.logger.error(f"Voice command handling error: {e}")
            self.stats["failed_commands"] += 1
            await self.voice_manager.speak("Sorry, there was an error processing your command.")
    
    async def _execute_command(self, llm_response: LLMResponse) -> bool:
        """Execute a parsed command."""
        if not llm_response.intent:
            return False
        
        intent = llm_response.intent
        
        try:
            # Route command to appropriate controller
            if intent.intent_type.value == "climate_control":
                return await self._execute_hvac_command(intent)
            
            elif intent.intent_type.value == "lighting_control":
                return await self._execute_lighting_command(intent)
            
            elif intent.intent_type.value == "engine_management":
                return await self._execute_engine_command(intent)
            
            elif intent.intent_type.value == "audio_control":
                return await self._execute_audio_command(intent)
            
            elif intent.intent_type.value == "vehicle_status":
                return await self._execute_status_command(intent)
            
            elif intent.intent_type.value == "emergency_action":
                return await self._execute_emergency_command(intent)
            
            else:
                self.logger.warning(f"Unknown intent type: {intent.intent_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            return False
    
    async def _execute_hvac_command(self, intent) -> bool:
        """Execute HVAC-related commands."""
        if not self.hvac_controller:
            return False
        
        if intent.target == "temperature":
            if intent.action == "set" and intent.value:
                result = await self.hvac_controller.set_temperature(float(intent.value))
                return result.get("success", False)
        
        elif intent.target == "air_conditioning":
            if intent.action == "activate":
                result = await self.hvac_controller.toggle_ac()
                return result.get("success", False)
        
        elif intent.target == "fan_speed":
            if intent.action in ["set", "increase", "decrease"] and intent.value:
                result = await self.hvac_controller.set_fan_speed(int(intent.value))
                return result.get("success", False)
        
        return False
    
    async def _execute_lighting_command(self, intent) -> bool:
        """Execute lighting control commands."""
        if not self.vehicle_manager:
            return False
        
        if intent.target == "interior_lights":
            if intent.action == "set" and intent.value:
                return await self.vehicle_manager.set_parameter("interior_lights", int(intent.value))
        
        return False
    
    async def _execute_engine_command(self, intent) -> bool:
        """Execute engine management commands."""
        if not self.vehicle_manager:
            return False
        
        if intent.target == "boost_pressure":
            if intent.action in ["set", "increase"] and intent.value:
                return await self.vehicle_manager.set_parameter("boost_pressure", float(intent.value))
        
        return False
    
    async def _execute_audio_command(self, intent) -> bool:
        """Execute audio system commands."""
        if not self.vehicle_manager:
            return False
        
        if intent.target == "volume":
            if intent.action in ["set", "increase", "decrease"] and intent.value:
                return await self.vehicle_manager.set_parameter("audio_volume", int(intent.value))
        
        return False
    
    async def _execute_status_command(self, intent) -> bool:
        """Execute status inquiry commands."""
        if not self.vehicle_manager:
            return False
        
        if intent.target == "engine_temperature":
            param = await self.vehicle_manager.get_parameter("engine_temp")
            if param:
                # Status successfully retrieved
                return True
        
        return False
    
    async def _execute_emergency_command(self, intent) -> bool:
        """Execute emergency commands."""
        if intent.action == "stop":
            await self.safety_monitor.emergency_protocol()
            return True
        
        return False
    
    async def _check_system_health(self) -> None:
        """Check overall system health."""
        try:
            issues = []
            
            # Check voice manager
            if self.voice_manager and self.voice_manager.state.value == "error":
                issues.append("Voice manager in error state")
            
            # Check vehicle manager
            if self.vehicle_manager:
                # Check for communication issues
                pass
            
            # Check safety monitor
            if not await self.safety_monitor.health_check():
                issues.append("Safety monitor health check failed")
            
            # Log issues
            if issues:
                self.logger.warning(f"System health issues detected: {', '.join(issues)}")
            else:
                self.logger.debug("System health check passed")
                
        except Exception as e:
            self.logger.error(f"System health check error: {e}")
    
    async def _log_system_stats(self) -> None:
        """Log system statistics."""
        try:
            uptime = time.time() - self.stats["uptime_start"]
            
            stats_summary = {
                "uptime_hours": uptime / 3600,
                "commands_processed": self.stats["commands_processed"],
                "success_rate": (
                    self.stats["successful_commands"] / max(1, self.stats["commands_processed"])
                ) * 100,
                "voice_activations": self.stats["voice_activations"]
            }
            
            self.logger.info(f"📊 System Stats: {stats_summary}")
            
        except Exception as e:
            self.logger.error(f"Stats logging error: {e}")
    
    def get_system_status(self) -> SystemStatus:
        """Get current system status."""
        safety_status = self.safety_monitor.get_safety_status()
        
        return SystemStatus(
            initialized=self.initialized,
            voice_active=self.voice_manager is not None and self.voice_manager.state.value == "listening",
            vehicle_connected=self.vehicle_manager is not None,
            safety_level=safety_status["safety_level"],
            llm_ready=self.llm_controller is not None,
            uptime=time.time() - self.start_time,
            commands_processed=self.stats["commands_processed"]
        )
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed system status."""
        status = {
            "system": self.get_system_status().__dict__,
            "safety": self.safety_monitor.get_safety_status(),
            "stats": self.stats.copy()
        }
        
        if self.voice_manager:
            status["voice"] = self.voice_manager.get_stats()
        
        if self.llm_controller:
            status["llm"] = self.llm_controller.get_stats()
        
        if self.hvac_controller:
            status["hvac"] = self.hvac_controller.get_stats()
        
        return status
    
    async def shutdown(self) -> None:
        """Shutdown the system gracefully."""
        self.logger.info("🛑 Shutting down System Controller...")
        self.running = False
        
        # Stop voice manager
        if self.voice_manager:
            await self.voice_manager.stop_listening()
            self.voice_manager.cleanup()
        
        # Shutdown controllers
        if self.hvac_controller:
            await self.hvac_controller.shutdown()
        
        if self.llm_controller:
            await self.llm_controller.shutdown()
        
        # Shutdown vehicle manager
        if self.vehicle_manager:
            await self.vehicle_manager.shutdown()
        
        self.logger.info("✅ System Controller shutdown complete")