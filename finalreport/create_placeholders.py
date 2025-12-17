#!/usr/bin/env python3
"""
Create placeholder images for missing figures
These will allow the LaTeX to compile without errors
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch
import numpy as np

def create_physical_layout_placeholder():
    """Create placeholder for physical layout diagram"""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Draw car outline
    car = FancyBboxPatch((2, 3), 6, 4, boxstyle="round,pad=0.2",
                        facecolor='lightgray', edgecolor='black', linewidth=2)
    ax.add_patch(car)
    
    # Components
    components = [
        ('Raspberry Pi', 5, 6, 'blue'),
        ('Camera', 7, 7, 'red'),
        ('Motor', 3, 4, 'green'),
        ('Servo', 4, 4, 'orange'),
        ('TOF Sensor', 6, 7.5, 'purple'),
    ]
    
    for name, x, y, color in components:
        circle = Circle((x, y), 0.3, facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(circle)
        ax.text(x, y-0.6, name, ha='center', va='top', fontsize=9, fontweight='bold')
    
    ax.text(5, 9, 'Physical Layout of Bin Diesel System', 
           ha='center', fontsize=14, fontweight='bold')
    ax.text(5, 0.5, 'PLACEHOLDER: Replace with actual CAD/physical layout diagram',
           ha='center', fontsize=10, style='italic', color='red')
    
    plt.tight_layout()
    plt.savefig('diagrams/car_layout_overview.png', dpi=150, bbox_inches='tight')
    print("Created: diagrams/car_layout_overview.png")
    plt.close()

def create_buck_converter_placeholder():
    """Create placeholder for buck converter photo"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Draw buck converter representation
    converter = FancyBboxPatch((2, 2), 6, 4, boxstyle="round,pad=0.3",
                               facecolor='#E8E8E8', edgecolor='black', linewidth=3)
    ax.add_patch(converter)
    
    # Input/output labels
    ax.text(1, 4, 'Battery\n(7-12V)', ha='center', va='center', 
           fontsize=10, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    ax.text(9, 4, 'Raspberry Pi\n(5V)', ha='center', va='center',
           fontsize=10, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    # Arrow
    arrow1 = FancyArrowPatch((1.5, 4), (2.5, 4), arrowstyle='->', 
                            mutation_scale=20, linewidth=2, color='black')
    arrow2 = FancyArrowPatch((7.5, 4), (8.5, 4), arrowstyle='->',
                            mutation_scale=20, linewidth=2, color='black')
    ax.add_patch(arrow1)
    ax.add_patch(arrow2)
    
    ax.text(5, 5.5, 'Buck Converter', ha='center', fontsize=16, fontweight='bold')
    ax.text(5, 4.5, 'Voltage Regulation', ha='center', fontsize=12)
    ax.text(5, 0.5, 'PLACEHOLDER: Replace with actual buck converter photo',
           ha='center', fontsize=10, style='italic', color='red')
    
    plt.tight_layout()
    plt.savefig('hardware/buck_converter.jpg', dpi=150, bbox_inches='tight')
    print("Created: hardware/buck_converter.jpg")
    plt.close()

def create_motor_inverter_circuit_placeholder():
    """Create placeholder for motor inverter circuit diagram"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Raspberry Pi GPIO
    pi_box = FancyBboxPatch((1, 6), 2, 1.5, boxstyle="round,pad=0.1",
                           facecolor='lightblue', edgecolor='black', linewidth=2)
    ax.add_patch(pi_box)
    ax.text(2, 6.75, 'Raspberry Pi\nGPIO 12', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # PWM signal line
    ax.plot([3.5, 4.5], [6.75, 6.75], 'k-', linewidth=2)
    ax.text(4, 7.2, 'PWM Signal\n(40Hz)', ha='center', fontsize=8)
    
    # Resistor
    resistor = Rectangle((5, 6.3), 1, 0.9, facecolor='brown', edgecolor='black', linewidth=1)
    ax.add_patch(resistor)
    ax.text(5.5, 6.75, 'R', ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    # Capacitor
    cap1 = Rectangle((7, 6.5), 0.3, 0.5, facecolor='gray', edgecolor='black', linewidth=1)
    cap2 = Rectangle((7.3, 6.3), 0.3, 0.9, facecolor='gray', edgecolor='black', linewidth=1)
    ax.add_patch(cap1)
    ax.add_patch(cap2)
    ax.text(7.5, 6.75, 'C', ha='left', va='center', fontsize=10, fontweight='bold')
    
    # Inverter circuit box
    inverter = FancyBboxPatch((9, 5.5), 2, 2.5, boxstyle="round,pad=0.2",
                             facecolor='lightyellow', edgecolor='black', linewidth=2)
    ax.add_patch(inverter)
    ax.text(10, 6.75, 'Inverter\nCircuit', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Motor
    motor = Circle((10, 3), 0.8, facecolor='lightgreen', edgecolor='black', linewidth=2)
    ax.add_patch(motor)
    ax.text(10, 3, 'Motor', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Connections
    ax.plot([3.5, 5], [6.75, 6.75], 'k-', linewidth=2)
    ax.plot([6, 7], [6.75, 6.75], 'k-', linewidth=2)
    ax.plot([7.6, 9], [6.75, 6.75], 'k-', linewidth=2)
    ax.plot([10, 10], [5.5, 3.8], 'k-', linewidth=2)
    
    # Labels
    ax.text(6, 5.5, 'Resistor: Current Limiting', ha='center', fontsize=9, 
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    ax.text(7.5, 5.5, 'Capacitor: Filtering', ha='center', fontsize=9,
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    ax.text(6, 1, 'Motor Inverter Circuit Diagram', ha='center', fontsize=14, fontweight='bold')
    ax.text(6, 0.3, 'PLACEHOLDER: Replace with actual circuit diagram (KiCad/CircuitLab)',
           ha='center', fontsize=10, style='italic', color='red')
    
    plt.tight_layout()
    plt.savefig('hardware/motor_inverter_circuit.png', dpi=150, bbox_inches='tight')
    print("Created: hardware/motor_inverter_circuit.png")
    plt.close()

def create_cad_drawing_placeholder():
    """Create placeholder for CAD drawing"""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Draw chassis outline
    chassis = FancyBboxPatch((2, 2), 8, 6, boxstyle="round,pad=0.3",
                            facecolor='#F0F0F0', edgecolor='black', linewidth=3)
    ax.add_patch(chassis)
    
    # Component positions with annotations
    components = [
        ('Raspberry Pi', 4, 6, 'blue', 0.5),
        ('Camera\nModule', 7, 7.5, 'red', 0.4),
        ('Motor', 3, 3.5, 'green', 0.4),
        ('Servo', 5, 3.5, 'orange', 0.4),
        ('TOF\nSensor', 8, 7, 'purple', 0.35),
        ('Battery', 9, 4, 'yellow', 0.4),
    ]
    
    for name, x, y, color, size in components:
        circle = Circle((x, y), size, facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        ax.text(x, y, name, ha='center', va='center', fontsize=8, fontweight='bold')
        # Dimension line
        ax.plot([x+size+0.2, x+size+0.5], [y, y], 'k--', linewidth=1, alpha=0.5)
        ax.text(x+size+0.7, y, f'{size*20:.0f}mm', ha='left', va='center', fontsize=7)
    
    # Mounting points
    for x, y in [(2.5, 2.5), (9.5, 2.5), (2.5, 7.5), (9.5, 7.5)]:
        mount = Circle((x, y), 0.15, facecolor='black', edgecolor='black')
        ax.add_patch(mount)
    
    ax.text(6, 9, 'CAD Rendering of Bin Diesel Chassis', ha='center', 
           fontsize=16, fontweight='bold')
    ax.text(6, 8.3, 'Component Layout and Dimensions', ha='center', fontsize=12)
    ax.text(6, 0.5, 'PLACEHOLDER: Replace with actual CAD drawing export',
           ha='center', fontsize=10, style='italic', color='red')
    
    # Add grid for CAD-like appearance
    for i in range(13):
        ax.axvline(i, color='lightgray', linewidth=0.5, alpha=0.3, linestyle='--')
    for i in range(11):
        ax.axhline(i, color='lightgray', linewidth=0.5, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('hardware/cad_drawing.png', dpi=150, bbox_inches='tight')
    print("Created: hardware/cad_drawing.png")
    plt.close()

def create_pose_detection_placeholder():
    """Create placeholder for pose detection screenshot"""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Simulate video frame
    frame = Rectangle((1, 2), 8, 5, facecolor='#2C2C2C', edgecolor='white', linewidth=2)
    ax.add_patch(frame)
    
    # Simulate person detection
    person_box = Rectangle((3, 3), 4, 3, facecolor='none', edgecolor='green', linewidth=2, linestyle='--')
    ax.add_patch(person_box)
    
    # Keypoints
    keypoints = [
        (4, 5, 'nose'),
        (4.5, 4.5, 'shoulder'),
        (5, 4, 'elbow'),
        (5.5, 3.5, 'wrist'),
    ]
    
    for x, y, name in keypoints:
        circle = Circle((x, y), 0.15, facecolor='red', edgecolor='white', linewidth=1)
        ax.add_patch(circle)
        ax.text(x+0.3, y, name, ha='left', va='center', fontsize=7, color='white')
    
    # Command line output simulation
    output_y = 1.5
    outputs = [
        'Person detected: Track ID 1',
        'Angle: 15.3°',
        'Centered: False',
        'Arm raised: True'
    ]
    
    for i, text in enumerate(outputs):
        ax.text(1, output_y - i*0.3, f'>>> {text}', fontsize=9, 
               family='monospace', color='green', weight='bold',
               bbox=dict(boxstyle='round', facecolor='black', alpha=0.8))
    
    ax.text(5, 7.5, 'YOLO Pose Detection Output', ha='center', 
           fontsize=14, fontweight='bold', color='white',
           bbox=dict(boxstyle='round', facecolor='darkblue', alpha=0.8))
    ax.text(5, 0.3, 'PLACEHOLDER: Replace with actual YOLO detection screenshot',
           ha='center', fontsize=10, style='italic', color='red')
    
    plt.tight_layout()
    plt.savefig('data/pose_detection_screenshot.png', dpi=150, bbox_inches='tight')
    print("Created: data/pose_detection_screenshot.png")
    plt.close()

if __name__ == '__main__':
    import os
    os.makedirs('hardware', exist_ok=True)
    os.makedirs('diagrams', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    print("Creating placeholder images...")
    create_physical_layout_placeholder()
    create_buck_converter_placeholder()
    create_motor_inverter_circuit_placeholder()
    create_cad_drawing_placeholder()
    create_pose_detection_placeholder()
    print("\nAll placeholder images created!")
    print("LaTeX should now compile without missing image errors.")

