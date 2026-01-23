"""
BAE Systems Landing Gear Control System
Baseline v4.0 
Date: 
Author: Ibrahim bax


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
    print("Note: matplotlib not available - visualization disabled")

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
        self.timeline = []  # NEW in v4.0: Event timeline tracking
    
    def log(self, message):
        print(f"[{self.state.name}] {message}")
    
    def _record_event(self, event: str):
        """NEW in v4.0: Record timeline for audit trail"""
        self.timeline.append({
            'time_ms': self.deployment_time_ms,
            'state': self.state.name,
            'event': event
        })
    
    def _check_requirement(self):
        """Real-time requirement monitoring (from v3.0)"""
        if self.deployment_time_ms > self.config.requirement_time_ms:
            self.log(f"REQUIREMENT BREACH: {self.deployment_time_ms}ms > {self.config.requirement_time_ms}ms")
            self.state = GearState.FAILURE_DETECTED
            self.fault_detected = True
            self._record_event("Requirement breach detected")
            return False
        
        margin = self.config.requirement_time_ms - self.deployment_time_ms
        self.log(f"✓ Requirement check PASSED ({self.deployment_time_ms}ms / {self.config.requirement_time_ms}ms, margin: {margin}ms)")
        return True

    def command_gear_down(self):
        """Deploy landing gear with full monitoring and tracking"""
        # Edge case handling
        if self.state == GearState.DOWN_LOCKED:
            self.log("Command rejected - gear already down")
            return False
        
        if self.state not in [GearState.UP_LOCKED]:
            self.log("Command rejected - invalid state for deployment")
            return False
        
        self.log("Command received: GEAR DOWN")
        self.deployment_time_ms = 0
        self.fault_detected = False
        self.timeline = []  # Reset timeline
        self._record_event("Deployment command issued")
        
        # Phase 1: Hydraulic pump activation
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
        self.log(f"Deployment SUCCESSFUL - Total: {self.deployment_time_ms}ms (Margin: {margin}ms)")
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
    
    def generate_timeline_visualization(self):
        """
        NEW in v4.0: Visual verification output
        Implements Kaizen: improve observability and verification
        """
        if not VISUALIZATION_AVAILABLE:
            print("Visualization not available - skipping chart generation")
            return
        
        if not self.timeline:
            print("No timeline data available")
            return
        
        times = [entry['time_ms'] for entry in self.timeline]
        events = [entry['event'] for entry in self.timeline]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(times, range(len(times)), 'bo-', linewidth=2, markersize=10)
        
        # Highlight requirement boundary
        ax.axvline(x=self.config.requirement_time_ms, color='red', 
                   linestyle='--', linewidth=2, label=f'Requirement ({self.config.requirement_time_ms}ms)')
        
        # Add event labels
        for i, (t, event) in enumerate(zip(times, events)):
            ax.annotate(event, (t, i), xytext=(10, 0), 
                       textcoords='offset points', fontsize=9, 
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        ax.set_xlabel('Time (milliseconds)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Event Sequence', fontsize=12, fontweight='bold')
        ax.set_title('Landing Gear Deployment Timeline - Baseline v4.0', 
                     fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('deployment_timeline_v4.png', dpi=150, bbox_inches='tight')
        print("\n✓ Timeline visualization saved to 'deployment_timeline_v4.png'")
        plt.show()

# Final Demonstration
print("="*70)
print("BAE Systems Landing Gear - Baseline v4.0 (Week 7 Final)")
print("Enhanced Verification with Visualization")
print("="*70)
print()

controller = LandingGearController(BASELINE_CONFIG)
success = controller.command_gear_down()

print()
print("="*70)
print("COMPREHENSIVE VERIFICATION REPORT")
print("="*70)
print(f"Final State: {controller.state.name}")
print(f"Deployment Time: {controller.deployment_time_ms}ms ({controller.deployment_time_ms/1000:.2f}s)")
print(f"Requirement: {BASELINE_CONFIG.requirement_time_ms}ms ({BASELINE_CONFIG.requirement_time_ms/1000:.1f}s)")

if success and not controller.fault_detected:
    margin = BASELINE_CONFIG.requirement_time_ms - controller.deployment_time_ms
    print(f"Margin: {margin}ms ({(margin/BASELINE_CONFIG.requirement_time_ms)*100:.1f}% safety buffer)")
    print()
    print("DEPLOYMENT SUCCESSFUL")
    print("   - All phases completed within requirement")
    print("   - Continuous monitoring confirmed compliance")
    print("   - Complete audit trail available")
    print("   - Visual verification generated")
else:
    print()
    print("DEPLOYMENT FAILED")
    print("   - Requirement breach detected")
    print("   - System entered FAILURE_DETECTED state")

print()
print("--- Event Timeline (Audit Trail) ---")
for entry in controller.timeline:
    print(f"  t={entry['time_ms']:5d}ms  [{entry['state']:20s}]  {entry['event']}")

print()
print("--- Generating Visual Verification ---")
controller.generate_timeline_visualization()
print()