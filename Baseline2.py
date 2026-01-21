"""
BAE Systems Landing Gear Control System
Baseline v2.0 - IN PROGRESS
Date: xxxxx
Author: Ibrahim Bax

Description to be added
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
        if self.state != GearState.UP_LOCKED:
            self.log("Command rejected - invalid state")
            return False

        self.log("Command received: GEAR DOWN")
        self.state = GearState.TRANSITIONING_DOWN
        self.log("Gear deploying")

        # Instant transition (no timing yet)
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
