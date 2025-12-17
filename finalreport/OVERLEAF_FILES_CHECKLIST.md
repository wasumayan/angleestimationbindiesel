# Overleaf Files Upload Checklist

Use this checklist to ensure you upload all required files to Overleaf.

## ✅ Files to Upload

### Main LaTeX File (1 file)
- [ ] `Final_Project_Report.tex` → Upload to root of Overleaf project

### Diagrams (3 files) → Upload to `diagrams/` folder
- [ ] `diagrams/system_block_diagram.png`
- [ ] `diagrams/state_machine_diagram.png`
- [ ] `diagrams/codebase_architecture_diagram.png`

### Data Graphs (5 files) → Upload to `data/` folder
- [ ] `data/wake_word_distance_graph.png`
- [ ] `data/apriltag_vs_aruco_comparison.png`
- [ ] `data/tof_safety_trigger_analysis.png`
- [ ] `data/pwm_traces.png`
- [ ] `data/steering_correction_path.png`

### Code Files (11 files)

#### Root Code Folder (`code/`)
- [ ] `code/main_control_system.py`
- [ ] `code/state_machine.py`

#### Hardware Controllers (`code/hardware_controllers/`)
- [ ] `code/hardware_controllers/motor_controller.py`
- [ ] `code/hardware_controllers/servo_controller.py`
- [ ] `code/hardware_controllers/tof_sensor.py`

#### Configuration (`code/configuration/`)
- [ ] `code/configuration/config.py`

#### Perception Modules (`code/perception_modules/`)
- [ ] `code/perception_modules/wake_word_detector.py`
- [ ] `code/perception_modules/yolo_pose_tracker.py`
- [ ] `code/perception_modules/aruco_detector.py`

#### Computation Modules (`code/computation_modules/`)
- [ ] `code/computation_modules/logger.py`
- [ ] `code/computation_modules/optimizations.py`

## 📁 Folder Structure in Overleaf

Create these folders in Overleaf (in this order):

1. `diagrams/` (for diagram PNGs)
2. `data/` (for data graph PNGs)
3. `code/` (root code folder)
4. `code/hardware_controllers/` (inside code/)
5. `code/configuration/` (inside code/)
6. `code/perception_modules/` (inside code/)
7. `code/computation_modules/` (inside code/)
8. `hardware/` (for images you'll add later - optional for now)

## 🚀 Quick Upload Steps

1. **Create folders first** (use "New Folder" button in Overleaf)
2. **Upload main file**: `Final_Project_Report.tex` to root
3. **Upload diagrams**: All 3 PNGs to `diagrams/` folder
4. **Upload data graphs**: All 5 PNGs to `data/` folder
5. **Upload code files**: 
   - 2 files to `code/` root
   - 3 files to `code/hardware_controllers/`
   - 1 file to `code/configuration/`
   - 3 files to `code/perception_modules/`
   - 2 files to `code/computation_modules/`

## ⚠️ Important Notes

- **File paths matter**: Make sure files are in the correct folders
- **Case sensitive**: File names are case-sensitive in LaTeX
- **No spaces**: Overleaf handles spaces, but it's better to avoid them
- **Set main file**: After uploading, set `Final_Project_Report.tex` as the main document

## 📊 Total Files

- **Main file**: 1
- **Diagrams**: 3
- **Data graphs**: 5
- **Code files**: 11
- **Total**: 20 files to upload

## ✅ After Upload

1. Set `Final_Project_Report.tex` as main document
2. Click "Recompile"
3. Check for errors
4. View PDF

If you get "file not found" errors, double-check:
- Folder names match exactly
- File names match exactly
- Files are in the correct folders

