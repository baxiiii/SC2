"""
BAE Systems Landing Gear Control System
Baseline v2.0 - IN PROGRESS
Date: xxxxx
Author: Ibrahim Bax

Description to be added
"""
from enum import Enum, auto
from dataclasses import dataclass

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

    def log(self, message):
        print(f"[{self.state.name}] {message}")

    def command_gear_down(self):
        if self.state != GearState.UP_LOCKED:
            self.log("Command rejected - invalid state")
            return False

        self.log("Command received: GEAR DOWN")
        self.state = GearState.TRANSITIONING_DOWN
        self.log("Gear deploying")

        self.state = GearState.DOWN_LOCKED
        self.log("Gear locked DOWN")
        return True

    def command_gear_up(self):
        if self.state != GearState.DOWN_LOCKED:
            self.log("Command rejected - invalid state")
            return False

        self.log("Command received: GEAR UP")
        self.state = GearState.TRANSITIONING_UP
        self.log("Gear retracting")

        self.state = GearState.UP_LOCKED
        self.log("Gear locked UP")
        return True

controller = LandingGearController()
controller.command_gear_down()
