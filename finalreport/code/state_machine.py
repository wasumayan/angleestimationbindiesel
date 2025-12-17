"""
State Machine Module
Manages system states and transitions for Bin Diesel workflow

DESIGN OVERVIEW:
This module implements a finite state machine (FSM) to manage the robot's operational states.
The state machine ensures proper sequencing of operations and prevents invalid state transitions.

KEY STATES:
- IDLE: Waiting for wake word, no movement
- TRACKING_USER: Detecting and tracking user (no movement)
- FOLLOWING_USER: Actively following user with adaptive speed control
- STOPPED: At target distance, waiting for trash collection
- HOME: Returning to home marker using ArUco detection

STATE TRANSITIONS:
IDLE -> FOLLOWING_USER: Wake word detected
FOLLOWING_USER -> TRACKING_USER: User lost (search mode)
TRACKING_USER -> FOLLOWING_USER: User found with arm raised
FOLLOWING_USER -> STOPPED: TOF sensor triggered (emergency stop)
STOPPED -> HOME: Timeout (trash collection complete)
HOME -> IDLE: ArUco marker reached

DESIGN DECISIONS:
1. State-based architecture: Ensures clear separation of concerns
2. Timeout tracking: Prevents infinite waiting in states
3. State entry time tracking: Enables timeout-based transitions
"""

import time
from enum import Enum, auto
import config


class State(Enum):
    """System states"""
    IDLE = auto()  # Wake word only - no voice recognizer (exclusive mic access)
    ACTIVE = auto()  # Post-wake-word: voice commands and visual detection for mode selection
    TRACKING_USER = auto()
    FOLLOWING_USER = auto()
    FINDING_LOST_USER = auto()  # User lost during following - searching with pose detection
    STOPPED = auto()  # At target distance, waiting for trash collection
    HOME = auto()  # Returning to home marker (turn 180, detect marker, drive to it)
    MANUAL_MODE = auto()
    RADD_MODE = auto()  # Drive towards users not wearing full pants or closed-toe shoes
    # Legacy states (for compatibility)
    DORMANT = auto()  # Deprecated - use IDLE instead
    RETURNING_TO_START = auto()  # Deprecated - use HOME instead
    DRIVING_TO_USER = auto()
    STOPPED_AT_USER = auto()
    RETURNING = auto()


class StateMachine:
    """
    State Machine for Bin Diesel system
    
    Manages state transitions and tracks time in each state.
    Provides timeout functionality to prevent infinite waiting.
    """
    def __init__(self, tracking_timeout=30.0):
        """
        Initialize state machine
        
        Args:
            tracking_timeout: Maximum time (seconds) to wait in tracking states
                            before transitioning to IDLE (prevents infinite waiting)
        """
        self.state = State.IDLE  # Start in IDLE state (waiting for wake word)
        self.old_state = None  # Track previous state for transition logging
        self.state_enter_time = time.time()  # Track when current state was entered
        self.tracking_timeout = tracking_timeout  # Timeout for tracking states (30 seconds)

        self.forward_start_time = None
        self.forward_elapsed_time = 0.0 

        if config.DEBUG_STATE:
            print(f"[SM] initial state: {self.state.name}")
    

    def get_state(self):
        return self.state
    
    def get_old_state(self): 
        return self.old_state
    
    def get_time_in_state(self):
        return time.time() - self.state_enter_time
    
    
    def transition_to(self, new_state: State):
        """
        Transition to a new state
        
        Args:
            new_state: Target state to transition to
            
        DESIGN: State transition tracking
        - Stores old state for logging and debugging
        - Resets state entry time for timeout calculations
        - Enables state-specific behavior in main control loop
        """
        if config.DEBUG_STATE:
            print(f"[SM] {self.state.name} -> {new_state.name}")
       
        self.old_state = self.state  # Store previous state
        self.state = new_state  # Update current state
        self.state_enter_time = time.time()  # Reset entry time for timeout tracking
    
    def is_timeout(self):
        """Check if tracking timeout has been exceeded"""
        return self.get_time_in_state() > self.tracking_timeout
    
    def set_start_position(self, position):
        self.start_position = position
        print(f"[StateMachine] Start position set: {position}")
    
    def get_start_position(self):
        return getattr(self, 'start_position', None)


if __name__ == '__main__':
    print("Testing state machine...")

    sm = StateMachine()

    print(f"Current state: {sm.get_state().name}")
    time.sleep(0.5)

    sm.transition_to(State.DRIVING_TO_USER)
    time.sleep(0.5)
    print(f"State: {sm.get_state().name}, time in state: {sm.get_time_in_state():.2f}s")

    sm.transition_to(State.STOPPED_AT_USER)
    time.sleep(0.5)
    print(f"State: {sm.get_state().name}, time in state: {sm.get_time_in_state():.2f}s")

    print("State machine test complete!")

