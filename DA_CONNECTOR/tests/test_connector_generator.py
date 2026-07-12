# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import unittest

import FreeCAD as App


CONNECTOR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CONNECTOR_DIR not in sys.path:
    sys.path.insert(0, CONNECTOR_DIR)

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


if __name__ == "__main__":
    unittest.main()
