# -*- coding: utf-8 -*-
"""模块化端子命令行生成器。

尺寸来自 profiles 目录，极数和颜色来自命令参数。生成器负责创建
FreeCAD 装配树、保存 FCStd，并导出带颜色的 STEP。
"""

import argparse
import json
import os
import re

import FreeCAD as App
import Part


COLOR_NAMES = {
    # 常用颜色名映射到固定的工程配色，命令行也可以直接传 #RRGGBB。
    "black": "#202020",
    "blue": "#1565C0",
    "green": "#2E8B57",
    "gray": "#8C8C8C",
    "grey": "#8C8C8C",
    "silver": "#C0C0C0",
    "red": "#D9291C",
    "orange": "#F58220",
    "yellow": "#F2C200",
    "white": "#F2F2F2",
}


def pitch_code(pitch):
    return "%03d" % int(round(float(pitch) * 100.0))


def normalize_color(value):
    text = str(value).strip()
    named = COLOR_NAMES.get(text.lower())
    if named:
        return named
    if re.fullmatch(r"#[0-9a-fA-F]{6}", text):
        return text.upper()
    raise ValueError("unsupported color: %s" % value)


def expand_colors(specification, poles):
    values = [item.strip() for item in str(specification).split(",") if item.strip()]
    colors = [normalize_color(item) for item in values]
    if len(colors) == 1:
        return colors * int(poles)
    if len(colors) != int(poles):
        raise ValueError(
            "actuator color count must be 1 or match poles (%d), got %d"
            % (int(poles), len(colors))
        )
    return colors


def output_stem(series, pitch, poles, variant=None):
    stem = "%s-%s-%dP" % (str(series).upper(), pitch_code(pitch), int(poles))
    if variant:
        safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(variant).strip()).strip("-")
        if safe:
            stem += "-" + safe.lower()
    return stem


def parse_poles(specification):
    result = [int(item.strip()) for item in str(specification).split(",") if item.strip()]
    if not result or any(value <= 0 for value in result):
        raise ValueError("pole counts must be positive integers")
    return result


def load_profile(series, pitch, connector_dir=None):
    """按系列和间距读取独立尺寸配置，禁止跨间距缩放复用。"""
    # tools 位于 DA_CONNECTOR/tools；产品 profile 位于 products/<series>/profiles。
    base_dir = connector_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = "%s-%s.json" % (str(series).upper(), pitch_code(pitch))
    path = os.path.join(base_dir, "products", str(series).upper(), "profiles", filename)
    if not os.path.isfile(path):
        raise ValueError("profile not found: %s" % path)
    with open(path, "r", encoding="utf-8") as stream:
        profile = json.load(stream)
    if str(profile.get("series", "")).upper() != str(series).upper():
        raise ValueError("profile series mismatch: %s" % path)
    if abs(float(profile.get("pitch", 0)) - float(pitch)) > 1e-9:
        raise ValueError("profile pitch mismatch: %s" % path)
    return profile


def hex_to_rgb(color):
    value = normalize_color(color).lstrip("#")
    return tuple(int(value[index : index + 2], 16) / 255.0 for index in (0, 2, 4))


def overall_width(profile, poles):
    return float(profile["pitch"]) * int(poles) + float(profile["cover_width"])


def pole_center(profile, index):
    return float(profile["pitch"]) * (int(index) + 0.5)


def safe_fillet(shape, radius):
    try:
        result = shape.makeFillet(float(radius), shape.Edges)
        if result.isValid() and not result.isNull():
            return result
    except Exception:
        pass
    return shape


def make_front_slope_cut(profile, x_start, width):
    """创建主体和侧盖共用的前上缘倒角切削体。"""
    slope_length = float(profile["body_front_slope_length"])
    slope_low_z = float(profile["body_front_slope_low_z"])
    body_height = float(profile["body_height"])
    start_x = float(x_start) - 0.10
    slope_wire = Part.makePolygon(
        [
            App.Vector(start_x, -0.10, slope_low_z),
            App.Vector(start_x, -0.10, body_height + 0.20),
            App.Vector(start_x, slope_length, body_height + 0.20),
            App.Vector(start_x, slope_length, body_height),
            App.Vector(start_x, -0.10, slope_low_z),
        ]
    )
    return Part.Face(slope_wire).extrude(App.Vector(float(width) + 0.20, 0, 0))


def make_housing(profile, poles, index):
    """生成一个电气模块外壳；每极宽度严格等于 pitch。"""
    pitch = float(profile["pitch"])
    left = int(index) * pitch
    center = pole_center(profile, index)
    shape = Part.makeBox(
        pitch,
        float(profile["depth"]),
        float(profile["body_height"]),
        App.Vector(left, 0, 0),
    )
    shape = safe_fillet(shape, 0.18)

    # 正面进线口由圆形下部和矩形上部组合成钥匙孔轮廓。
    round_opening = Part.makeCylinder(
        float(profile["wire_opening_radius"]),
        float(profile["wire_opening_depth"]),
        App.Vector(center, -0.05, 4.0),
        App.Vector(0, 1, 0),
    )
    upper_slot = Part.makeBox(
        2.20,
        float(profile["wire_opening_depth"]),
        4.10,
        App.Vector(center - 1.10, -0.05, 4.0),
    )
    shape = shape.cut(round_opening.fuse(upper_slot))

    # 顶部通道给压杆留出运动和装配空间。
    top_channel = Part.makeBox(
        2.82,
        8.75,
        2.15,
        App.Vector(center - 1.41, 0.75, 8.62),
    )
    shape = shape.cut(top_channel)

    # 主体前上缘切出斜坡，给手指从压杆下方进入的空间。
    shape = shape.cut(make_front_slope_cut(profile, left, pitch))

    if int(index) == 0:
        for y_pos, z_pos in ((2.4, 3.0), (7.3, 3.0), (4.7, 7.1), (9.6, 7.1)):
            pocket = Part.makeCylinder(
                0.48,
                0.32,
                App.Vector(left - 0.05, y_pos, z_pos),
                App.Vector(1, 0, 0),
            )
            shape = shape.cut(pocket)
    return shape.removeSplitter()


def make_side_cover(profile, poles):
    """生成独立侧盖；侧盖没有电气开口。"""
    left = int(poles) * float(profile["pitch"])
    shape = Part.makeBox(
        float(profile["cover_width"]),
        float(profile["depth"]),
        float(profile["body_height"]),
        App.Vector(left, 0, 0),
    )
    shape = safe_fillet(shape, 0.18)
    # 侧盖与电气模块采用同一前缘倒角，装配后侧面轮廓连续。
    shape = shape.cut(make_front_slope_cut(profile, left, profile["cover_width"]))
    x_start = overall_width(profile, poles) + 0.05
    for y_pos, z_pos in ((2.4, 3.0), (7.3, 3.0), (4.7, 7.1), (9.6, 7.1)):
        pocket = Part.makeCylinder(
            0.48,
            0.32,
            App.Vector(x_start, y_pos, z_pos),
            App.Vector(-1, 0, 0),
        )
        shape = shape.cut(pocket)
    return shape.removeSplitter()


def make_actuator(profile, index):
    """生成后端铰接的塑料压杆，前端伸出并带明显斜面。"""
    center = pole_center(profile, index)
    pivot_y = float(profile["actuator_pivot_y"])
    pivot_z = float(profile["actuator_pivot_z"])
    width = float(profile["actuator_width"])
    tip_y = float(profile["actuator_tip_y"])
    nose_start_y = float(profile["actuator_nose_start_y"])
    top_z = float(profile["actuator_top_z"])
    # 厚度由 profile 统一控制，底面由上表面减厚度得到。
    main_bottom_z = top_z - float(profile["actuator_thickness"])

    # 先建立薄长条毛坯，再按参考图切掉前端绿色区域：长条底面
    # 通过一条斜线直接收敛到上方尖点，不保留前端竖直面。
    x_start = center - width / 2.0
    side_wire = Part.makePolygon(
        [
            App.Vector(x_start, tip_y, top_z),
            App.Vector(x_start, pivot_y, top_z),
            App.Vector(x_start, pivot_y, main_bottom_z),
            App.Vector(x_start, nose_start_y, main_bottom_z),
            App.Vector(x_start, tip_y, top_z),
        ]
    )
    actuator = Part.Face(side_wire).extrude(App.Vector(width, 0, 0))

    # 圆柱表示后端铰轴，便于装配树和侧视图识别旋转中心。
    axle = Part.makeCylinder(
        0.58,
        width,
        App.Vector(center - width / 2.0, pivot_y, pivot_z + 0.50),
        App.Vector(1, 0, 0),
    )
    actuator = actuator.fuse(axle).removeSplitter()
    angle = float(profile.get("actuator_angle", 0.0))
    if angle:
        actuator.rotate(
            App.Vector(center, pivot_y, pivot_z + 0.50),
            App.Vector(1, 0, 0),
            angle,
        )
    return actuator


def make_terminal_pin(profile, index, row):
    """生成一根 PCB 焊脚；每极包含前后两根。"""
    # 焊脚中心按推荐 PCB layout 定位，不等同于塑胶模块几何中心。
    center_x = float(profile["pin_x_first"]) + int(index) * float(profile["pitch"])
    center_y = float(profile["pin_y_front"]) + int(row) * float(profile["pin_row_pitch"])
    width = float(profile["pin_width"])
    thickness = float(profile["pin_thickness"])
    length = float(profile["pin_length"])
    return Part.makeBox(
        width,
        thickness,
        length,
        App.Vector(center_x - width / 2.0, center_y - thickness / 2.0, -length),
    )


def add_feature(doc, container, name, label, shape, color, kind, pole_index=0):
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "ConfiguredColor", "Appearance")
    obj.ConfiguredColor = normalize_color(color)
    obj.addProperty("App::PropertyString", "ComponentKind", "Model")
    obj.ComponentKind = kind
    obj.addProperty("App::PropertyInteger", "PoleIndex", "Model")
    obj.PoleIndex = int(pole_index)
    container.addObject(obj)
    if App.GuiUp and obj.ViewObject:
        obj.ViewObject.ShapeColor = hex_to_rgb(color)
        obj.ViewObject.LineColor = tuple(max(0.0, channel * 0.55) for channel in hex_to_rgb(color))
    return obj


def add_parameters(doc, assembly, profile, poles, body_color, actuator_colors, pin_color, variant):
    obj = doc.addObject("App::FeaturePython", "Parameters")
    obj.Label = "Connector generation parameters"
    values = (
        ("App::PropertyString", "BuildId", "CONNECTOR_GENERATOR_V1"),
        ("App::PropertyString", "Series", str(profile["series"])),
        ("App::PropertyString", "PitchCode", pitch_code(profile["pitch"])),
        ("App::PropertyString", "Variant", str(variant or "")),
        ("App::PropertyString", "BodyColor", normalize_color(body_color)),
        ("App::PropertyString", "TerminalPinColor", normalize_color(pin_color)),
        ("App::PropertyString", "LeverHingeSide", "Rear"),
        ("App::PropertyString", "LeverState", "Closed"),
    )
    for property_type, name, value in values:
        obj.addProperty(property_type, name, "Generation")
        setattr(obj, name, value)
    obj.addProperty("App::PropertyInteger", "Poles", "Generation")
    obj.Poles = int(poles)
    obj.addProperty("App::PropertyLength", "Pitch", "Dimensions")
    obj.Pitch = float(profile["pitch"])
    obj.addProperty("App::PropertyLength", "OverallWidth", "Dimensions")
    obj.OverallWidth = overall_width(profile, poles)
    obj.addProperty("App::PropertyLength", "Depth", "Dimensions")
    obj.Depth = float(profile["depth"])
    obj.addProperty("App::PropertyLength", "BodyHeight", "Dimensions")
    obj.BodyHeight = float(profile["body_height"])
    obj.addProperty("App::PropertyLength", "CoverWidth", "Dimensions")
    obj.CoverWidth = float(profile["cover_width"])
    obj.addProperty("App::PropertyLength", "ActuatorThickness", "Dimensions")
    obj.ActuatorThickness = float(profile["actuator_thickness"])
    obj.addProperty("App::PropertyLength", "PinFirstX", "PCB layout")
    obj.PinFirstX = float(profile["pin_x_first"])
    obj.addProperty("App::PropertyLength", "PinFrontY", "PCB layout")
    obj.PinFrontY = float(profile["pin_y_front"])
    obj.addProperty("App::PropertyLength", "PinRowPitch", "PCB layout")
    obj.PinRowPitch = float(profile["pin_row_pitch"])
    obj.addProperty("App::PropertyStringList", "ActuatorColors", "Generation")
    obj.ActuatorColors = [normalize_color(color) for color in actuator_colors]
    assembly.addObject(obj)
    return obj


def generate_one(
    profile,
    poles,
    body_color,
    actuator_colors,
    terminal_pin_color,
    variant=None,
    output_dir=None,
):
    poles = int(poles)
    if poles <= 0:
        raise ValueError("poles must be positive")
    if len(actuator_colors) != poles:
        raise ValueError("actuator color count must match poles")

    connector_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_dir = output_dir or os.path.join(
        connector_dir,
        "products",
        str(profile["series"]).upper(),
        "generated",
        "%s-%s" % (profile["series"], pitch_code(profile["pitch"])),
    )
    os.makedirs(base_dir, exist_ok=True)
    stem = output_stem(profile["series"], profile["pitch"], poles, variant)
    fcstd_path = os.path.join(base_dir, stem + ".FCStd")
    step_path = os.path.join(base_dir, stem + ".step")

    doc_name = re.sub(r"[^A-Za-z0-9_]", "_", stem)
    if doc_name in App.listDocuments():
        App.closeDocument(doc_name)
    # 每个输出文件都是独立装配文档，避免不同极数和配色互相覆盖。
    doc = App.newDocument(doc_name)
    assembly = doc.addObject("App::Part", "ConnectorAssembly")
    assembly.Label = stem + " Assembly"
    add_parameters(
        doc,
        assembly,
        profile,
        poles,
        body_color,
        actuator_colors,
        terminal_pin_color,
        variant,
    )

    export_objects = []
    # 按从左到右的顺序创建电气模块、压杆和两根焊脚。
    for index in range(poles):
        pole_no = index + 1
        pole = doc.addObject("App::Part", "Pole_%d" % pole_no)
        pole.Label = "Pole %d Module" % pole_no
        assembly.addObject(pole)
        export_objects.append(
            add_feature(
                doc,
                pole,
                "Housing_P%d" % pole_no,
                "Housing P%d" % pole_no,
                make_housing(profile, poles, index),
                body_color,
                "Housing",
                pole_no,
            )
        )
        export_objects.append(
            add_feature(
                doc,
                pole,
                "Actuator_P%d" % pole_no,
                "Actuator P%d" % pole_no,
                make_actuator(profile, index),
                actuator_colors[index],
                "Actuator",
                pole_no,
            )
        )
        for row, suffix in enumerate(("A", "B")):
            export_objects.append(
                add_feature(
                    doc,
                    pole,
                    "Pin_P%d_%s" % (pole_no, suffix),
                    "Terminal Pin P%d %s" % (pole_no, suffix),
                    make_terminal_pin(profile, index, row),
                    terminal_pin_color,
                    "TerminalPin",
                    pole_no,
                )
            )

    export_objects.append(
        add_feature(
            doc,
            assembly,
            "SideCover",
            "%g mm Side Cover" % float(profile["cover_width"]),
            make_side_cover(profile, poles),
            body_color,
            "SideCover",
        )
    )
    doc.recompute()
    doc.saveAs(fcstd_path)
    # GUI 模式优先使用 ImportGui，以便 STEP 保留部件颜色。
    if App.GuiUp:
        try:
            import ImportGui

            ImportGui.export(export_objects, step_path)
        except Exception:
            Part.export(export_objects, step_path)
    else:
        Part.export(export_objects, step_path)
    doc.save()
    App.closeDocument(doc.Name)
    return {
        "stem": stem,
        "fcstd": fcstd_path,
        "step": step_path,
        "parts": len(export_objects),
    }


def derive_variant(specification):
    values = [item.strip().lower() for item in str(specification).split(",") if item.strip()]
    if len(set(values)) <= 1:
        return None
    return "-".join(re.sub(r"[^a-z0-9]+", "", value.lstrip("#")) for value in values)


def build_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series", required=True)
    parser.add_argument("--pitch", required=True, type=float)
    parser.add_argument("--poles", required=True, help="One value or comma-separated values")
    parser.add_argument("--body-color")
    parser.add_argument("--actuator-colors")
    parser.add_argument("--terminal-pin-color")
    parser.add_argument("--variant")
    parser.add_argument("--output-dir")
    return parser


def request_to_argv(request):
    argv = []
    for key, value in request.items():
        if value is not None and value != "":
            argv.extend(["--" + key.replace("_", "-"), str(value)])
    return argv


def main(argv=None):
    args = build_argument_parser().parse_args(argv)
    connector_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profile = load_profile(args.series, args.pitch, connector_dir)
    defaults = profile["default_colors"]
    body_color = normalize_color(args.body_color or defaults["body"])
    pin_color = normalize_color(args.terminal_pin_color or defaults["terminal_pin"])
    pole_counts = parse_poles(args.poles)
    results = []
    for poles in pole_counts:
        color_spec = args.actuator_colors or defaults["actuator"]
        actuator_colors = expand_colors(color_spec, poles)
        variant = args.variant or derive_variant(color_spec)
        results.append(
            generate_one(
                profile,
                poles,
                body_color,
                actuator_colors,
                pin_color,
                variant,
                args.output_dir,
            )
        )
    for result in results:
        print(
            "GENERATE_OK stem=%s parts=%d FCSTD=%s STEP=%s"
            % (result["stem"], result["parts"], result["fcstd"], result["step"])
        )
    if App.GuiUp and os.environ.get("CONNECTOR_AUTOCLOSE") == "1":
        try:
            import FreeCADGui as Gui

            Gui.getMainWindow().close()
        except Exception:
            pass
    return results


request_json = os.environ.get("CONNECTOR_REQUEST_JSON")
if request_json:
    main(request_to_argv(json.loads(request_json)))
elif __name__ == "__main__":
    main()
