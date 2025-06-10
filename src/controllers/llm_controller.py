"""
LLM Controller - Manages local language model integration and processing
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import aiohttp

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("Ollama not available - using mock LLM responses")


class IntentType(Enum):
    """Types of user intents."""
    CLIMATE_CONTROL = "climate_control"
    LIGHTING_CONTROL = "lighting_control" 
    ENGINE_MANAGEMENT = "engine_management"
    AUDIO_CONTROL = "audio_control"
    VEHICLE_STATUS = "vehicle_status"
    EMERGENCY_ACTION = "emergency_action"
    SYSTEM_CONFIG = "system_config"
    UNKNOWN = "unknown"


@dataclass
class Entity:
    """Extracted entity from user input."""
    name: str
    value: Any
    confidence: float
    start_pos: int
    end_pos: int


@dataclass
class Intent:
    """Parsed user intent with entities."""
    intent_type: IntentType
    confidence: float
    entities: List[Entity]
    raw_text: str
    action: str  # increase, decrease, set, get, activate, etc.
    target: str  # temperature, volume, lights, etc.
    value: Optional[Any] = None


@dataclass
class LLMResponse:
    """Response from LLM processing."""
    text: str
    intent: Optional[Intent]
    confidence: float
    processing_time: float
    requires_confirmation: bool = False
    safety_warning: Optional[str] = None


class AutomotivePromptTemplate:
    """Automotive-specific prompt templates."""
    
    SYSTEM_PROMPT = """You are an AI assistant for automotive systems. You help drivers control vehicle systems safely through voice commands.

Your capabilities include:
- HVAC control (temperature, fan speed, modes)
- Lighting control (interior, exterior, brightness)
- Engine monitoring (diagnostics, performance)
- Audio system control (volume, source, playback)
- Vehicle status information

Safety Rules:
1. NEVER control critical safety systems (brakes, steering, airbags)
2. Always prioritize driver safety over convenience
3. Require confirmation for performance modifications
4. Refuse commands that could be dangerous while driving
5. Provide clear, concise responses suitable for voice interaction

Respond with JSON containing:
- "intent": the parsed intent type
- "action": the action to perform
- "target": the target system/parameter
- "value": the specific value (if applicable)
- "confidence": confidence score 0-1
- "response": natural language response
- "requires_confirmation": boolean for safety-critical actions
- "safety_warning": warning message if applicable

Examples:
Input: "Turn up the heat to 75 degrees"
Output: {
  "intent": "climate_control",
  "action": "set",
  "target": "temperature", 
  "value": 75,
  "confidence": 0.95,
  "response": "Setting temperature to 75 degrees",
  "requires_confirmation": false
}

Input: "Increase boost pressure by 3 PSI"
Output: {
  "intent": "engine_management",
  "action": "increase",
  "target": "boost_pressure",
  "value": 3,
  "confidence": 0.90,
  "response": "This will increase boost pressure by 3 PSI. Please confirm this is safe for your engine.",
  "requires_confirmation": true,
  "safety_warning": "Boost pressure modifications can damage your engine if not done properly"
}
"""

    CONTEXT_PROMPT = """Previous conversation:
{conversation_history}

Current vehicle status:
{vehicle_status}

User command: "{user_input}"

Provide appropriate response considering the context and current vehicle state."""


class ConversationManager:
    """Manages conversation context and history."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversation_history: List[Dict[str, str]] = []
        self.current_context: Dict[str, Any] = {}
        
    def add_interaction(self, user_input: str, assistant_response: str) -> None:
        """Add interaction to conversation history."""
        interaction = {
            "timestamp": time.time(),
            "user": user_input,
            "assistant": assistant_response
        }
        
        self.conversation_history.append(interaction)
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_context_string(self) -> str:
        """Get formatted conversation history."""
        if not self.conversation_history:
            return "No previous conversation"
        
        context_lines = []
        for interaction in self.conversation_history[-5:]:  # Last 5 interactions
            context_lines.append(f"User: {interaction['user']}")
            context_lines.append(f"Assistant: {interaction['assistant']}")
        
        return "\n".join(context_lines)
    
    def update_context(self, key: str, value: Any) -> None:
        """Update conversation context."""
        self.current_context[key] = value
    
    def clear_context(self) -> None:
        """Clear conversation context."""
        self.conversation_history.clear()
        self.current_context.clear()


class LLMController:
    """Controls local LLM processing for automotive commands."""
    
    def __init__(self, 
                 model_name: str = "llama3.1:8b-instruct-q4_K_M",
                 ollama_host: str = "http://localhost:11434"):
        
        self.model_name = model_name
        self.ollama_host = ollama_host
        self.logger = logging.getLogger(__name__)
        self.mock_mode = not OLLAMA_AVAILABLE
        
        # Conversation management
        self.conversation_manager = ConversationManager()
        
        # Performance tracking
        self.stats = {
            "requests_processed": 0,
            "average_processing_time": 0.0,
            "successful_responses": 0,
            "failed_responses": 0
        }
        
        # Mock responses for development
        self.mock_responses = {
            "turn on air conditioning": {
                "intent": "climate_control",
                "action": "activate",
                "target": "air_conditioning",
                "confidence": 0.95,
                "response": "Air conditioning is now on"
            },
            "set temperature to 72": {
                "intent": "climate_control", 
                "action": "set",
                "target": "temperature",
                "value": 72,
                "confidence": 0.95,
                "response": "Setting temperature to 72 degrees"
            },
            "what's my engine temperature": {
                "intent": "vehicle_status",
                "action": "get", 
                "target": "engine_temperature",
                "confidence": 0.90,
                "response": "Engine temperature is 195 degrees Fahrenheit"
            },
            "turn up the volume": {
                "intent": "audio_control",
                "action": "increase",
                "target": "volume",
                "confidence": 0.92,
                "response": "Volume increased"
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize LLM controller."""
        try:
            self.logger.info("🧠 Initializing LLM Controller...")
            
            if not self.mock_mode:
                # Check if Ollama is running
                if await self._check_ollama_connection():
                    # Verify model is available
                    if await self._verify_model():
                        self.logger.info(f"✅ LLM ready with model: {self.model_name}")
                        return True
                    else:
                        self.logger.error("❌ Model not available, falling back to mock mode")
                        self.mock_mode = True
                else:
                    self.logger.warning("⚠️ Ollama not running, using mock mode")
                    self.mock_mode = True
            
            if self.mock_mode:
                self.logger.warning("🔧 Using mock LLM responses")
            
            return True
            
        except Exception as e:
            self.logger.error(f"LLM initialization error: {e}")
            return False
    
    async def _check_ollama_connection(self) -> bool:
        """Check if Ollama service is running."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_host}/api/tags", timeout=5) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def _verify_model(self) -> bool:
        """Verify the specified model is available."""
        try:
            if OLLAMA_AVAILABLE:
                models = ollama.list()
                model_names = [model['name'] for model in models['models']]
                return self.model_name in model_names
        except Exception as e:
            self.logger.error(f"Error checking models: {e}")
        return False
    
    async def process_command(self, 
                            user_input: str, 
                            vehicle_status: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """Process user command and return structured response."""
        start_time = time.time()
        
        try:
            if self.mock_mode:
                response = await self._process_mock_command(user_input)
            else:
                response = await self._process_ollama_command(user_input, vehicle_status)
            
            # Update conversation history
            self.conversation_manager.add_interaction(user_input, response.text)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=True)
            
            response.processing_time = processing_time
            
            self.logger.info(f"🧠 Processed command: '{user_input}' -> {response.intent.intent_type if response.intent else 'no intent'}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Command processing error: {e}")
            self._update_stats(time.time() - start_time, success=False)
            
            return LLMResponse(
                text="Sorry, I couldn't process that command. Please try again.",
                intent=None,
                confidence=0.0,
                processing_time=time.time() - start_time
            )
    
    async def _process_mock_command(self, user_input: str) -> LLMResponse:
        """Process command using mock responses."""
        # Simulate processing time
        await asyncio.sleep(0.2)
        
        # Find best matching mock response
        user_lower = user_input.lower()
        best_match = None
        best_score = 0
        
        for phrase, response_data in self.mock_responses.items():
            # Simple keyword matching
            keywords = phrase.split()
            score = sum(1 for keyword in keywords if keyword in user_lower)
            if score > best_score:
                best_score = score
                best_match = response_data
        
        if best_match and best_score > 0:
            intent = Intent(
                intent_type=IntentType(best_match["intent"]),
                confidence=best_match["confidence"],
                entities=[],
                raw_text=user_input,
                action=best_match["action"],
                target=best_match["target"],
                value=best_match.get("value")
            )
            
            return LLMResponse(
                text=best_match["response"],
                intent=intent,
                confidence=best_match["confidence"],
                processing_time=0.0,
                requires_confirmation=best_match.get("requires_confirmation", False),
                safety_warning=best_match.get("safety_warning")
            )
        else:
            return LLMResponse(
                text="I'm not sure what you want me to do. Could you please rephrase that?",
                intent=Intent(
                    intent_type=IntentType.UNKNOWN,
                    confidence=0.0,
                    entities=[],
                    raw_text=user_input,
                    action="unknown",
                    target="unknown"
                ),
                confidence=0.0,
                processing_time=0.0
            )
    
    async def _process_ollama_command(self, 
                                    user_input: str, 
                                    vehicle_status: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """Process command using Ollama LLM."""
        # Prepare context
        context = AutomotivePromptTemplate.CONTEXT_PROMPT.format(
            conversation_history=self.conversation_manager.get_context_string(),
            vehicle_status=json.dumps(vehicle_status or {}, indent=2),
            user_input=user_input
        )
        
        # Create full prompt
        messages = [
            {"role": "system", "content": AutomotivePromptTemplate.SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ]
        
        try:
            # Call Ollama API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 512
                    }
                )
            )
            
            # Parse LLM response
            llm_text = response['message']['content']
            
            # Try to parse as JSON
            try:
                parsed_response = json.loads(llm_text)
                return self._create_llm_response_from_json(parsed_response, user_input)
            except json.JSONDecodeError:
                # Fallback to text response
                return LLMResponse(
                    text=llm_text,
                    intent=self._extract_intent_from_text(user_input, llm_text),
                    confidence=0.7,
                    processing_time=0.0
                )
                
        except Exception as e:
            self.logger.error(f"Ollama processing error: {e}")
            raise
    
    def _create_llm_response_from_json(self, parsed_response: Dict[str, Any], user_input: str) -> LLMResponse:
        """Create LLMResponse from parsed JSON."""
        try:
            intent = Intent(
                intent_type=IntentType(parsed_response.get("intent", "unknown")),
                confidence=parsed_response.get("confidence", 0.0),
                entities=[],  # Would be populated in full implementation
                raw_text=user_input,
                action=parsed_response.get("action", "unknown"),
                target=parsed_response.get("target", "unknown"),
                value=parsed_response.get("value")
            )
            
            return LLMResponse(
                text=parsed_response.get("response", "Command processed"),
                intent=intent,
                confidence=parsed_response.get("confidence", 0.0),
                processing_time=0.0,
                requires_confirmation=parsed_response.get("requires_confirmation", False),
                safety_warning=parsed_response.get("safety_warning")
            )
            
        except Exception as e:
            self.logger.error(f"Error creating LLM response from JSON: {e}")
            raise
    
    def _extract_intent_from_text(self, user_input: str, llm_response: str) -> Intent:
        """Extract intent from text response (fallback method)."""
        # Simple keyword-based intent extraction
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["temperature", "heat", "cool", "ac", "air"]):
            intent_type = IntentType.CLIMATE_CONTROL
        elif any(word in user_lower for word in ["lights", "lighting", "dim", "bright"]):
            intent_type = IntentType.LIGHTING_CONTROL
        elif any(word in user_lower for word in ["volume", "music", "audio", "radio"]):
            intent_type = IntentType.AUDIO_CONTROL
        elif any(word in user_lower for word in ["engine", "boost", "rpm", "performance"]):
            intent_type = IntentType.ENGINE_MANAGEMENT
        elif any(word in user_lower for word in ["status", "check", "what", "how"]):
            intent_type = IntentType.VEHICLE_STATUS
        else:
            intent_type = IntentType.UNKNOWN
        
        return Intent(
            intent_type=intent_type,
            confidence=0.6,
            entities=[],
            raw_text=user_input,
            action="unknown",
            target="unknown"
        )
    
    def _update_stats(self, processing_time: float, success: bool) -> None:
        """Update processing statistics."""
        self.stats["requests_processed"] += 1
        
        if success:
            self.stats["successful_responses"] += 1
        else:
            self.stats["failed_responses"] += 1
        
        # Update average processing time
        total_requests = self.stats["requests_processed"]
        current_avg = self.stats["average_processing_time"]
        self.stats["average_processing_time"] = (
            (current_avg * (total_requests - 1) + processing_time) / total_requests
        )
    
    async def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        if not self.conversation_manager.conversation_history:
            return "No conversation history"
        
        # In a full implementation, this could use the LLM to summarize
        recent_interactions = self.conversation_manager.conversation_history[-3:]
        summary_parts = []
        
        for interaction in recent_interactions:
            summary_parts.append(f"User asked: {interaction['user']}")
        
        return "Recent requests: " + "; ".join(summary_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.stats.copy()
    
    async def shutdown(self) -> None:
        """Shutdown LLM controller."""
        self.logger.info("🛑 Shutting down LLM Controller...")
        self.conversation_manager.clear_context()
        self.logger.info("✅ LLM Controller shutdown complete")