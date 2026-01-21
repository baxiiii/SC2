"""
BAE Systems Landing Gear Control System
Baseline v1.0 - Initial Proof of Concept
Date: xxxxx
Author: Ibrahim Bax

Initial simple state machine demonstrating basic state transitions.
This proves the concept works before adding complexity.
"""
from enum import Enum, auto

class GearState(Enum):
    UP_LOCKED = auto()
    TRANSITIONING_DOWN = auto()
    DOWN_LOCKED = auto()
    TRANSITIONING_UP = auto()

class LandingGearController:
    def __init__(self):
        self.state = GearState.UP_LOCKED
    
    def log(self, message):
        print(f"[{self.state.name}] {message}")

    def command_gear_down(self):
        if self.state == GearState.UP_LOCKED:
            self.state = GearState.TRANSITIONING_DOWN
            self.log("Gear deploying")
            self.state = GearState.DOWN_LOCKED
            self.log("Gear locked down")
        else:
            self.log("Command rejected")

    def command_gear_up(self):
        if self.state == GearState.DOWN_LOCKED:
            self.state = GearState.TRANSITIONING_UP
            self.log("Gear Retracting")
            self.state = GearState.UP_LOCKED
            self.log("Gear locked up")
        else:
            self.log("Command rejected")

controller = LandingGearController()
controller.command_gear_down()
