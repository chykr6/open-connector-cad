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

    def test_actuator_front_tab_protrudes_and_has_clear_side_slope(self):
        profile = generator.load_profile("DA803", 3.5, CONNECTOR_DIR)
        actuator = generator.make_actuator(profile, 0)
        # 绿色区域切除后，尖端略缩在主体最前缘内，不再向外伸出。
        self.assertGreater(actuator.BoundBox.YMin, 0.05)
        self.assertLess(actuator.BoundBox.YMin, 0.25)

        sloped_edges = []
        for edge in actuator.Edges:
            if not isinstance(edge.Curve, Part.Line) or len(edge.Vertexes) != 2:
                continue
            start = edge.Vertexes[0].Point
            end = edge.Vertexes[1].Point
            dy = abs(end.y - start.y)
            dz = abs(end.z - start.z)
            if dy > 0.8 and dz > 0.4:
                sloped_edges.append(edge)
        self.assertTrue(sloped_edges, "actuator must contain a visible straight sloped edge")

        center_x = profile["pitch"] / 2.0
        # 尖端下方的绿色区域为空，而红色尖端上部仍属于压杆实体。
        self.assertFalse(
            actuator.isInside(App.Vector(center_x, 0.40, 10.40), 0.01, True)
        )
        self.assertTrue(
            actuator.isInside(App.Vector(center_x, 0.40, 10.70), 0.01, True)
        )

        # 长条主体厚度为 2.0 mm，不再是薄片。
        self.assertTrue(
            actuator.isInside(App.Vector(center_x, 5.00, 9.00), 0.01, True)
        )
        self.assertFalse(
            actuator.isInside(App.Vector(center_x, 5.00, 8.80), 0.01, True)
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
