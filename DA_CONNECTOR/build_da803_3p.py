# -*- coding: utf-8 -*-
"""Build a simplified, parametric DA803 3P assembly for PCBA display."""

import os

import FreeCAD as App
import Part


BASE_DIR = os.environ.get(
    "DA803_DIR",
    os.path.dirname(os.path.abspath(globals().get("__file__", os.getcwd()))),
)
FCSTD_PATH = os.path.join(BASE_DIR, "DA803-350-3P.FCStd")
STEP_PATH = os.path.join(BASE_DIR, "DA803-350-3P.step")

PARAMS = {
    "poles": 3,
    "pitch": 3.5,
    "cover_width": 1.5,
    "depth": 12.5,
    "body_height": 10.6,
    "open_height": 15.93,
    "pin_length": 3.5,
    "pin_x": 0.8,
    "pin_y": 0.5,
    "pin_row_pitch": 5.0,
    "pin_y_front": 3.3,
    "pcb_hole": 1.3,
    "wire_opening_radius": 1.35,
    "wire_opening_depth": 4.35,
    "lever_width": 2.70,
    "lever_length": 7.30,
    "lever_thickness": 1.00,
    "lever_angle": 0.0,
    "body_color": (0.55, 0.55, 0.55),
    "body_color_hex": "#8C8C8C",
    "lever_color": (0.125, 0.125, 0.125),
    "lever_color_hex": "#202020",
}


def add_length(obj, name, value, group="Drawing dimensions"):
    obj.addProperty("App::PropertyLength", name, group)
    setattr(obj, name, value)


def add_parameters(doc, assembly):
    obj = doc.addObject("App::FeaturePython", "Parameters")
    obj.Label = "DA803 Parameters (edit script to regenerate)"
    obj.addProperty("App::PropertyString", "BuildId", "Model")
    obj.BuildId = "DA803_SCRIPTED_3P_V2"
    obj.addProperty("App::PropertyInteger", "Poles", "Drawing dimensions")
    obj.Poles = PARAMS["poles"]
    add_length(obj, "Pitch", PARAMS["pitch"])
    add_length(obj, "OverallWidth", overall_width())
    add_length(obj, "Depth", PARAMS["depth"])
    add_length(obj, "BodyHeight", PARAMS["body_height"])
    add_length(obj, "OpenHeight", PARAMS["open_height"])
    add_length(obj, "PinLength", PARAMS["pin_length"])
    add_length(obj, "PinWidth", PARAMS["pin_x"])
    add_length(obj, "PinThickness", PARAMS["pin_y"])
    add_length(obj, "PinRowPitch", PARAMS["pin_row_pitch"])
    add_length(obj, "RecommendedPcbHole", PARAMS["pcb_hole"])
    obj.addProperty("App::PropertyString", "LeverHingeSide", "Model")
    obj.LeverHingeSide = "Rear"
    obj.addProperty("App::PropertyString", "LeverState", "Model")
    obj.LeverState = "Closed" if PARAMS["lever_angle"] == 0 else "Open"
    obj.addProperty("App::PropertyAngle", "LeverAngle", "Model")
    obj.LeverAngle = PARAMS["lever_angle"]
    obj.addProperty("App::PropertyString", "BodyColor", "Display")
    obj.BodyColor = PARAMS["body_color_hex"]
    obj.addProperty("App::PropertyString", "LeverColor", "Display")
    obj.LeverColor = PARAMS["lever_color_hex"]
    obj.addProperty("App::PropertyString", "Assumptions", "Model")
    obj.Assumptions = (
        "External PCBA-display model; internal spring metal omitted; "
        "unmarked wall, opening and lever details estimated from reference photo."
    )
    obj.addProperty("App::PropertyString", "RegenerateWith", "Model")
    obj.RegenerateWith = "FreeCADCmd.exe build_da803_3p.py"
    assembly.addObject(obj)
    return obj


def overall_width():
    return PARAMS["pitch"] * PARAMS["poles"] + PARAMS["cover_width"]


def pole_center(index):
    return PARAMS["pitch"] * (index + 0.5)


def module_bounds(index):
    left = index * PARAMS["pitch"]
    return left, left + PARAMS["pitch"]


def safe_fillet(shape, radius):
    try:
        result = shape.makeFillet(radius, shape.Edges)
        if result.isValid() and not result.isNull():
            return result
    except Exception:
        pass
    return shape


def make_housing(index):
    left, right = module_bounds(index)
    center = pole_center(index)
    shape = Part.makeBox(
        right - left,
        PARAMS["depth"],
        PARAMS["body_height"],
        App.Vector(left, 0, 0),
    )
    shape = safe_fillet(shape, 0.18)

    # Keyhole-like front wire entry: round lower chamber plus narrow upper slot.
    round_opening = Part.makeCylinder(
        PARAMS["wire_opening_radius"],
        PARAMS["wire_opening_depth"],
        App.Vector(center, -0.05, 4.0),
        App.Vector(0, 1, 0),
    )
    upper_slot = Part.makeBox(
        2.20,
        PARAMS["wire_opening_depth"],
        4.10,
        App.Vector(center - 1.10, -0.05, 4.0),
    )
    shape = shape.cut(round_opening.fuse(upper_slot))

    # Open top channel around the operating lever.
    top_channel = Part.makeBox(
        2.82,
        8.75,
        2.15,
        App.Vector(center - 1.41, 0.75, 8.62),
    )
    shape = shape.cut(top_channel)

    # Rear inspection recess adds the visible stepped product silhouette.
    rear_recess = Part.makeBox(
        2.45,
        2.10,
        2.55,
        App.Vector(center - 1.225, 10.55, 7.20),
    )
    shape = shape.cut(rear_recess)

    # Shallow circular marks on the two outside end faces.
    if index == 0:
        direction = App.Vector(1, 0, 0)
        x_start = left - 0.05
        for y_pos, z_pos in ((2.4, 3.0), (7.3, 3.0), (4.7, 7.1), (9.6, 7.1)):
            pocket = Part.makeCylinder(
                0.48,
                0.32,
                App.Vector(x_start, y_pos, z_pos),
                direction,
            )
            shape = shape.cut(pocket)

    return shape.removeSplitter()


def make_side_cover():
    left = PARAMS["poles"] * PARAMS["pitch"]
    shape = Part.makeBox(
        PARAMS["cover_width"],
        PARAMS["depth"],
        PARAMS["body_height"],
        App.Vector(left, 0, 0),
    )
    shape = safe_fillet(shape, 0.18)

    # Right outside face details; the cover has no electrical opening.
    x_start = overall_width() + 0.05
    for y_pos, z_pos in ((2.4, 3.0), (7.3, 3.0), (4.7, 7.1), (9.6, 7.1)):
        pocket = Part.makeCylinder(
            0.48,
            0.32,
            App.Vector(x_start, y_pos, z_pos),
            App.Vector(-1, 0, 0),
        )
        shape = shape.cut(pocket)
    return shape.removeSplitter()


def make_lever(index):
    center = pole_center(index)
    pivot_y = 9.45
    pivot_z = 9.72
    width = PARAMS["lever_width"]
    lever = Part.makeBox(
        width,
        PARAMS["lever_length"],
        PARAMS["lever_thickness"],
        App.Vector(center - width / 2.0, pivot_y - PARAMS["lever_length"], pivot_z),
    )
    finger_pad = Part.makeBox(
        width + 0.12,
        2.15,
        0.45,
        App.Vector(
            center - (width + 0.12) / 2.0,
            pivot_y - PARAMS["lever_length"] - 0.15,
            pivot_z + 0.75,
        ),
    )
    axle = Part.makeCylinder(
        0.58,
        width,
        App.Vector(center - width / 2.0, pivot_y, pivot_z + 0.50),
        App.Vector(1, 0, 0),
    )
    lever = lever.fuse(finger_pad).fuse(axle).removeSplitter()
    if PARAMS["lever_angle"] != 0:
        lever.rotate(
            App.Vector(center, pivot_y, pivot_z + 0.50),
            App.Vector(1, 0, 0),
            PARAMS["lever_angle"],
        )
    return lever


def make_pin(index, row):
    center_x = pole_center(index)
    center_y = PARAMS["pin_y_front"] + row * PARAMS["pin_row_pitch"]
    return Part.makeBox(
        PARAMS["pin_x"],
        PARAMS["pin_y"],
        PARAMS["pin_length"],
        App.Vector(
            center_x - PARAMS["pin_x"] / 2.0,
            center_y - PARAMS["pin_y"] / 2.0,
            -PARAMS["pin_length"],
        ),
    )


def add_part_feature(doc, container, name, label, shape, color):
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    container.addObject(obj)
    try:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = tuple(max(0.0, c * 0.55) for c in color)
    except Exception:
        pass
    return obj


def build():
    os.makedirs(BASE_DIR, exist_ok=True)
    for name in list(App.listDocuments().keys()):
        App.closeDocument(name)

    doc = App.newDocument("DA803_350_3P")
    assembly = doc.addObject("App::Part", "DA803_3P_Assembly")
    assembly.Label = "DA803 3.5mm 3P Assembly"
    add_parameters(doc, assembly)

    export_objects = []
    housing_color = PARAMS["body_color"]
    lever_color = PARAMS["lever_color"]
    metal_color = (0.78, 0.80, 0.82)

    for index in range(PARAMS["poles"]):
        pole_no = index + 1
        pole = doc.addObject("App::Part", "Pole_%d" % pole_no)
        pole.Label = "Pole %d Module" % pole_no
        assembly.addObject(pole)

        housing = add_part_feature(
            doc,
            pole,
            "Housing_P%d" % pole_no,
            "Housing P%d" % pole_no,
            make_housing(index),
            housing_color,
        )
        lever = add_part_feature(
            doc,
            pole,
            "Lever_P%d" % pole_no,
            "Lever P%d (Open)" % pole_no,
            make_lever(index),
            lever_color,
        )
        pin_a = add_part_feature(
            doc,
            pole,
            "Pin_P%d_A" % pole_no,
            "Pin P%d Front" % pole_no,
            make_pin(index, 0),
            metal_color,
        )
        pin_b = add_part_feature(
            doc,
            pole,
            "Pin_P%d_B" % pole_no,
            "Pin P%d Rear" % pole_no,
            make_pin(index, 1),
            metal_color,
        )
        export_objects.extend((housing, lever, pin_a, pin_b))

    cover = add_part_feature(
        doc,
        assembly,
        "SideCover",
        "1.5 mm Side Cover",
        make_side_cover(),
        housing_color,
    )
    export_objects.append(cover)

    doc.recompute()
    doc.saveAs(FCSTD_PATH)
    Part.export(export_objects, STEP_PATH)
    print("BUILD_OK FCSTD=%s STEP=%s PARTS=%d" % (FCSTD_PATH, STEP_PATH, len(export_objects)))
    return doc


if __name__ == "__main__":
    build()
