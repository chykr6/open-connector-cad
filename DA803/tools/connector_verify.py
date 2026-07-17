# -*- coding: utf-8 -*-
"""验证 connector_generator.py 生成的端子模型。"""

import argparse
import os
import re

import FreeCAD as App
import Part


TOLERANCE = 0.03


def parse_step_colors(text):
    number = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:E[-+]?\d+)?"
    pattern = re.compile(
        r"COLOUR_RGB\('',\s*(%s)\s*,\s*(%s)\s*,\s*(%s)\s*\)"
        % (number, number, number),
        re.IGNORECASE | re.DOTALL,
    )
    return [tuple(float(value) for value in match) for match in pattern.findall(text)]


def contains_rgb(colors, hex_color, tolerance=0.002):
    value = str(hex_color).lstrip("#")
    expected = tuple(int(value[index : index + 2], 16) / 255.0 for index in (0, 2, 4))
    return any(
        all(abs(actual - target) <= tolerance for actual, target in zip(color, expected))
        for color in colors
    )


def assert_close(actual, expected, label, tolerance=TOLERANCE):
    if abs(float(actual) - float(expected)) > tolerance:
        raise AssertionError(
            "%s: expected %.3f, got %.3f" % (label, float(expected), float(actual))
        )


def verify_model(fcstd_path, step_path=None, require_step_colors=True):
    """检查尺寸、零件数量、颜色元数据和 STEP 实体数量。"""
    fcstd_path = os.path.abspath(fcstd_path)
    step_path = os.path.abspath(step_path or os.path.splitext(fcstd_path)[0] + ".step")
    if not os.path.isfile(fcstd_path):
        raise AssertionError("FCStd file missing: %s" % fcstd_path)
    if not os.path.isfile(step_path):
        raise AssertionError("STEP file missing: %s" % step_path)

    doc = App.openDocument(fcstd_path)
    params = doc.getObject("Parameters")
    if params is None or params.BuildId != "CONNECTOR_GENERATOR_V1":
        raise AssertionError("model was not produced by the generic connector generator")

    poles = int(params.Poles)
    pitch = float(params.Pitch)
    housing_width = float(params.HousingWidth) if hasattr(params, "HousingWidth") else pitch
    spacer_width = (
        float(params.InterPoleSpacerWidth)
        if hasattr(params, "InterPoleSpacerWidth")
        else 0.0
    )
    cover_width = float(params.CoverWidth)
    expected_spacers = poles - 1 if spacer_width > 0 else 0
    expected_parts = poles * 4 + expected_spacers + 1
    cover_side_numbering = (
        hasattr(params, "PinNumberingDirection")
        and params.PinNumberingDirection == "CoverSideHighXToLowX"
    )
    # 装配结构必须随极数动态增长：每极 1 外壳、1 压杆、2 焊脚。
    housings = [doc.getObject("Housing_P%d" % index) for index in range(1, poles + 1)]
    actuators = [doc.getObject("Actuator_P%d" % index) for index in range(1, poles + 1)]
    pins = [
        doc.getObject("Pin_P%d_%s" % (index, suffix))
        for index in range(1, poles + 1)
        for suffix in ("A", "B")
    ]
    spacers = []
    if expected_spacers:
        for geometry_index in range(0, poles - 1):
            low_pin = poles - geometry_index
            high_pin = low_pin - 1
            spacers.append(doc.getObject("Spacer_P%d_P%d" % (high_pin, low_pin)))
    cover = doc.getObject("SideCover")
    parts = housings + spacers + actuators + pins + [cover]
    if any(obj is None for obj in parts):
        raise AssertionError("assembly is missing generated component objects")
    if len(parts) != expected_parts:
        raise AssertionError("expected %d parts, got %d" % (expected_parts, len(parts)))
    for obj in parts:
        if obj.Shape.isNull() or not obj.Shape.isValid() or obj.Shape.Volume <= 0:
            raise AssertionError("invalid component geometry: %s" % obj.Name)

    housing_colors = (
        list(params.HousingColors)
        if hasattr(params, "HousingColors")
        else [params.BodyColor] * poles
    )
    if len(housing_colors) != poles:
        raise AssertionError("housing color metadata count mismatch")
    for index, housing in enumerate(housings):
        geometry_index = poles - index - 1 if cover_side_numbering else index
        assert_close(housing.Shape.BoundBox.XLength, housing_width, "housing width")
        assert_close(
            housing.Shape.BoundBox.Center.x,
            pitch * geometry_index + housing_width / 2.0,
            "pole center",
        )
        if housing.ConfiguredColor != housing_colors[index]:
            raise AssertionError("housing color mismatch: %s" % housing.Name)
    for index, spacer in enumerate(spacers):
        assert_close(spacer.Shape.BoundBox.XLength, spacer_width, "spacer width")
        assert_close(
            spacer.Shape.BoundBox.XMin,
            index * pitch + housing_width,
            "spacer start",
        )
        expected_spacer_color = (
            params.SpacerColor if hasattr(params, "SpacerColor") else params.CoverColor
        )
        if spacer.ConfiguredColor != expected_spacer_color:
            raise AssertionError("spacer color mismatch: %s" % spacer.Name)
    assert_close(cover.Shape.BoundBox.XLength, cover_width, "cover width")
    assert_close(
        cover.Shape.BoundBox.XMin,
        (poles - 1) * pitch + housing_width,
        "cover start",
    )
    expected_cover_color = (
        params.CoverColor if hasattr(params, "CoverColor") else params.BodyColor
    )
    if cover.ConfiguredColor != expected_cover_color:
        raise AssertionError("side cover color mismatch")

    actuator_colors = list(params.ActuatorColors)
    if len(actuator_colors) != poles:
        raise AssertionError("actuator color metadata count mismatch")
    for index, actuator in enumerate(actuators):
        if actuator.ConfiguredColor != actuator_colors[index]:
            raise AssertionError("actuator color mismatch: %s" % actuator.Name)
    for pin in pins:
        if pin.ConfiguredColor != params.TerminalPinColor:
            raise AssertionError("terminal pin color mismatch: %s" % pin.Name)

    # 焊脚坐标必须与推荐 PCB layout 一致：横向按 pitch 递增，纵向两排间距固定。
    for index in range(1, poles + 1):
        geometry_index = poles - index if cover_side_numbering else index - 1
        expected_x = float(params.PinFirstX) + geometry_index * pitch
        front_pin = doc.getObject("Pin_P%d_A" % index)
        rear_pin = doc.getObject("Pin_P%d_B" % index)
        assert_close(front_pin.Shape.BoundBox.Center.x, expected_x, "pin column X")
        assert_close(front_pin.Shape.BoundBox.Center.y, float(params.PinFrontY), "front pin Y")
        assert_close(
            rear_pin.Shape.BoundBox.Center.y,
            float(params.PinFrontY) + float(params.PinRowPitch),
            "rear pin Y",
        )

    body = Part.makeCompound([obj.Shape for obj in housings + spacers + [cover]])
    expected_width = (
        float(params.OverallWidth)
        if hasattr(params, "OverallWidth")
        else (poles - 1) * pitch + housing_width + cover_width
    )
    assert_close(body.BoundBox.XLength, expected_width, "overall width")
    assert_close(body.BoundBox.YLength, float(params.Depth), "body depth")
    assert_close(body.BoundBox.ZLength, float(params.BodyHeight), "body height")
    configured_colors = set(housing_colors + actuator_colors)
    configured_colors.add(expected_cover_color)
    if expected_spacers:
        configured_colors.add(
            params.SpacerColor if hasattr(params, "SpacerColor") else expected_cover_color
        )
    configured_colors.add(params.TerminalPinColor)
    App.closeDocument(doc.Name)

    with open(step_path, "r", encoding="utf-8") as stream:
        step_text = stream.read()
    step_lines = step_text.splitlines()
    if any(line.endswith((" ", "\t")) for line in step_lines):
        raise AssertionError("STEP contains trailing whitespace")
    if require_step_colors:
        step_colors = parse_step_colors(step_text)
        if not step_colors:
            raise AssertionError("STEP does not contain color entities")
        missing = [
            color for color in configured_colors if not contains_rgb(step_colors, color)
        ]
        if missing:
            raise AssertionError("STEP missing configured colors: %s" % ", ".join(missing))

    # 重新导入 STEP，确认交换文件不是空壳且实体数量没有丢失。
    step_doc = App.newDocument("StepVerification")
    Part.insert(step_path, step_doc.Name)
    step_doc.recompute()
    step_objects = [
        obj
        for obj in step_doc.Objects
        if hasattr(obj, "Shape") and not obj.Shape.isNull() and obj.Shape.Volume > 0
    ]
    solid_count = sum(len(obj.Shape.Solids) for obj in step_objects)
    if solid_count != expected_parts:
        raise AssertionError(
            "STEP expected %d solids, got %d" % (expected_parts, solid_count)
        )
    App.closeDocument(step_doc.Name)
    result = {
        "poles": poles,
        "parts": expected_parts,
        "width": expected_width,
        "fcstd": fcstd_path,
        "step": step_path,
    }
    print(
        "VERIFY_OK poles=%d parts=%d width=%.3f FCSTD=%s STEP=%s"
        % (poles, expected_parts, result["width"], fcstd_path, step_path)
    )
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fcstd")
    parser.add_argument("--step")
    args = parser.parse_args(argv)
    verify_model(args.fcstd, args.step)


if __name__ == "__main__":
    main()
