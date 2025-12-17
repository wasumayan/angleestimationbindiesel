#!/usr/bin/env python3
"""
Generate diagrams for final report
Creates state machine, system block, and architecture diagrams
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np

def create_state_machine_diagram():
    """Create state machine diagram showing all states and transitions"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define states with positions
    states = {
        'IDLE': (2, 8),
        'FOLLOWING_USER': (5, 8),
        'TRACKING_USER': (5, 5),
        'STOPPED': (8, 5),
        'HOME': (2, 2),
    }
    
    # State colors
    state_colors = {
        'IDLE': '#FFE5B4',  # Light yellow
        'FOLLOWING_USER': '#B4E5FF',  # Light blue
        'TRACKING_USER': '#B4E5FF',
        'STOPPED': '#FFB4B4',  # Light red
        'HOME': '#B4FFB4',  # Light green
    }
    
    # Draw states
    state_patches = {}
    for state_name, (x, y) in states.items():
        # Create rounded rectangle for state
        box = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8,
                             boxstyle="round,pad=0.1",
                             facecolor=state_colors[state_name],
                             edgecolor='black',
                             linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, state_name, ha='center', va='center', 
                fontsize=10, fontweight='bold')
        state_patches[state_name] = (x, y)
    
    # Define transitions
    transitions = [
        ('IDLE', 'FOLLOWING_USER', 'Wake word\ndetected'),
        ('FOLLOWING_USER', 'TRACKING_USER', 'User lost'),
        ('TRACKING_USER', 'FOLLOWING_USER', 'Arm raised'),
        ('FOLLOWING_USER', 'STOPPED', 'TOF triggered'),
        ('STOPPED', 'HOME', 'Timeout'),
        ('HOME', 'IDLE', 'Marker reached'),
        ('FOLLOWING_USER', 'HOME', 'Emergency'),
    ]
    
    # Draw transitions
    for from_state, to_state, label in transitions:
        if from_state in state_patches and to_state in state_patches:
            x1, y1 = state_patches[from_state]
            x2, y2 = state_patches[to_state]
            
            # Calculate arrow position
            dx = x2 - x1
            dy = y2 - y1
            dist = np.sqrt(dx**2 + dy**2)
            
            # Start and end points (on edge of boxes)
            start_x = x1 + 0.8 * dx / dist if abs(dx) > 0.01 else x1
            start_y = y1 + 0.4 * dy / dist if abs(dy) > 0.01 else y1
            end_x = x2 - 0.8 * dx / dist if abs(dx) > 0.01 else x2
            end_y = y2 - 0.4 * dy / dist if abs(dy) > 0.01 else y2
            
            # Draw arrow
            arrow = FancyArrowPatch((start_x, start_y), (end_x, end_y),
                                   arrowstyle='->', mutation_scale=20,
                                   linewidth=1.5, color='black')
            ax.add_patch(arrow)
            
            # Add label
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            ax.text(mid_x, mid_y + 0.2, label, ha='center', va='bottom',
                   fontsize=8, bbox=dict(boxstyle='round,pad=0.3', 
                                        facecolor='white', alpha=0.8))
    
    ax.set_title('Bin Diesel State Machine', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('state_machine_diagram.png', dpi=300, bbox_inches='tight')
    print("State machine diagram saved to state_machine_diagram.png")
    plt.close()

def create_system_block_diagram():
    """Create system block diagram showing all components"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define component positions and colors
    components = {
        'Raspberry Pi': (6, 9, '#FFE5B4'),  # Yellow
        'Camera\n(PiCamera2)': (2, 7, '#FFE5B4'),
        'Microphone': (4, 7, '#FFE5B4'),
        'TOF Sensor\n(VL53L0X)': (8, 7, '#FFB4B4'),  # Red
        'Motor Controller\n(PWM)': (2, 4, '#FFB4B4'),
        'Servo Controller\n(PWM)': (4, 4, '#FFB4B4'),
        'Wake Word\nDetector': (6, 5.5, '#FFE5B4'),
        'YOLO Pose\nTracker': (8, 5.5, '#FFE5B4'),
        'ArUco Detector': (10, 5.5, '#FFE5B4'),
        'State Machine': (6, 3, '#B4E5FF'),  # Blue
    }
    
    # Draw components
    for name, (x, y, color) in components.items():
        box = FancyBboxPatch((x-0.9, y-0.5), 1.8, 1.0,
                             boxstyle="round,pad=0.1",
                             facecolor=color,
                             edgecolor='black',
                             linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center',
                fontsize=9, fontweight='bold', wrap=True)
    
    # Draw connections
    connections = [
        ((2, 7), (6, 9), 'Video'),  # Camera to Pi
        ((4, 7), (6, 9), 'Audio'),  # Mic to Pi
        ((8, 7), (6, 9), 'I2C'),  # TOF to Pi
        ((6, 9), (6, 5.5), 'Processing'),  # Pi to Wake Word
        ((6, 9), (8, 5.5), 'Processing'),  # Pi to YOLO
        ((6, 9), (10, 5.5), 'Processing'),  # Pi to ArUco
        ((6, 9), (6, 3), 'Control'),  # Pi to State Machine
        ((6, 3), (2, 4), 'PWM'),  # State Machine to Motor
        ((6, 3), (4, 4), 'PWM'),  # State Machine to Servo
    ]
    
    for (x1, y1), (x2, y2), label in connections:
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='->', mutation_scale=15,
                               linewidth=1.5, color='gray', alpha=0.7)
        ax.add_patch(arrow)
        # Add label
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(mid_x, mid_y + 0.15, label, ha='center', va='bottom',
               fontsize=7, color='gray')
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor='#FFE5B4', label='Perception/Input'),
        mpatches.Patch(facecolor='#FFB4B4', label='Hardware Control'),
        mpatches.Patch(facecolor='#B4E5FF', label='Computation'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    ax.set_title('Bin Diesel System Block Diagram', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('system_block_diagram.png', dpi=300, bbox_inches='tight')
    print("System block diagram saved to system_block_diagram.png")
    plt.close()

def create_codebase_architecture_diagram():
    """Create codebase architecture diagram with color coding"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Color scheme matching report
    colors = {
        'main': '#FFE5B4',  # Yellow
        'perception': '#FFD700',  # Gold/Yellow
        'hardware': '#FF6B6B',  # Red
        'computation': '#4ECDC4',  # Blue
        'config': '#95E1D3',  # Green
    }
    
    # Main control system (YELLOW)
    main_box = FancyBboxPatch((1, 7), 3, 1.5,
                             boxstyle="round,pad=0.1",
                             facecolor=colors['main'],
                             edgecolor='black',
                             linewidth=3)
    ax.add_patch(main_box)
    ax.text(2.5, 8, 'Main Control System\n(main_control_system.py)', 
           ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Perception modules (YELLOW/ORANGE)
    perception_modules = [
        ('Wake Word\nDetector', 6, 8.5),
        ('YOLO Pose\nTracker', 8.5, 8.5),
        ('ArUco\nDetector', 10.5, 8.5),
    ]
    for name, x, y in perception_modules:
        box = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8,
                             boxstyle="round,pad=0.1",
                             facecolor=colors['perception'],
                             edgecolor='black',
                             linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Hardware controllers (RED)
    hardware_modules = [
        ('Motor\nController', 2, 5),
        ('Servo\nController', 4, 5),
        ('TOF Sensor', 6, 5),
    ]
    for name, x, y in hardware_modules:
        box = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8,
                             boxstyle="round,pad=0.1",
                             facecolor=colors['hardware'],
                             edgecolor='black',
                             linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Computation modules (BLUE)
    computation_modules = [
        ('State\nMachine', 8.5, 5),
        ('Optimizations', 10.5, 5),
    ]
    for name, x, y in computation_modules:
        box = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8,
                             boxstyle="round,pad=0.1",
                             facecolor=colors['computation'],
                             edgecolor='black',
                             linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Configuration (GREEN)
    config_box = FancyBboxPatch((2, 2), 2, 0.8,
                                boxstyle="round,pad=0.1",
                                facecolor=colors['config'],
                                edgecolor='black',
                                linewidth=2)
    ax.add_patch(config_box)
    ax.text(3, 2.4, 'Configuration\n(config.py)', 
           ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Draw connections
    connections = [
        ((2.5, 7), (6, 8.5), ''),  # Main to Wake Word
        ((2.5, 7), (8.5, 8.5), ''),  # Main to YOLO
        ((2.5, 7), (10.5, 8.5), ''),  # Main to ArUco
        ((2.5, 7), (2, 5), ''),  # Main to Motor
        ((2.5, 7), (4, 5), ''),  # Main to Servo
        ((2.5, 7), (6, 5), ''),  # Main to TOF
        ((2.5, 7), (8.5, 5), ''),  # Main to State Machine
        ((3, 2.8), (2.5, 7), ''),  # Config to Main
    ]
    
    for (x1, y1), (x2, y2), label in connections:
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='->', mutation_scale=12,
                               linewidth=1, color='gray', alpha=0.5)
        ax.add_patch(arrow)
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=colors['main'], label='Main Control (Yellow)'),
        mpatches.Patch(facecolor=colors['perception'], label='Perception Modules (Yellow/Orange)'),
        mpatches.Patch(facecolor=colors['hardware'], label='Hardware Controllers (Red)'),
        mpatches.Patch(facecolor=colors['computation'], label='Computation (Blue)'),
        mpatches.Patch(facecolor=colors['config'], label='Configuration (Green)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
    ax.set_title('Codebase Architecture (Color Coded)', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('codebase_architecture_diagram.png', dpi=300, bbox_inches='tight')
    print("Codebase architecture diagram saved to codebase_architecture_diagram.png")
    plt.close()

if __name__ == '__main__':
    print("Generating diagrams...")
    create_state_machine_diagram()
    create_system_block_diagram()
    create_codebase_architecture_diagram()
    print("All diagrams generated successfully!")

