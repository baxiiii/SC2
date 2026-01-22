"""
BAE Systems Landing Gear Control System
Baseline v3.0 -
Date: xxxx
Author: Ibrahim Bax

QA-Driven Improvements from v2.0:
- Real-time requirement monitoring (Lean: early defect detection)
- Continuous validation during deployment phases
- Enhanced edge case handling
- Improved fault detection and state management

Rationale (PDCA CHECK Phase):
v2.0 review identified that requirement checking only occurred
AFTER deployment completed. This violated Lean principle of
detecting defects as early as possible. v3.0 implements continuous
monitoring to detect timing violations immediately.
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
    
    def _check_requirement(self):
        """
        NEW in v3.0: Real-time requirement monitoring.
        Implements Lean principle: detect problems early.
        """
        if self.deployment_time_ms > self.config.requirement_time_ms:
            self.log(f"REQUIREMENT BREACH: {self.deployment_time_ms}ms > {self.config.requirement_time_ms}ms")
            self.state = GearState.FAILURE_DETECTED
            self.fault_detected = True
            return False
        
        # Log progress
        margin = self.config.requirement_time_ms - self.deployment_time_ms
        self.log(f"✓ Requirement check PASSED ({self.deployment_time_ms}ms / {self.config.requirement_time_ms}ms, margin: {margin}ms)")
        return True

    def command_gear_down(self):
        """Deploy landing gear with continuous monitoring"""
        # Edge case: Already deployed
        if self.state == GearState.DOWN_LOCKED:
            self.log("Command rejected - gear already down")
            return False
        
        # Edge case: Invalid state
        if self.state not in [GearState.UP_LOCKED]:
            self.log("Command rejected - invalid state for deployment")
            return False
        
        self.log("Command received: GEAR DOWN")
        self.deployment_time_ms = 0
        self.fault_detected = False
        
        # Phase 1: Hydraulic pump activation
        self.state = GearState.TRANSITIONING_DOWN
        pump_time = self.config.pump_latency_ms
        self.log(f"Hydraulic pump activating ({pump_time}ms)")
        time.sleep(pump_time / 1000)
        self.deployment_time_ms += pump_time
        
        # NEW: Check requirement after pump phase
        if not self._check_requirement():
            return False
        
        # Phase 2: Actuator extension
        speed = self.config.actuator_speed_mm_per_100ms / 100.0
        extension_time = int(self.config.extension_distance_mm / speed)
        self.log(f"Actuator extending ({extension_time}ms)")
        time.sleep(extension_time / 1000)
        self.deployment_time_ms += extension_time
        
        # NEW: Check requirement after extension
        if not self._check_requirement():
            return False
        
        # Phase 3: Lock engagement
        lock_time = self.config.lock_time_ms
        self.log(f"Engaging down-lock ({lock_time}ms)")
        time.sleep(lock_time / 1000)
        self.deployment_time_ms += lock_time
        
        # NEW: Final requirement check
        if not self._check_requirement():
            return False
        
        # Success - transition to locked
        self.state = GearState.DOWN_LOCKED
        margin = self.config.requirement_time_ms - self.deployment_time_ms
        self.log(f"Deployment SUCCESSFUL - Total: {self.deployment_time_ms}ms (Margin: {margin}ms)")
        
        return True

    def command_gear_up(self):
        """Retract landing gear"""
        if self.state != GearState.DOWN_LOCKED:
            self.log("Command rejected - invalid state for retraction")
            return False
        
        self.log("Command received: GEAR UP")
        self.state = GearState.TRANSITIONING_UP
        self.log("Gear retracting")
        self.state = GearState.UP_LOCKED
        self.log("Gear locked UP")
        return True

# QA Improvement Demonstration
print("="*70)
print("BAE Systems Landing Gear - Baseline v3.0 (QA Improvement)")
print("Real-Time Monitoring Implementation")
print("="*70)
print()

controller = LandingGearController(BASELINE_CONFIG)
success = controller.command_gear_down()

print()
print("="*70)
print("VERIFICATION REPORT")
print("="*70)
print(f"Final State: {controller.state.name}")
print(f"Deployment Time: {controller.deployment_time_ms}ms ({controller.deployment_time_ms/1000:.2f}s)")
print(f"Requirement: {BASELINE_CONFIG.requirement_time_ms}ms ({BASELINE_CONFIG.requirement_time_ms/1000:.1f}s)")

if success and not controller.fault_detected:
    margin = BASELINE_CONFIG.requirement_time_ms - controller.deployment_time_ms
    print(f"Margin: {margin}ms")
    print()
    print("DEPLOYMENT SUCCESSFUL")
    print("   - All phases completed within requirement")
    print("   - Continuous monitoring confirmed compliance")
    print("   - No faults detected")
else:
    print()
    print("DEPLOYMENT FAILED")
    print("   - Requirement breach detected during deployment")
    print("   - System entered FAILURE_DETECTED state")
    print("   - Manual intervention required")
print()