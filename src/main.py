#!/usr/bin/env python3
"""
Automotive LLM System - Main Entry Point
Local AI assistant for classic cars with voice control and vehicle integration.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

from controllers.system_controller import SystemController
from config.settings import Settings
from safety.monitor import SafetyMonitor


class AutomotiveLLMSystem:
    """Main system coordinator for the Automotive LLM Assistant."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.settings = Settings(config_path)
        self.logger = self._setup_logging()
        self.system_controller: Optional[SystemController] = None
        self.safety_monitor: Optional[SafetyMonitor] = None
        self.running = False
        
    def _setup_logging(self) -> logging.Logger:
        """Configure system logging."""
        log_level = getattr(logging, self.settings.log_level.upper())
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.settings.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        return logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize all system components."""
        try:
            self.logger.info("🚗 Initializing Automotive LLM System...")
            
            # Initialize safety monitor first
            self.safety_monitor = SafetyMonitor(self.settings)
            await self.safety_monitor.initialize()
            
            # Initialize main system controller
            self.system_controller = SystemController(
                settings=self.settings,
                safety_monitor=self.safety_monitor
            )
            
            initialization_success = await self.system_controller.initialize()
            
            if initialization_success:
                self.logger.info("✅ System initialization complete")
                return True
            else:
                self.logger.error("❌ System initialization failed")
                return False
                
        except Exception as e:
            self.logger.error(f"💥 Initialization error: {e}")
            return False
    
    async def start(self) -> None:
        """Start the automotive LLM system."""
        if not await self.initialize():
            self.logger.error("Failed to initialize system. Exiting.")
            sys.exit(1)
        
        self.running = True
        self.logger.info("🎤 Automotive LLM System started - Listening for commands...")
        
        try:
            # Setup signal handlers for graceful shutdown
            for sig in [signal.SIGINT, signal.SIGTERM]:
                signal.signal(sig, self._signal_handler)
            
            # Start main system loop
            await self.system_controller.start()
            
            # Keep running until shutdown signal
            while self.running:
                await asyncio.sleep(1.0)
                
                # Periodic health checks
                if not await self.safety_monitor.health_check():
                    self.logger.warning("⚠️ Safety monitor health check failed")
                    await self._emergency_shutdown()
                    break
                    
        except Exception as e:
            self.logger.error(f"💥 Runtime error: {e}")
            await self._emergency_shutdown()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"📡 Received signal {signum}, initiating graceful shutdown...")
        self.running = False
    
    async def shutdown(self) -> None:
        """Graceful system shutdown."""
        self.logger.info("🛑 Shutting down Automotive LLM System...")
        self.running = False
        
        if self.system_controller:
            await self.system_controller.shutdown()
        
        if self.safety_monitor:
            await self.safety_monitor.shutdown()
        
        self.logger.info("✅ System shutdown complete")
    
    async def _emergency_shutdown(self) -> None:
        """Emergency shutdown with safety protocols."""
        self.logger.critical("🚨 EMERGENCY SHUTDOWN INITIATED")
        
        if self.safety_monitor:
            await self.safety_monitor.emergency_protocol()
        
        await self.shutdown()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automotive LLM System")
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to configuration file",
        default=None
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Override log level if debug flag is set
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run the system
    system = AutomotiveLLMSystem(config_path=args.config)
    
    try:
        asyncio.run(system.start())
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()