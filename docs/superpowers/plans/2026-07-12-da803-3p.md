# DA803 3P Implementation Plan

> **For agentic workers:** Execute inline in the current session; no subagent delegation was requested.

**Goal:** Build and verify a script-generated DA803 3P FreeCAD assembly for PCBA visualization.

**Architecture:** A single FreeCAD Python builder owns all dimensional parameters and creates an `App::Part` assembly containing three 3.5 mm pole subassemblies plus one independent 1.5 mm side cover. Each pole contains one housing, one rear-hinged lever, and two pins; final solids are saved to FCStd and exported together to STEP.

**Tech Stack:** FreeCAD 1.0 Python API, Part/OpenCASCADE, STEP export.

## Global Constraints

- Work only under `E:\.proj\3D`.
- Do not install global dependencies.
- Rebuild from scratch; do not derive geometry from the existing FCStd files.
- Preserve FCStd and export STEP; do not export STL.
- Model external PCBA-display geometry only; omit internal conductor details.

---

### Task 1: Parametric builder and assembly tree

**Files:**
- Create: `DA_CONNECTOR/build_da803_3p.py`

- [ ] Define all drawing dimensions and estimated display-detail dimensions in one `PARAMS` mapping.
- [ ] Implement housing, lever, and pin solid builders.
- [ ] Create the root assembly, three pole subassemblies, and independent side cover with stable object names.
- [ ] Add a parameter object recording dimensions and assumptions in the FCStd tree.
- [ ] Save `DA803-350-3P.FCStd` and export `DA803-350-3P.step`.

### Task 2: Geometry generation and verification

**Files:**
- Create: `DA_CONNECTOR/verify_da803_3p.py`
- Generate: `DA_CONNECTOR/DA803-350-3P.FCStd`
- Generate: `DA_CONNECTOR/DA803-350-3P.step`

- [ ] Run the builder with `FreeCADCmd.exe` and require exit code 0.
- [ ] Open FCStd and assert the expected 3 housings, 1 side cover, 3 levers, and 6 pins.
- [ ] Assert valid, nonzero-volume shapes and drawing-critical dimensions.
- [ ] Import STEP into a fresh document and assert it contains 13 solids.
- [ ] Report measured body and complete-assembly bounding boxes.
