# -*- coding: utf-8 -*-
"""将生成的 FCStd 保存为轴测 PNG 预览。"""

import argparse
import json
import os

import FreeCAD as App


def preview_path_for_model(model_path):
    return os.path.splitext(str(model_path))[0] + ".png"


def render_model(model_path, output_path=None, width=1200, height=900):
    import FreeCADGui as Gui

    model_path = os.path.abspath(model_path)
    output_path = os.path.abspath(output_path or preview_path_for_model(model_path))
    doc = App.openDocument(model_path)
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    Gui.activeDocument().activeView().saveImage(
        output_path, int(width), int(height), "White"
    )
    App.closeDocument(doc.Name)
    print("RENDER_OK PNG=%s" % output_path)
    return output_path


def request_to_argv(request):
    argv = []
    for key, value in request.items():
        if value is not None and value != "":
            argv.extend(["--" + key.replace("_", "-"), str(value)])
    return argv


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output")
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=900)
    args = parser.parse_args(argv)
    result = render_model(args.model, args.output, args.width, args.height)
    if App.GuiUp and os.environ.get("CONNECTOR_AUTOCLOSE") == "1":
        try:
            import FreeCADGui as Gui

            Gui.getMainWindow().close()
        except Exception:
            pass
    return result


request_json = os.environ.get("CONNECTOR_RENDER_REQUEST_JSON")
if request_json:
    main(request_to_argv(json.loads(request_json)))
elif __name__ == "__main__":
    main()
