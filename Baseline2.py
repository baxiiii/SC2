from enum import Enum, auto
from dataclasses import dataclass
import time

@dataclass
class GearConfiguration:
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

class LandingGearController:
    def __init__(self, config: GearConfiguration):
        self.state = GearState.UP_LOCKED
        self.config = config
        self.deployment_time_ms = 0

    def log(self, message):
        print(f"[{self.state.name}] {message}")

    def command_gear_down(self):
        if self.state != GearState.UP_LOCKED:
            self.log("Command rejected - invalid state")
            return False

        self.log("Command received: GEAR DOWN")
        self.state = GearState.TRANSITIONING_DOWN
        self.deployment_time_ms = 0

        # Pump
        time.sleep(self.config.pump_latency_ms / 1000)
        self.deployment_time_ms += self.config.pump_latency_ms
        self.log("Hydraulic pump active")

        # Actuator
        speed = self.config.actuator_speed_mm_per_100ms / 100.0
        extension_time = int(self.config.extension_distance_mm / speed)
        time.sleep(extension_time / 1000)
        self.deployment_time_ms += extension_time
        self.log("Actuator extending")

        # Lock
        time.sleep(self.config.lock_time_ms / 1000)
        self.deployment_time_ms += self.config.lock_time_ms
        self.log("Down-lock engaged")

        self.state = GearState.DOWN_LOCKED
        self.log(f"Gear locked DOWN ({self.deployment_time_ms}ms)")
        return True


# Demo
controller = LandingGearController(BASELINE_CONFIG)
controller.command_gear_down()
