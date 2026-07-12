# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import unittest

import FreeCAD as App
import Part


CONNECTOR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(CONNECTOR_DIR, "tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

import connector_generator as generator


class GeneratorParameterTests(unittest.TestCase):
    def test_pitch_code_uses_hundredths_of_millimeter(self):
        self.assertEqual(generator.pitch_code(3.5), "350")
        self.assertEqual(generator.pitch_code(5.0), "500")
        self.assertEqual(generator.pitch_code(7.5), "750")

    def test_named_and_hex_colors_are_normalized(self):
        self.assertEqual(generator.normalize_color("black"), "#202020")
        self.assertEqual(generator.normalize_color("blue"), "#1565C0")
        self.assertEqual(generator.normalize_color("#2e8b57"), "#2E8B57")

    def test_single_actuator_color_expands_to_all_poles(self):
        self.assertEqual(
            generator.expand_colors("black", 3),
            ["#202020", "#202020", "#202020"],
        )

    def test_actuator_color_list_maps_left_to_right(self):
        self.assertEqual(
            generator.expand_colors("black,blue,green", 3),
            ["#202020", "#1565C0", "#2E8B57"],
        )

    def test_wrong_color_count_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "color count"):
            generator.expand_colors("black,blue", 3)

    def test_output_name_contains_pitch_poles_and_variant(self):
        self.assertEqual(
            generator.output_stem("DA803", 3.5, 3, "black-blue-green"),
            "DA803-350-3P-black-blue-green",
        )

    def test_multiple_pole_counts_are_parsed(self):
        self.assertEqual(generator.parse_poles("1,2,4,8"), [1, 2, 4, 8])
        with self.assertRaisesRegex(ValueError, "positive"):
            generator.parse_poles("0,3")

    def test_environment_request_is_converted_to_cli_arguments(self):
        argv = generator.request_to_argv(
            {
                "series": "DA803",
                "pitch": 3.5,
                "poles": "3",
                "body_color": "black",
                "variant": None,
            }
        )
        self.assertEqual(
            argv,
            [
                "--series",
                "DA803",
                "--pitch",
                "3.5",
                "--poles",
                "3",
                "--body-color",
                "black",
            ],
        )

    def test_da803_350_profile_is_loaded_by_series_and_pitch(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        self.assertEqual(profile["series"], "DA803")
        self.assertEqual(profile["pitch"], 3.5)
        self.assertEqual(profile["cover_width"], 1.5)


class GeneratorIntegrationTests(unittest.TestCase):
    def tearDown(self):
        for name in list(App.listDocuments().keys()):
            App.closeDocument(name)

    def test_two_pole_model_has_dynamic_parts_and_per_pole_colors(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        with tempfile.TemporaryDirectory() as output_dir:
            result = generator.generate_one(
                profile=profile,
                poles=2,
                body_color="#202020",
                actuator_colors=["#202020", "#1565C0"],
                terminal_pin_color="#C0C0C0",
                variant="black-blue",
                output_dir=output_dir,
            )
            self.assertTrue(os.path.isfile(result["fcstd"]))
            self.assertTrue(os.path.isfile(result["step"]))
            with open(result["step"], "r", encoding="utf-8") as stream:
                step_lines = stream.read().splitlines()
            self.assertFalse(
                any(line.endswith((" ", "\t")) for line in step_lines),
                "generated STEP must not contain trailing whitespace",
            )
            self.assertEqual(
                os.path.basename(result["fcstd"]),
                "DA803-350-2P-black-blue.FCStd",
            )

            doc = App.openDocument(result["fcstd"])
            params = doc.getObject("Parameters")
            self.assertEqual(params.Poles, 2)
            self.assertEqual(params.BodyColor, "#202020")
            self.assertEqual(list(params.ActuatorColors), ["#202020", "#1565C0"])
            self.assertAlmostEqual(float(params.PinFirstX), 2.25, places=6)
            self.assertAlmostEqual(float(params.PinFrontY), 4.60, places=6)
            self.assertAlmostEqual(float(params.PinRowPitch), 5.00, places=6)
            self.assertIsNotNone(doc.getObject("SideCover"))
            self.assertIsNone(doc.getObject("Housing_P3"))
            self.assertEqual(doc.getObject("Actuator_P1").ConfiguredColor, "#202020")
            self.assertEqual(doc.getObject("Actuator_P2").ConfiguredColor, "#1565C0")

            expected_names = (
                ["Housing_P1", "Housing_P2", "SideCover"]
                + ["Actuator_P1", "Actuator_P2"]
                + ["Pin_P1_A", "Pin_P1_B", "Pin_P2_A", "Pin_P2_B"]
            )
            self.assertEqual(
                sum(len(doc.getObject(name).Shape.Solids) for name in expected_names),
                9,
            )

    def test_actuator_is_flush_with_housing_and_only_pointed_tip_protrudes(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        actuator = generator.make_actuator(profile, 0)

        # 压杆上表面与主体顶面平齐，铰轴也不得向上凸出。
        self.assertAlmostEqual(
            actuator.BoundBox.ZMax, profile["body_height"], delta=0.02
        )

        # 只有楔形尖端越过主体正面约 0.35 mm，厚主体仍留在通道内。
        self.assertGreater(actuator.BoundBox.YMin, -0.45)
        self.assertLess(actuator.BoundBox.YMin, -0.25)
        self.assertLess(actuator.BoundBox.YMin, 0.0)

        center_x = profile["pitch"] / 2.0
        front_y = actuator.BoundBox.YMin + 0.10
        # 侧视尖端上部有材料，下部为空，不再是竖直厚鼻头。
        self.assertTrue(
            actuator.isInside(
                App.Vector(center_x, front_y, profile["body_height"] - 0.05),
                0.01,
                True,
            )
        )
        self.assertFalse(
            actuator.isInside(
                App.Vector(center_x, front_y, profile["body_height"] - 0.30),
                0.01,
                True,
            )
        )

        # 沿 Y 向后，斜面逐渐降低，随后恢复完整 2 mm 厚主体。
        self.assertFalse(
            actuator.isInside(App.Vector(center_x, 0.60, 9.20), 0.01, True)
        )
        self.assertTrue(
            actuator.isInside(App.Vector(center_x, 0.60, 9.60), 0.01, True)
        )

        # 长条主体厚度为 2.0 mm，不再是薄片。
        self.assertTrue(
            actuator.isInside(App.Vector(center_x, 5.00, 8.80), 0.01, True)
        )
        self.assertFalse(
            actuator.isInside(App.Vector(center_x, 5.00, 8.50), 0.01, True)
        )

    def test_actuator_length_profile_directly_controls_closed_length(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        shorter = dict(profile)
        shorter["actuator_length"] = 6.0
        actuator = generator.make_actuator(shorter, 0)
        self.assertAlmostEqual(actuator.BoundBox.YLength, 6.0, delta=0.15)

    def test_nonzero_actuator_angle_rotates_around_the_visible_axle(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        opened = dict(profile)
        opened["actuator_angle"] = 24.0
        actuator = generator.make_actuator(opened, 0)

        center_x = profile["pitch"] / 2.0
        width = profile["actuator_width"]
        axle_y = profile["actuator_pivot_y"] + profile["actuator_axle_y_offset"]
        axle_z = profile["actuator_pivot_z"] + profile["actuator_axle_z_offset"]
        axle = Part.makeCylinder(
            profile["actuator_axle_radius"],
            width,
            App.Vector(center_x - width / 2.0, axle_y, axle_z),
            App.Vector(1, 0, 0),
        )
        self.assertAlmostEqual(
            actuator.common(axle).Volume,
            axle.Volume,
            delta=axle.Volume * 0.01,
        )

    def test_wire_opening_has_a_wide_rounded_cavity_and_narrow_top_arch(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        housing = generator.make_housing(profile, 3, 0)
        center_x = profile["pitch"] / 2.0

        # 下部腔体应接近主体底边，并比旧版圆孔更宽。
        self.assertFalse(housing.isInside(App.Vector(center_x, 0.20, 1.20), 0.01, True))
        self.assertFalse(
            housing.isInside(App.Vector(center_x - 1.05, 0.20, 3.20), 0.01, True)
        )

        # 顶部为较窄的圆拱：中心切空，而相同高度的两侧仍保留外壳材料。
        self.assertFalse(housing.isInside(App.Vector(center_x, 0.20, 7.45), 0.01, True))
        self.assertTrue(
            housing.isInside(App.Vector(center_x - 1.15, 0.20, 7.45), 0.01, True)
        )

    def test_wire_opening_has_a_shallow_wider_entry_bevel(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        housing = generator.make_housing(profile, 3, 0)
        center_x = profile["pitch"] / 2.0

        # 外缘只在正面浅切放大，进入腔体后应恢复到较小的正式轮廓。
        bevel_point = App.Vector(center_x - 1.32, 0.12, 3.20)
        inner_point = App.Vector(center_x - 1.32, 0.80, 3.20)
        self.assertFalse(housing.isInside(bevel_point, 0.01, True))
        self.assertTrue(housing.isInside(inner_point, 0.01, True))

    def test_top_channel_has_a_sloped_support_below_the_actuator_nose(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        housing = generator.make_housing(profile, 3, 0)
        center_x = profile["pitch"] / 2.0

        # 尖端伸出区域由主体前斜面让空；厚主体进入通道后与槽底保持间隙。
        self.assertFalse(housing.isInside(App.Vector(center_x, 0.15, 9.60), 0.01, True))
        self.assertTrue(housing.isInside(App.Vector(center_x, 1.50, 8.30), 0.01, True))
        self.assertFalse(housing.isInside(App.Vector(center_x, 1.50, 8.60), 0.01, True))

    def test_top_channel_support_height_is_profile_driven(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        raised_support = dict(profile)
        raised_support["top_channel_floor_z"] = 9.0
        housing = generator.make_housing(raised_support, 3, 0)
        center_x = profile["pitch"] / 2.0
        self.assertTrue(housing.isInside(App.Vector(center_x, 4.00, 8.60), 0.01, True))

    def test_exposed_side_has_six_shallow_molded_dimples(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        housing = generator.make_housing(profile, 3, 0)
        expected_centers = (
            (1.65, 8.15),
            (4.65, 7.20),
            (10.65, 8.15),
            (1.65, 1.45),
            (6.25, 1.45),
            (10.65, 3.10),
        )
        for y_pos, z_pos in expected_centers:
            with self.subTest(y=y_pos, z=z_pos):
                self.assertFalse(
                    housing.isInside(App.Vector(0.10, y_pos, z_pos), 0.01, True)
                )
                self.assertTrue(
                    housing.isInside(App.Vector(0.45, y_pos, z_pos), 0.01, True)
                )

    def test_housing_has_front_finger_slope_and_closed_rear_wall(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        housing = generator.make_housing(profile, 3, 0)

        # 前上缘应切出斜坡：靠前高点为空，斜坡后方仍保留实体。
        self.assertFalse(housing.isInside(App.Vector(0.2, 0.2, 9.8), 0.01, True))
        self.assertTrue(housing.isInside(App.Vector(0.2, 2.5, 9.8), 0.01, True))

        # 背面不再开方形凹孔。
        self.assertTrue(housing.isInside(App.Vector(1.75, 11.5, 8.0), 0.01, True))

    def test_side_cover_uses_the_same_front_chamfer_as_housing(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        cover = generator.make_side_cover(profile, 3)
        cover_center_x = 3 * profile["pitch"] + profile["cover_width"] / 2.0
        self.assertFalse(
            cover.isInside(App.Vector(cover_center_x, 0.2, 9.8), 0.01, True)
        )
        self.assertTrue(
            cover.isInside(App.Vector(cover_center_x, 2.5, 9.8), 0.01, True)
        )

    def test_housing_and_side_cover_use_visible_outer_edge_rounding(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        housing = generator.make_housing(profile, 3, 1)
        cover = generator.make_side_cover(profile, 3)

        # 0.30 mm 级圆角应切掉距三向外角各 0.10 mm 的尖角材料。
        self.assertFalse(
            housing.isInside(App.Vector(3.60, 12.40, 0.10), 0.005, True)
        )
        self.assertFalse(
            cover.isInside(App.Vector(11.90, 12.40, 0.10), 0.005, True)
        )

    def test_terminal_pin_centers_match_recommended_pcb_layout(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        pin_1a = generator.make_terminal_pin(profile, 0, 0)
        pin_1b = generator.make_terminal_pin(profile, 0, 1)
        pin_2a = generator.make_terminal_pin(profile, 1, 0)

        self.assertAlmostEqual(pin_1a.BoundBox.Center.x, 2.25, places=6)
        self.assertAlmostEqual(pin_2a.BoundBox.Center.x, 5.75, places=6)
        self.assertAlmostEqual(pin_1a.BoundBox.Center.y, 4.60, places=6)
        self.assertAlmostEqual(pin_1b.BoundBox.Center.y, 9.60, places=6)


if __name__ == "__main__":
    unittest.main()
