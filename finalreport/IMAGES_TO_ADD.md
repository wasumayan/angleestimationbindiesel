# Images That Need to Be Added to LaTeX Report

The LaTeX document references several images that you need to add. Here's what's needed:

## ✅ Images Already Available (Paths Correct)

These images are already in the `finalreport/` folder and paths are correct:

1. ✅ `diagrams/system_block_diagram.png` - System block diagram
2. ✅ `diagrams/state_machine_diagram.png` - State machine diagram
3. ✅ `diagrams/codebase_architecture_diagram.png` - Codebase architecture
4. ✅ `data/wake_word_distance_graph.png` - Wake word distance graph
5. ✅ `data/apriltag_vs_aruco_comparison.png` - ArUco vs AprilTag comparison
6. ✅ `data/tof_safety_trigger_analysis.png` - TOF safety analysis
7. ✅ `data/pwm_traces.png` - PWM traces
8. ✅ `data/steering_correction_path.png` - Steering correction path

## ⚠️ Placeholder Images Created (Replace When Available)

These images have placeholder versions created so the LaTeX compiles. Replace them with actual images when available:

### 1. Physical Layout Diagram ✅ PLACEHOLDER CREATED
**Path in LaTeX**: `diagrams/car_layout_overview.png`
**Status**: Placeholder created - replace with actual photo/CAD
**What to create**: 
- Top-down or isometric view of the car
- Show component placement (Pi, camera, motor, servo, TOF)
- Annotations for each component
- Can be a photo, CAD export, or hand-drawn diagram

### 2. Buck Converter Photo ✅ PLACEHOLDER CREATED
**Path in LaTeX**: `hardware/buck_converter.jpg`
**What to do**: 
- Take a clear photo of your buck converter
- Make sure it's well-lit and in focus
- Save as JPG in `finalreport/hardware/` folder

### 3. Motor Inverter Circuit Diagram ✅ PLACEHOLDER CREATED
**Path in LaTeX**: `hardware/motor_inverter_circuit.png`
**What to create**:
- Circuit diagram showing:
  - Raspberry Pi GPIO → PWM signal
  - Resistors (current limiting, voltage division)
  - Capacitors (filtering)
  - Inverter circuit
  - Motor connection
- Can use KiCad, CircuitLab, draw.io, or hand-drawn (scanned)
- Save as PNG in `finalreport/hardware/` folder

### 4. CAD Drawing ✅ PLACEHOLDER CREATED
**Path in LaTeX**: `hardware/cad_drawing.png`
**What to create**:
- Rendered CAD drawing of your chassis
- Annotate: component locations, mounting points, dimensions
- Export from your CAD software as PNG
- Save in `finalreport/hardware/` folder

### 5. Pose Detection Screenshot ✅ PLACEHOLDER CREATED
**Path in LaTeX**: `data/pose_detection_screenshot.png`
**What to do**:
- Run `test_yolo_pose_tracking.py` on your laptop
- Take a screenshot showing:
  - Detected person with keypoints
  - Track ID visible
  - Command line output showing angle, centered status
- Save as PNG in `finalreport/data/` folder

## 📁 Folder Structure Needed

Make sure you have this folder structure:

```
finalreport/
├── diagrams/          ✅ (exists)
├── data/              ✅ (exists)
├── code/              ✅ (exists)
└── hardware/          ❌ (need to create)
    ├── buck_converter.jpg
    ├── motor_inverter_circuit.png
    └── cad_drawing.png
```

## 🔧 Quick Fixes for LaTeX

If you don't have some images yet, you can:

1. **Comment out the figure**: Add `%` before `\begin{figure}` and `\end{figure}`
2. **Use placeholder**: Create a simple placeholder image (colored rectangle with text)
3. **Temporary removal**: Remove the `\includegraphics` line and keep the caption as "To be added"

## ✅ All Code Files Ready

All code files are ready and paths are correct:
- ✅ `code/main_control_system.py`
- ✅ `code/hardware_controllers/motor_controller.py`
- ✅ `code/hardware_controllers/servo_controller.py`
- ✅ `code/hardware_controllers/tof_sensor.py`
- ✅ `code/configuration/config.py`
- ✅ `code/perception_modules/wake_word_detector.py`
- ✅ `code/perception_modules/yolo_pose_tracker.py`
- ✅ `code/perception_modules/aruco_detector.py`
- ✅ `code/state_machine.py`

## 🎨 Color Coding in LaTeX

The LaTeX document uses color coding for code listings:
- **Yellow background**: Main Control System, ArUco Detection
- **Orange background**: YOLO Pose Tracking, Wake Word
- **Red background**: Hardware Controllers
- **Green background**: Configuration
- **Blue background**: State Machine, Computation

This matches the architecture diagram colors!

