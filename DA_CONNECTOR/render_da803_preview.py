# -*- coding: utf-8 -*-
"""Render an isometric QA preview from the generated FCStd."""

import os

import FreeCAD as App
import FreeCADGui as Gui


base = os.path.dirname(os.path.abspath(__file__))
model = os.path.join(base, "DA803-350-3P.FCStd")
preview = os.path.join(base, "DA803-350-3P-preview.png")

doc = App.openDocument(model)
params = doc.getObject("Parameters")
body_hex = params.BodyColor.lstrip("#") if params else "8C8C8C"
lever_hex = params.LeverColor.lstrip("#") if params else "202020"
body_color = tuple(int(body_hex[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
lever_color = tuple(int(lever_hex[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
for obj in doc.Objects:
    if obj.Name.startswith(("DA803_3P_Assembly", "Pole_", "Housing_", "SideCover", "Lever_", "Pin_")):
        obj.ViewObject.Visibility = True
    if obj.Name.startswith(("Housing_", "SideCover")):
        obj.ViewObject.ShapeColor = body_color
    elif obj.Name.startswith("Lever_"):
        obj.ViewObject.ShapeColor = lever_color
    elif obj.Name.startswith("Pin_"):
        obj.ViewObject.ShapeColor = (0.78, 0.80, 0.82)
doc.recompute()
doc.save()
Gui.updateGui()
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
Gui.activeDocument().activeView().setAnimationEnabled(False)
Gui.updateGui()
Gui.activeDocument().activeView().saveImage(preview, 1200, 900, "White")
print("PREVIEW_OK " + preview)
App.closeDocument(doc.Name)
Gui.getMainWindow().close()
