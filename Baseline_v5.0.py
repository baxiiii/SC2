"""
BAE Systems Landing Gear Control System
Baseline v5.0 - Automated Testing & Validation
Date:23/01/2025
Author: Ibrahim Bax

Additional Improvements from v4.0:
- Automated test suite for systematic verification
- Edge case testing (already deployed, invalid states, timing violations)
- Test result reporting
- Systematic validation approach

Rationale (QA Best Practice):
Professional aerospace software requires systematic testing.
v5.0 adds automated test cases to verify:
- Nominal deployment scenarios
- Edge cases and guard conditions
- Timing requirement validation
- State machine integrity
"""

from enum import Enum, auto
from dataclasses import dataclass
import time

# COMMERCIAL TOOL: matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# ============================================================
# LEGACY COMPONENT: Configuration from simulation baseline
# ============================================================

@dataclass
class GearConfiguration:
    """Legacy configuration from approved simulation"""
    pump_latency_ms: int
    actuator_speed_mm_per_100ms: float
    extension_distance_mm: int
    lock_time_ms: int
    requirement_time_ms: int = 8000


# Standard baseline configuration
BASELINE_CONFIG = GearConfiguration(
    pump_latency_ms=200,
    actuator_speed_mm_per_100ms=10.0,
    extension_distance_mm=700,
    lock_time_ms=300,
    requirement_time_ms=8000
)

# Edge case configuration (will exceed requirement)
SLOW_CONFIG = GearConfiguration(
    pump_latency_ms=500,
    actuator_speed_mm_per_100ms=5.0,
    extension_distance_mm=700,
    lock_time_ms=500,
    requirement_time_ms=8000
)

# ============================================================
# STATE MODEL
# ============================================================

class GearState(Enum):
    UP_LOCKED = auto()
    TRANSITIONING_DOWN = auto()
    DOWN_LOCKED = auto()
    TRANSITIONING_UP = auto()
    FAILURE_DETECTED = auto()

# ============================================================
# LANDING GEAR CONTROLLER
# ============================================================

class LandingGearController:
    def __init__(self, config: GearConfiguration):
        self.state = GearState.UP_LOCKED
        self.config = config
        self.deployment_time_ms = 0
        self.fault_detected = False
        self.timeline = []

    def log(self, message):
        print(f"[{self.state.name}] {message}")

    def _record_event(self, event: str):
        """Record timeline for audit trail"""
        self.timeline.append({
            "time_ms": self.deployment_time_ms,
            "state": self.state.name,
            "event": event
        })

    def _check_requirement(self):
        """Real-time requirement monitoring"""
        if self.deployment_time_ms > self.config.requirement_time_ms:
            self.log(
                f"⚠️  REQUIREMENT BREACH: "
                f"{self.deployment_time_ms}ms > {self.config.requirement_time_ms}ms"
            )
            self.state = GearState.FAILURE_DETECTED
            self.fault_detected = True
            self._record_event("Requirement breach detected")
            return False

        margin = self.config.requirement_time_ms - self.deployment_time_ms
        self.log(
            f"✓ Requirement check PASSED "
            f"({self.deployment_time_ms}ms / {self.config.requirement_time_ms}ms, "
            f"margin: {margin}ms)"
        )
        return True

    def command_gear_down(self):
        """Deploy landing gear with full monitoring"""
        if self.state == GearState.DOWN_LOCKED:
            self.log("Command rejected - gear already down")
            return False

        if self.state != GearState.UP_LOCKED:
            self.log("Command rejected - invalid state for deployment")
            return False

        self.log("Command received: GEAR DOWN")
        self.deployment_time_ms = 0
        self.fault_detected = False
        self.timeline = []
        self._record_event("Deployment command issued")

        # Phase 1: Hydraulic pump
        self.state = GearState.TRANSITIONING_DOWN
        pump_time = self.config.pump_latency_ms
        self.log(f"Hydraulic pump activating ({pump_time}ms)")
        time.sleep(pump_time / 1000)
        self.deployment_time_ms += pump_time
        self._record_event(f"Pump ready ({pump_time}ms)")

        if not self._check_requirement():
            return False

        # Phase 2: Actuator extension
        speed = self.config.actuator_speed_mm_per_100ms / 100.0
        extension_time = int(self.config.extension_distance_mm / speed)
        self.log(f"Actuator extending ({extension_time}ms)")
        time.sleep(extension_time / 1000)
        self.deployment_time_ms += extension_time
        self._record_event(f"Extension complete ({extension_time}ms)")

        if not self._check_requirement():
            return False

        # Phase 3: Lock engagement
        lock_time = self.config.lock_time_ms
        self.log(f"Engaging down-lock ({lock_time}ms)")
        time.sleep(lock_time / 1000)
        self.deployment_time_ms += lock_time
        self._record_event(f"Lock engaged ({lock_time}ms)")

        if not self._check_requirement():
            return False

        # Success
        self.state = GearState.DOWN_LOCKED
        margin = self.config.requirement_time_ms - self.deployment_time_ms
        self.log(
            f"✅ Deployment SUCCESSFUL - Total: "
            f"{self.deployment_time_ms}ms (Margin: {margin}ms)"
        )
        self._record_event("Deployment complete - SUCCESS")
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

# ============================================================
# NEW in v5.0: AUTOMATED TEST SUITE
# ============================================================

class TestResults:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []

    def record_test(self, name, passed, details=""):
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            self.tests_failed += 1
            status = "❌ FAIL"

        self.results.append({
            "name": name,
            "status": status,
            "passed": passed,
            "details": details
        })

        print(f"{status}: {name}")
        if details:
            print(f"         {details}")

    def print_summary(self):
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Tests Run: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Pass Rate: {(self.tests_passed / self.tests_run * 100):.1f}%\n")

# ============================================================
# TEST EXECUTION
# ============================================================

def run_automated_tests():
    """Automated test suite for systematic verification"""

    print("=" * 70)
    print("BAE Systems Landing Gear - Baseline v5.0")
    print("AUTOMATED TEST SUITE")
    print("=" * 70 + "\n")

    results = TestResults()

    # Test 1: Nominal deployment
    controller = LandingGearController(BASELINE_CONFIG)
    success = controller.command_gear_down()
    results.record_test(
        "Nominal deployment within requirement",
        success and controller.state == GearState.DOWN_LOCKED,
        f"Time: {controller.deployment_time_ms}ms"
    )

    # Test 2: Already deployed
    success2 = controller.command_gear_down()
    results.record_test(
        "Reject deployment when already deployed",
        not success2 and controller.state == GearState.DOWN_LOCKED
    )

    # Test 3: Retraction
    success3 = controller.command_gear_up()
    results.record_test(
        "Gear retraction functionality",
        success3 and controller.state == GearState.UP_LOCKED
    )

    # Test 4: Invalid retraction
    success4 = controller.command_gear_up()
    results.record_test(
        "Reject retraction when already retracted",
        not success4
    )

    # Test 5: Timing violation
    slow_controller = LandingGearController(SLOW_CONFIG)
    success5 = slow_controller.command_gear_down()
    results.record_test(
        "Detect timing requirement breach",
        not success5 and slow_controller.fault_detected
    )

    # Test 6: Timeline tracking
    test_controller = LandingGearController(BASELINE_CONFIG)
    test_controller.command_gear_down()
    results.record_test(
        "Timeline tracking completeness",
        len(test_controller.timeline) > 0
    )

    results.print_summary()
    return results


if __name__ == "__main__":
    test_results = run_automated_tests()
