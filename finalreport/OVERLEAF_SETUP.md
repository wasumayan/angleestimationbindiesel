# Overleaf Setup Guide

This guide will walk you through setting up your LaTeX report in Overleaf.

## Step 1: Create Overleaf Project

1. Go to https://www.overleaf.com
2. Sign in (or create account if needed)
3. Click "New Project" → "Blank Project"
4. Name it: "Bin Diesel Final Project Report"

## Step 2: Upload Main LaTeX File

1. In Overleaf, click "Upload" (top left)
2. Upload `Final_Project_Report.tex` from the `finalreport/` folder
3. This will be your main file

## Step 3: Create Folder Structure

In Overleaf, create the following folder structure using the "New Folder" button:

```
📁 diagrams/
📁 data/
📁 code/
   📁 hardware_controllers/
   📁 perception_modules/
   📁 computation_modules/
   📁 configuration/
📁 hardware/  (for images you'll add later)
```

## Step 4: Upload Diagrams

Upload all diagram files to the `diagrams/` folder:

1. Click on `diagrams/` folder
2. Click "Upload" 
3. Upload these files:
   - `system_block_diagram.png`
   - `state_machine_diagram.png`
   - `codebase_architecture_diagram.png`

**Files to upload**:
- `finalreport/diagrams/system_block_diagram.png`
- `finalreport/diagrams/state_machine_diagram.png`
- `finalreport/diagrams/codebase_architecture_diagram.png`

## Step 5: Upload Data Graphs

Upload all data graph files to the `data/` folder:

1. Click on `data/` folder
2. Click "Upload"
3. Upload these files:
   - `wake_word_distance_graph.png`
   - `apriltag_vs_aruco_comparison.png`
   - `tof_safety_trigger_analysis.png`
   - `pwm_traces.png`
   - `steering_correction_path.png`

**Files to upload**:
- `finalreport/data/wake_word_distance_graph.png`
- `finalreport/data/apriltag_vs_aruco_comparison.png`
- `finalreport/data/tof_safety_trigger_analysis.png`
- `finalreport/data/pwm_traces.png`
- `finalreport/data/steering_correction_path.png`

## Step 6: Upload Code Files

### 6.1 Main Control System

1. Click on `code/` folder (root level)
2. Upload: `main_control_system.py`
   - File: `finalreport/code/main_control_system.py`

### 6.2 Hardware Controllers

1. Click on `code/hardware_controllers/` folder
2. Upload these files:
   - `motor_controller.py`
   - `servo_controller.py`
   - `tof_sensor.py`

**Files to upload**:
- `finalreport/code/hardware_controllers/motor_controller.py`
- `finalreport/code/hardware_controllers/servo_controller.py`
- `finalreport/code/hardware_controllers/tof_sensor.py`

### 6.3 Configuration

1. Click on `code/configuration/` folder
2. Upload: `config.py`
   - File: `finalreport/code/configuration/config.py`

### 6.4 Perception Modules

1. Click on `code/perception_modules/` folder
2. Upload these files:
   - `wake_word_detector.py`
   - `yolo_pose_tracker.py`
   - `aruco_detector.py`

**Files to upload**:
- `finalreport/code/perception_modules/wake_word_detector.py`
- `finalreport/code/perception_modules/yolo_pose_tracker.py`
- `finalreport/code/perception_modules/aruco_detector.py`

### 6.5 Computation Modules

1. Click on `code/computation_modules/` folder
2. Upload these files:
   - `state_machine.py`
   - `logger.py`
   - `optimizations.py`

**Files to upload**:
- `finalreport/code/state_machine.py` (copy from `finalreport/code/`)
- `finalreport/code/computation_modules/logger.py`
- `finalreport/code/computation_modules/optimizations.py`

**Note**: `state_machine.py` is in the root `code/` folder, but you can also copy it to `computation_modules/` or just reference it from root.

## Step 7: Set Main File

1. In Overleaf, make sure `Final_Project_Report.tex` is open
2. Click the "Menu" button (top left, three lines)
3. Under "Main document", select `Final_Project_Report.tex`
4. This tells Overleaf which file to compile

## Step 8: Compile

1. Click the "Recompile" button (top center)
2. Wait for compilation to complete
3. View the PDF on the right side

## Step 9: Handle Missing Images (Temporary)

If you get errors about missing images, you have two options:

### Option A: Comment Out Missing Images

For images you haven't created yet, comment them out in the LaTeX:

```latex
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.7\textwidth]{diagrams/car_layout_overview.png}
%     \caption{Physical layout...}
%     \label{fig:physical_layout}
% \end{figure}
```

### Option B: Create Placeholder Images

Create simple placeholder images (colored rectangles with text) and upload them to the appropriate folders.

## Step 10: Add Missing Images Later

When you have the missing images ready:

1. **Physical Layout**: Upload to `diagrams/car_layout_overview.png`
2. **Buck Converter Photo**: Upload to `hardware/buck_converter.jpg`
3. **Motor Inverter Circuit**: Upload to `hardware/motor_inverter_circuit.png`
4. **CAD Drawing**: Upload to `hardware/cad_drawing.png`
5. **Pose Detection Screenshot**: Upload to `data/pose_detection_screenshot.png`

Then uncomment the figure sections in the LaTeX file.

## Troubleshooting

### Error: "File not found"

- Check that file paths in LaTeX match the folder structure in Overleaf
- Make sure all files are uploaded to the correct folders
- Paths are relative to the main `.tex` file location

### Error: "Package not found"

Overleaf usually has all packages. If you get package errors:
1. Check the error message
2. Sometimes Overleaf auto-installs missing packages
3. If not, you may need to use a different package or comment out that section

### Code Listings Too Long

If the PDF is very large or compilation is slow:
- The code files are included in full (as requested)
- This is normal for a complete appendix
- PDF may be 50-100+ pages with all code

### Compilation Takes Long Time

- First compilation may take 1-2 minutes (Overleaf processes all images)
- Subsequent compilations are faster
- Large code listings add to compilation time

## Quick Upload Checklist

Use this checklist to ensure you upload everything:

**Diagrams** (3 files):
- [ ] `diagrams/system_block_diagram.png`
- [ ] `diagrams/state_machine_diagram.png`
- [ ] `diagrams/codebase_architecture_diagram.png`

**Data Graphs** (5 files):
- [ ] `data/wake_word_distance_graph.png`
- [ ] `data/apriltag_vs_aruco_comparison.png`
- [ ] `data/tof_safety_trigger_analysis.png`
- [ ] `data/pwm_traces.png`
- [ ] `data/steering_correction_path.png`

**Code Files** (9 files):
- [ ] `code/main_control_system.py`
- [ ] `code/state_machine.py`
- [ ] `code/hardware_controllers/motor_controller.py`
- [ ] `code/hardware_controllers/servo_controller.py`
- [ ] `code/hardware_controllers/tof_sensor.py`
- [ ] `code/configuration/config.py`
- [ ] `code/perception_modules/wake_word_detector.py`
- [ ] `code/perception_modules/yolo_pose_tracker.py`
- [ ] `code/perception_modules/aruco_detector.py`
- [ ] `code/computation_modules/logger.py`
- [ ] `code/computation_modules/optimizations.py`

**Main File**:
- [ ] `Final_Project_Report.tex`

## Final Structure in Overleaf

Your Overleaf project should look like this:

```
📄 Final_Project_Report.tex (main file)
📁 diagrams/
   📄 system_block_diagram.png
   📄 state_machine_diagram.png
   📄 codebase_architecture_diagram.png
📁 data/
   📄 wake_word_distance_graph.png
   📄 apriltag_vs_aruco_comparison.png
   📄 tof_safety_trigger_analysis.png
   📄 pwm_traces.png
   📄 steering_correction_path.png
📁 code/
   📄 main_control_system.py
   📄 state_machine.py
   📁 hardware_controllers/
      📄 motor_controller.py
      📄 servo_controller.py
      📄 tof_sensor.py
   📁 configuration/
      📄 config.py
   📁 perception_modules/
      📄 wake_word_detector.py
      📄 yolo_pose_tracker.py
      📄 aruco_detector.py
   📁 computation_modules/
      📄 logger.py
      📄 optimizations.py
📁 hardware/ (empty for now, add images later)
```

## Tips for Overleaf

1. **Auto-compile**: Overleaf can auto-compile on save (enable in Settings)
2. **Version History**: Overleaf keeps version history (useful for reverting changes)
3. **Collaboration**: You can share the project with others if needed
4. **Download PDF**: Click "PDF" button to download the compiled PDF
5. **Download Source**: Click "Menu" → "Source" to download all files as ZIP

## Next Steps

1. Upload all files following the checklist above
2. Compile the document
3. Check for any errors
4. Add missing images as you create them
5. Recompile to see updates

Good luck! Your report should compile successfully once all files are uploaded.

