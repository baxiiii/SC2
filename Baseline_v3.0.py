"""
BAE Systems Landing Gear Control System
Baseline v2.x - 
Date: xxxx
Author: Ibrahim Bax

"""

from enum import Enum, auto
from dataclasses import dataclass
import time

# LEGACY COMPONENT: Configuration from simulation baseline
@dataclass
class GearConfiguration:
    """Legacy configuration from approved simulation"""
    pump_latency_ms: int
    actuator_speed_mm_per_100ms: float
    extension_distance_mm: int
    lock_time_ms: int
    requirement_time_ms: int = 8000

# Approved baseline configuration
BASELINE_CONFIG = GearConfiguration(
    pump_latency_ms=200,
    actuator_speed_mm_per_100ms=10.0,
    extension_distance_mm=700,
    lock_time_ms=300,
    requirement_time_ms=8000
)

class GearState(Enum):
    UP_LOCKED = auto()
    TRANSITIONING_DOWN = auto()
    DOWN_LOCKED = auto()
    TRANSITIONING_UP = auto()
    FAILURE_DETECTED = auto()

class LandingGearController:
    def __init__(self, config: GearConfiguration):
        self.state = GearState.UP_LOCKED
        self.config = config
        self.deployment_time_ms = 0
        self.fault_detected = False 
    
    def log(self, message):
        print(f"[{self.state.name}] {message}")

    def command_gear_down(self):
        """Deploy landing gear with timing simulation"""
        if self.state != GearState.UP_LOCKED:
            self.log("Command rejected - invalid state")
            return False
        
        self.log("Command received: GEAR DOWN")
        self.deployment_time_ms = 0
        
        # Phase 1: Hydraulic pump activation
        self.state = GearState.TRANSITIONING_DOWN
        pump_time = self.config.pump_latency_ms
        self.log(f"Hydraulic pump activating ({pump_time}ms)")
        time.sleep(pump_time / 1000)
        self.deployment_time_ms += pump_time
        
        # Phase 2: Actuator extension
        speed = self.config.actuator_speed_mm_per_100ms / 100.0
        extension_time = int(self.config.extension_distance_mm / speed)
        self.log(f"Actuator extending ({extension_time}ms)")
        time.sleep(extension_time / 1000)
        self.deployment_time_ms += extension_time
        
        # Phase 3: Lock engagement
        lock_time = self.config.lock_time_ms
        self.log(f"Engaging down-lock ({lock_time}ms)")
        time.sleep(lock_time / 1000)
        self.deployment_time_ms += lock_time
        
        # Transition to locked
        self.state = GearState.DOWN_LOCKED
        self.log(f"Gear locked DOWN - Total: {self.deployment_time_ms}ms")
        
        # Basic requirement check (happens AFTER deployment)
        if self.deployment_time_ms > self.config.requirement_time_ms:
            self.log(f"WARNING: Deployment exceeded {self.config.requirement_time_ms}ms requirement")
            return False
        
        return True

    def command_gear_up(self):
        """Retract landing gear"""
        if self.state != GearState.DOWN_LOCKED:
            self.log("Command rejected - invalid state")
            return False
        
        self.log("Command received: GEAR UP")
        self.state = GearState.TRANSITIONING_UP
        self.log("Gear retracting")
        self.state = GearState.UP_LOCKED
        self.log("Gear locked UP")
        return True

# Demonstration
print("="*70)
print("BAE Systems Landing Gear - Baseline v2.0 ")
print("="*70)
print()

controller = LandingGearController(BASELINE_CONFIG)
success = controller.command_gear_down()

print()
print("--- Verification Summary ---")
print(f"Deployment Time: {controller.deployment_time_ms}ms ({controller.deployment_time_ms/1000:.2f}s)")
print(f"Requirement: {BASELINE_CONFIG.requirement_time_ms}ms ({BASELINE_CONFIG.requirement_time_ms/1000:.1f}s)")
if success:
    print("PASS: Within requirement")
else:
    print("FAIL: Exceeds requirement")
print()
