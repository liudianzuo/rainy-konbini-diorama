# -*- coding: utf-8 -*-
"""Build 'Rainy Night Konbini' miniature diorama in Blender 5.2."""
import bpy
import os
import sys
import math
import random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import scene_lib as L
from scene_lib import (
    box, plane, polygon, cylinder, torus, ico, tube, curve_line,
    text_obj, material, emission_material, glass_material,
    area_light, point_light, spot_light, sun_light, point_at,
    anim, fade_light, fade_emission, col, D2R, TAU,
)

random.seed(20261104)

OUT_DIR = HERE
BLEND_PATH = os.path.join(OUT_DIR, "rainy_konbini.blend")
RENDER_DIR = os.path.join(OUT_DIR, "renders")
os.makedirs(RENDER_DIR, exist_ok=True)

# ------------------------------------------------------------------ palette
C = {
    "ink": (0.014, 0.020, 0.042),
    "base_side": (0.050, 0.065, 0.090),
    "base_top": (0.095, 0.105, 0.118),
    "asphalt": (0.060, 0.078, 0.100),
    "asphalt2": (0.085, 0.105, 0.128),
    "sidewalk": (0.43, 0.45, 0.47),
    "sidewalk2": (0.33, 0.35, 0.37),
    "curb": (0.50, 0.52, 0.53),
    "paint": (0.78, 0.80, 0.74),
    "paint_y": (0.92, 0.62, 0.13),
    "steel": (0.27, 0.31, 0.34),
    "steel_dark": (0.10, 0.12, 0.14),
    "alu": (0.38, 0.41, 0.43),
    "concrete": (0.40, 0.41, 0.40),
    "wall": (0.78, 0.74, 0.65),
    "wall_warm": (0.86, 0.79, 0.66),
    "wall_gray": (0.48, 0.48, 0.46),
    "interior_wall": (0.62, 0.55, 0.43),
    "interior_floor": (0.47, 0.41, 0.31),
    "ceiling": (0.68, 0.64, 0.55),
    "white": (0.82, 0.81, 0.76),
    "shelf": (0.78, 0.78, 0.73),
    "wood": (0.42, 0.28, 0.19),
    "wood_dark": (0.24, 0.16, 0.12),
    "green": (0.055, 0.36, 0.21),
    "green_bright": (0.10, 0.58, 0.32),
    "blue": (0.035, 0.17, 0.42),
    "orange": (0.92, 0.41, 0.10),
    "red": (0.72, 0.08, 0.07),
    "pink": (1.0, 0.10, 0.42),
    "cyan": (0.10, 0.75, 0.96),
    "amber": (1.0, 0.58, 0.18),
    "glass_tint": (0.36, 0.52, 0.58),
    "black": (0.025, 0.028, 0.034),
    "tire": (0.022, 0.024, 0.027),
    "plant": (0.035, 0.16, 0.10),
    "plant2": (0.06, 0.24, 0.13),
    "plum": (0.70, 0.20, 0.32),
}

# ------------------------------------------------------------------ materials
M = {}
def build_materials():
    M["base_side"] = material("BaseSide", C["base_side"], rough=.46, metallic=.2)
    M["base_top"] = material("BaseTop", C["base_top"], rough=.55, metallic=.1)
    M["brass"] = material("BrassEdge", (0.55, 0.39, 0.17), rough=.28, metallic=.85)
    M["asphalt"] = material("WetAsphalt", C["asphalt"], rough=.19, metallic=.42)
    M["asphalt2"] = material("WetAsphalt2", C["asphalt2"], rough=.26, metallic=.32)
    M["sidewalk"] = material("Sidewalk", C["sidewalk"], rough=.55, metallic=.08)
    M["sidewalk2"] = material("SidewalkDark", C["sidewalk2"], rough=.52)
    M["curb"] = material("CurbStone", C["curb"], rough=.52)
    M["paint"] = material("RoadPaint", C["paint"], rough=.38, emission=(0.75, 0.78, 0.72), emission_strength=.03)
    M["paint_y"] = material("RoadPaintYellow", C["paint_y"], rough=.4, emission=(0.9, 0.6, 0.1), emission_strength=.04)
    M["puddle"] = material("Puddle", (0.045, 0.085, 0.120), rough=.055, metallic=.62, spec=.8,
                           emission=(0.020, 0.045, 0.070), emission_strength=.35)
    M["ripple"] = emission_material("Ripple", (0.35, 0.78, 1.0), 1.0, base=(0.2, 0.4, 0.5))
    M["steel"] = material("Steel", C["steel"], rough=.38, metallic=.7)
    M["steel_dark"] = material("SteelDark", C["steel_dark"], rough=.42, metallic=.55)
    M["alu"] = material("Aluminium", C["alu"], rough=.3, metallic=.8)
    M["concrete"] = material("Concrete", C["concrete"], rough=.85)
    M["concrete_dark"] = material("ConcreteDark", (0.20, 0.21, 0.21), rough=.9)
    M["wall"] = material("StoreWall", C["wall"], rough=.68)
    M["wall_warm"] = material("StoreWallWarm", C["wall_warm"], rough=.64)
    M["wall_gray"] = material("NeighborWall", C["wall_gray"], rough=.78)
    M["wall_dark"] = material("NeighborDark", (0.12, 0.13, 0.14), rough=.82)
    M["interior_wall"] = material("InteriorWall", C["interior_wall"], rough=.66)
    M["interior_floor"] = material("InteriorFloor", C["interior_floor"], rough=.4, metallic=.05)
    M["ceiling"] = material("CeilingPanel", C["ceiling"], rough=.72)
    M["white"] = material("SoftWhite", C["white"], rough=.5)
    M["shelf"] = material("ShelfWhite", C["shelf"], rough=.45)
    M["wood"] = material("WarmWood", C["wood"], rough=.56)
    M["wood_dark"] = material("DarkWood", C["wood_dark"], rough=.62)
    M["green"] = material("BrandGreen", C["green"], rough=.5)
    M["green_bright"] = material("BrandGreenBright", C["green_bright"], rough=.48)
    M["blue"] = material("BrandBlue", C["blue"], rough=.5)
    M["orange"] = material("BrandOrange", C["orange"], rough=.5)
    M["red"] = material("SignalRed", C["red"], rough=.48)
    M["black"] = material("NearBlack", C["black"], rough=.55)
    M["rubber"] = material("Rubber", (0.018, 0.020, 0.023), rough=.84)
    M["tire"] = material("Tire", C["tire"], rough=.9)
    M["plant"] = material("LeafDark", C["plant"], rough=.72)
    M["plant2"] = material("Leaf", C["plant2"], rough=.68)
    M["trunk"] = material("Trunk", (0.19, 0.13, 0.09), rough=.9)
    M["plum"] = material("Plum", C["plum"], rough=.6)
    M["glass"] = glass_material("StoreGlass", C["glass_tint"], alpha=.055, reflect=.6)
    M["glass_door"] = glass_material("DoorGlass", (0.42, 0.60, 0.65), alpha=.09, reflect=.7)
    M["glass_vend"] = glass_material("VendingGlass", (0.55, 0.75, 0.85), alpha=.22, reflect=.65)
    # Emissive signage
    M["sign_white"] = emission_material("SignWhite", (1.0, 0.88, 0.64), 1.15, base=(0.030, 0.026, 0.020))
    M["sign_white_soft"] = emission_material("SignWhiteSoft", (1.0, 0.78, 0.46), .62, base=(0.025, 0.018, 0.010))
    M["sign_green"] = material("SignGreen", C["green"], rough=.44, emission=C["green"], emission_strength=.25)
    M["sign_blue"] = material("SignBlue", C["blue"], rough=.44, emission=C["blue"], emission_strength=.2)
    M["sign_orange"] = material("SignOrange", C["orange"], rough=.44, emission=C["orange"], emission_strength=.25)
    M["text_dark"] = material("SignText", (0.025, 0.085, 0.065), rough=.4)
    M["ink_unlit"] = L.unlit_material("UnlitInk", (0.006, 0.011, 0.020))
    M["ink_green"] = L.unlit_material("UnlitGreenInk", (0.020, 0.090, 0.055))
    M["unlit_white"] = L.unlit_material("UnlitWhite", (1.0, 0.97, 0.88))
    M["unlit_cream"] = L.unlit_material("UnlitCream", (1.0, 0.88, 0.62))
    M["text_cream"] = emission_material("SignTextCream", (1.0, 0.9, 0.68), 2.2, base=(0.9, 0.84, 0.7))
    M["neon_pink"] = emission_material("NeonPink", (1.0, 0.055, 0.33), 4.0, base=(0.06, 0.004, 0.02))
    M["neon_cyan"] = emission_material("NeonCyan", (0.05, 0.65, 1.0), 3.4, base=(0.004, 0.035, 0.06))
    M["neon_red"] = emission_material("NeonRed", (1.0, 0.12, 0.055), 2.6, base=(0.05, 0.006, 0.003))
    M["neon_warm"] = emission_material("NeonWarm", (1.0, 0.56, 0.18), 2.4, base=(0.05, 0.02, 0.004))
    M["canopy_neon"] = emission_material("CanopyNeon", (0.08, 0.85, 0.42), 1.55, base=(0.010, 0.040, 0.020))
    M["warm_light"] = emission_material("WarmLightPanel", (1.0, 0.64, 0.30), 2.3, base=(0.05, 0.025, 0.008))
    M["cool_light"] = emission_material("CoolLightPanel", (0.62, 0.84, 1.0), 1.6, base=(0.015, 0.04, 0.06))
    M["fridge_light"] = emission_material("FridgeLight", (0.80, 0.94, 1.0), 1.8, base=(0.02, 0.04, 0.055))
    M["screen"] = emission_material("Screen", (0.30, 0.72, 0.62), 1.2, base=(0.02, 0.08, 0.06))
    M["lamp_glass"] = emission_material("LampGlass", (1.0, 0.68, 0.34), 3.8, base=(0.04, 0.018, 0.005))
    M["headlight"] = emission_material("Headlight", (1.0, 0.82, 0.55), 6.0)
    M["rain"] = glass_material("RainStreak", (0.62, 0.80, 1.0), alpha=.30, reflect=.2)
    M["fake_reflect_green"] = emission_material("ReflectGreen", (0.05, 0.55, 0.30), .7, base=(0.03, 0.2, 0.1))
    M["fake_reflect_pink"] = emission_material("ReflectPink", (1.0, 0.12, 0.42), .65, base=(0.4, 0.05, 0.18))
    M["fake_reflect_cyan"] = emission_material("ReflectCyan", (0.15, 0.7, 1.0), .6, base=(0.05, 0.25, 0.4))
    M["fake_reflect_warm"] = emission_material("ReflectWarm", (1.0, 0.66, 0.32), .6, base=(0.4, 0.25, 0.1))
    # Product colours
    prod_colors = [
        (0.86, 0.14, 0.12), (0.95, 0.52, 0.10), (0.95, 0.80, 0.16),
        (0.18, 0.55, 0.26), (0.10, 0.42, 0.72), (0.44, 0.22, 0.56),
        (0.92, 0.45, 0.62), (0.10, 0.66, 0.68), (0.88, 0.87, 0.80),
        (0.55, 0.30, 0.14), (0.62, 0.72, 0.18), (0.25, 0.35, 0.55),
    ]
    for i, cc in enumerate(prod_colors):
        M[f"prod{i}"] = material(f"Product{i}", cc, rough=.45, emission=cc, emission_strength=.05)
    M["price"] = material("PriceTag", (0.96, 0.95, 0.87), rough=.5, emission=(1, 1, .9), emission_strength=.12)
    M["mag1"] = material("Mag1", (0.85, 0.15, 0.30), rough=.5, emission=(0.85, 0.15, 0.30), emission_strength=.05)
    M["mag2"] = material("Mag2", (0.15, 0.45, 0.85), rough=.5, emission=(0.15, 0.45, 0.85), emission_strength=.05)
    M["mag3"] = material("Mag3", (0.95, 0.72, 0.12), rough=.5, emission=(0.95, 0.72, 0.12), emission_strength=.05)
    M["mag4"] = material("Mag4", (0.2, 0.7, 0.45), rough=.5, emission=(0.2, 0.7, 0.45), emission_strength=.05)
    M["food"] = material("HotFood", (0.78, 0.38, 0.10), rough=.42, emission=(0.9, 0.45, 0.1), emission_strength=.2)
    M["coffee"] = material("Coffee", (0.18, 0.08, 0.035), rough=.3)


# ------------------------------------------------------------------ base & street
def build_base():
    box("Plinth", (0, 0, -0.68), (26.3, 26.3, 1.36), M["base_side"],
        "00_Base", bevel=.22, segments=3)
    box("PlinthTop", (0, 0, -0.045), (26.15, 26.15, 0.09), M["base_top"],
        "00_Base", bevel=.04)
    # brass inlay around top edge
    for i, (loc, size) in enumerate([
        ((0, 12.98, 0.022), (25.95, .055, .025)),
        ((0, -12.98, 0.022), (25.95, .055, .025)),
        ((12.98, 0, 0.022), (.055, 25.95, .025)),
        ((-12.98, 0, 0.022), (.055, 25.95, .025)),
    ]):
        box(f"BrassInlay{i}", loc, size, M["brass"], "00_Base", bevel=.01)
    # plaque on front edge
    box("Plaque", (0, -13.21, -0.60), (4.8, .06, .72), M["brass"], "00_Base", bevel=.035)
    text_obj("PlaqueTitle", "雨夜のコンビニ", (0, -13.255, -0.53), .30,
             L.unlit_material("PlaqueDark", (0.015, 0.022, 0.018)),
             "00_Base", rot=(90*D2R, 0, 0), extrude=.004, font=L.FONT_JP)
    text_obj("PlaqueSub", "HOSHIMI MART  /  MINIATURE DIORAMA", (0, -13.257, -0.85), .10,
             L.unlit_material("PlaqueDark2", (0.015, 0.022, 0.018)),
             "00_Base", rot=(90*D2R, 0, 0), extrude=.002, font=L.FONT_EN)



def build_street():
    # asphalt L
    box("AsphaltSouth", (0, -9.35, .005), (26, 7.3, .03), M["asphalt"], "01_Street", bevel=.01)
    box("AsphaltEast", (9.5, 3.85, .005), (7, 18.7, .03), M["asphalt"], "01_Street", bevel=.01)
    # subtle asphalt patches
    for i in range(7):
        x = random.uniform(-12, 12)
        y = random.uniform(-12.5, -6.3)
        polygon(f"PatchS{i}", (x, y, .023), [
            (random.uniform(-1.6, 1.6), random.uniform(-.6, .6)) for _ in range(5)
        ], M["asphalt2"], "01_Street")
    for i in range(4):
        x = random.uniform(6.4, 12.3)
        y = random.uniform(-5.0, 12.2)
        polygon(f"PatchE{i}", (x, y, .023), [
            (random.uniform(-.7, .7), random.uniform(-1.6, 1.6)) for _ in range(5)
        ], M["asphalt2"], "01_Street")

    # sidewalks (slightly raised)
    box("SidewalkSouth", (-3.5, -4.1, .075), (19.0, 3.2, .15), M["sidewalk"], "01_Street", bevel=.025)
    box("SidewalkEast", (4.0, 5.15, .075), (4.0, 18.5, .15), M["sidewalk"], "01_Street", bevel=.025)
    box("SidewalkCorner", (4.0, -4.1, .075), (4.0, 3.2, .15), M["sidewalk"], "01_Street", bevel=.025)
    # sidewalk tile seams
    seam_mat = M["sidewalk2"]
    for i in range(15):
        x = -12.5 + i * 1.2
        if x < 6.0:
            box(f"SeamSx{i}", (x, -4.1, .157), (.018, 3.16, .006), seam_mat, "01_Street")
    for i in range(3):
        y = -5.55 + i * 1.05
        box(f"SeamSy{i}", (-3.5, y, .157), (18.9, .018, .006), seam_mat, "01_Street")
    for i in range(16):
        y = -5.4 + i * 1.2
        box(f"SeamEy{i}", (4.0, y, .157), (3.96, .018, .006), seam_mat, "01_Street")
    for i in range(4):
        x = 2.55 + i * 1.0
        box(f"SeamEx{i}", (x, 5.15, .157), (.018, 18.4, .006), seam_mat, "01_Street")

    # curbs
    box("CurbSouth", (-3.5, -5.68, .12), (19.0, .24, .24), M["curb"], "01_Street", bevel=.04)
    box("CurbEast", (5.98, 5.9, .12), (.24, 19.0, .24), M["curb"], "01_Street", bevel=.04)
    # little rounded curb corner
    cylinder("CurbCorner", (5.98, -5.68, .12), .26, .24, M["curb"], "01_Street", vertices=24, bevel=.03)

    # road paint: center dash and edge lines
    for i in range(9):
        x = -12.2 + i * 2.65
        box(f"CenterDashS{i}", (x, -9.2, .031), (1.45, .12, .012), M["paint"], "01_Street")
    for i in range(7):
        y = -4.6 + i * 2.65
        box(f"CenterDashE{i}", (9.6, y, .031), (.12, 1.45, .012), M["paint"], "01_Street")
    box("EdgeLineSouth", (0, -6.15, .031), (25.2, .09, .012), M["paint"], "01_Street")
    box("EdgeLineEast", (6.55, 4.0, .031), (.09, 18.4, .012), M["paint"], "01_Street")

    # zebra crossing south road
    for i in range(7):
        y = -6.55 - i * .95
        box(f"ZebraS{i}", (8.25, y, .034), (3.4, .38, .014), M["paint"], "01_Street")
    # zebra crossing east road
    for i in range(7):
        x = 6.65 + i * .95
        box(f"ZebraE{i}", (x, -2.55, .034), (.38, 3.1, .014), M["paint"], "01_Street")
    # stop lines
    box("StopLineE", (9.65, -1.0, .034), (6.0, .22, .014), M["paint"], "01_Street")
    box("StopLineS", (11.2, -9.4, .034), (.22, 6.6, .014), M["paint"], "01_Street")
    # directional arrows
    for name, x, y, rot in [("ArrowE", 11.7, 4.9, 0), ("ArrowS", -8.5, -8.0, 90*D2R)]:
        box(name + "_stem", (x, y, .038), (.20, 1.9, .012), M["paint"], "01_Street", rot=(0, 0, rot))
        if name == "ArrowE":
            box(name + "_head1", (x-.28, y+1.15, .038), (.62, .18, .012), M["paint"], "01_Street", rot=(0, 0, 45*D2R))
            box(name + "_head2", (x+.28, y+1.15, .038), (.62, .18, .012), M["paint"], "01_Street", rot=(0, 0, -45*D2R))
        else:
            box(name + "_head1", (x+.28, y-.55, .038), (.62, .18, .012), M["paint"], "01_Street", rot=(0, 0, -45*D2R))
            box(name + "_head2", (x+.28, y+.55, .038), (.62, .18, .012), M["paint"], "01_Street", rot=(0, 0, 45*D2R))

    # parking bay on east road
    box("ParkLine1", (10.1, 1.8, .034), (.10, 5.4, .012), M["paint"], "01_Street")
    box("ParkLine2", (12.75, 1.8, .034), (.10, 5.4, .012), M["paint"], "01_Street")
    box("ParkLine3", (11.42, -0.9, .034), (2.7, .10, .012), M["paint"], "01_Street")
    box("ParkLine4", (11.42, 4.5, .034), (2.7, .10, .012), M["paint"], "01_Street")
    for i, x in enumerate([10.8, 12.05]):
        box(f"WheelStop{i}", (x, 2.0, .10), (.24, .42, .18), M["concrete"], "01_Street", bevel=.03)

    # manholes and gutter grates
    cylinder("Manhole", (10.8, -8.3, .036), .42, .018, M["steel_dark"], "01_Street", vertices=28)
    for i in range(9):
        y = -6.3 + i * 1.0
        box(f"GrateS{i}", (-11.8 + i*1.9, -5.52, .036), (.85, .30, .018), M["steel_dark"], "01_Street")
        for j in range(5):
            box(f"GrateS{i}_slot{j}", (-12.12 + i*1.9 + j*.16, -5.52, .047), (.055, .25, .008), M["black"], "01_Street")
    for i in range(8):
        y = -1.8 + i * 1.4
        box(f"GrateE{i}", (5.86, y, .036), (.30, .95, .018), M["steel_dark"], "01_Street")
        for j in range(5):
            box(f"GrateE{i}_slot{j}", (5.86, y - .38 + j*.19, .047), (.25, .055, .008), M["black"], "01_Street")

    # puddles
    puddles = [
        ("Puddle1", (1.0, -7.35), [(-1.9,-.5),(-.8,-1.2),(1.4,-1.0),(2.6,-.1),(1.9,.65),(-.2,.75),(-1.3,.35)]),
        ("Puddle2", (8.5, -10.6), [(-1.1,-.5),(-.5,-1.2),(1.0,-.9),(1.7,.1),(.8,.8),(-.7,.7)]),
        ("Puddle3", (-8.1, -8.1), [(-2.2,-.4),(-1.4,-1.1),(.7,-1.2),(2.3,-.2),(1.1,.8),(-.8,.9),(-2.0,.5)]),
        ("Puddle4", (11.3, 6.4), [(-.9,-1.5),(.3,-1.8),(1.2,-.8),(1.0,.9),(.1,1.5),(-.9,.8)]),
        ("Puddle5", (2.9, -4.1), [(-1.4,-.3),(-.6,-.8),(.9,-.6),(1.6,.2),(.6,.7),(-.7,.5)]),
    ]
    for name, (x, y), pts in puddles:
        polygon(name, (x, y, .042), pts, M["puddle"], "01_Street")
        # thin fake neon reflection in puddle
        if name in ("Puddle1", "Puddle5"):
            box(name+"_glow1", (x-.3, y, .047), (1.0, .055, .005), M["fake_reflect_green"], "01_Street", rot=(0,0,-.12))
            box(name+"_glow2", (x+.55, y+.18, .047), (.55, .045, .005), M["fake_reflect_warm"], "01_Street", rot=(0,0,.15))
        if name == "Puddle2":
            box(name+"_glow", (x-.1, y, .047), (.9, .06, .005), M["fake_reflect_cyan"], "01_Street", rot=(0,0,.2))
        if name == "Puddle3":
            box(name+"_glow", (x, y, .047), (1.3, .055, .005), M["fake_reflect_pink"], "01_Street", rot=(0,0,-.2))
        # concentric ripples
        for k in range(2):
            torus(name+f"_ripple{k}", (x+random.uniform(-.5,.5), y+random.uniform(-.4,.4), .046),
                  .18 + k*.16, .006, M["ripple"], "01_Street", rot=(0,0,0),
                  major_segments=20, minor_segments=4)
    # wet reflection streaks on road from crosswalk
    for i in range(4):
        box(f"CrosswalkRefl{i}", (8.5, -10.2 + i*.9, .039), (2.8, .10, .006), M["fake_reflect_warm"], "01_Street")

    # tactile paving at corner
    for i in range(7):
        for j in range(2):
            cylinder(f"Tactile{i}_{j}", (4.9 + j*.38, -5.15 + i*.36, .162), .05, .022,
                     M["paint_y"], "01_Street", vertices=12)

    # storm drain box at corner
    box("DrainBox", (5.45, -5.42, .07), (.75, .45, .10), M["steel_dark"], "01_Street", bevel=.02)


# ------------------------------------------------------------------ store shell
def window_frame(name, x, y, z, w, h, mat, collection="02_Building", facing='S', depth=.08, t=.055):
    """Four-strip window frame. facing S = plane normal -Y, E = +X."""
    if facing == 'S':
        box(name+"_top", (x, y, z+h-t/2), (w, depth, t), mat, collection, bevel=.008)
        box(name+"_bot", (x, y, z+t/2), (w, depth, t), mat, collection, bevel=.008)
        box(name+"_l", (x-w/2+t/2, y, z+h/2), (t, depth, h), mat, collection, bevel=.008)
        box(name+"_r", (x+w/2-t/2, y, z+h/2), (t, depth, h), mat, collection, bevel=.008)
    else:
        box(name+"_top", (x, y, z+h-t/2), (depth, w, t), mat, collection, bevel=.008)
        box(name+"_bot", (x, y, z+t/2), (depth, w, t), mat, collection, bevel=.008)
        box(name+"_l", (x, y-w/2+t/2, z+h/2), (depth, t, h), mat, collection, bevel=.008)
        box(name+"_r", (x, y+w/2-t/2, z+h/2), (depth, t, h), mat, collection, bevel=.008)


def build_store_shell():
    # foundations
    box("StoreFoundation", (-3.5, 1.75, .11), (11.1, 8.6, .22), M["concrete_dark"], "02_Building", bevel=.03)
    # solid side / back
    box("StoreLeftWall", (-8.93, 1.75, 0.0), (.20, 8.5, 7.02), M["wall"], "02_Building", bevel=.02, anchor='BOTTOM')
    box("StoreBackWall", (-3.5, 5.92, 0.0), (11.0, .22, 7.02), M["wall"], "02_Building", bevel=.02, anchor='BOTTOM')
    # front base and header
    box("FrontKick", (-3.5, -2.44, 0.0), (11.0, .30, .30), M["steel_dark"], "02_Building", bevel=.015, anchor='BOTTOM')
    box("FrontHeader", (-3.5, -2.45, 2.90), (11.0, .34, .60), M["wall_warm"], "02_Building", bevel=.015, anchor='BOTTOM')
    box("SideKick", (2.02, 1.2, 0.0), (.30, 7.4, .30), M["steel_dark"], "02_Building", bevel=.015, anchor='BOTTOM')
    box("SideHeader", (2.03, 1.25, 2.90), (.34, 7.5, .60), M["wall_warm"], "02_Building", bevel=.015, anchor='BOTTOM')
    # corner column
    box("CornerColumn", (1.82, -2.35, 0.0), (.38, .38, 3.50), M["steel_dark"], "02_Building", bevel=.025, anchor='BOTTOM')

    # front window mullions
    mull_x = [-9.0, -6.55, -4.10, -1.65, -.45, 1.62]
    for i, x in enumerate(mull_x):
        box(f"FrontMullion{i}", (x, -2.47, .28), (.10, .15, 2.64), M["steel_dark"], "02_Building", bevel=.012, anchor='BOTTOM')
    # horizontal sill / transom
    box("FrontTransom", (-3.6, -2.47, 2.84), (10.4, .13, .10), M["steel_dark"], "02_Building", anchor='BOTTOM')
    # glass front panels
    glass_centers = [(-7.78, 2.60), (-5.33, 2.60), (-2.88, 2.60), (-1.05, 2.25)]
    for i, (x, w) in enumerate(glass_centers):
        box(f"FrontGlass{i}", (x, -2.48, .33), (w, .035, 2.49), M["glass"], "02_Building", anchor='BOTTOM')
    # door frame and sliding doors
    box("DoorFrameTop", (0.55, -2.42, 2.80), (2.1, .18, .16), M["steel_dark"], "02_Building", anchor='BOTTOM')
    box("DoorFrameL", (-.49, -2.41, 0.0), (.12, .18, 2.93), M["steel_dark"], "02_Building", anchor='BOTTOM')
    box("DoorFrameR", (1.61, -2.41, 0.0), (.12, .18, 2.93), M["steel_dark"], "02_Building", anchor='BOTTOM')
    # retracted right leaf, open left leaf
    box("DoorLeafL", (-.05, -2.40, .12), (.94, .06, 2.66), M["glass_door"], "02_Building", anchor='BOTTOM')
    box("DoorLeafL_frameB", (-.05, -2.39, .12), (.98, .09, .12), M["steel_dark"], "02_Building", anchor='BOTTOM')
    box("DoorLeafL_frameT", (-.05, -2.39, 2.66), (.98, .09, .12), M["steel_dark"], "02_Building", anchor='BOTTOM')
    box("DoorLeafL_frameL", (-.52, -2.39, .18), (.08, .09, 2.52), M["steel_dark"], "02_Building", anchor='BOTTOM')
    box("DoorLeafL_frameR", (.42, -2.39, .18), (.08, .09, 2.52), M["steel_dark"], "02_Building", anchor='BOTTOM')
    box("DoorHandle", (.24, -2.31, 1.05), (.05, .05, .55), M["alu"], "02_Building", anchor='BOTTOM')
    # sensor + decals
    box("DoorSensor", (0.56, -2.28, 2.90), (.36, .12, .10), M["black"], "02_Building", bevel=.015)
    M["SensorEye"] = emission_material("SensorEye", (0.9, 0.15, 0.1), 3.0)
    box("SensorEye", (0.56, -2.21, 2.90), (.08, .02, .04), M["SensorEye"], "02_Building")
    text_obj("DoorOpenText", "OPEN", (0.55, -2.365, 2.40), .13, M["white"], "02_Building",
             rot=(90*D2R, 0, 0), extrude=.002, font=L.FONT_EN)
    text_obj("DoorAutoText", "自動ドア", (0.55, -2.365, 2.20), .11, M["white"], "02_Building",
             rot=(90*D2R, 0, 0), extrude=.002, font=L.FONT_JP)

    # side glass panes on east
    side_mull_y = [-2.35, -.30, 1.75, 3.80, 4.85]
    for i, y in enumerate(side_mull_y):
        box(f"SideMullion{i}", (2.04, y, .28), (.15, .10, 2.64), M["steel_dark"], "02_Building", bevel=.012, anchor='BOTTOM')
    side_glass = [(-1.32, 1.95), (0.72, 1.95), (2.78, 1.95), (4.32, .95)]
    for i, (y, d) in enumerate(side_glass):
        box(f"SideGlass{i}", (2.03, y, .33), (.035, d, 2.49), M["glass"], "02_Building", anchor='BOTTOM')
    box("SideTransom", (2.04, 1.25, 2.84), (.13, 7.35, .10), M["steel_dark"], "02_Building", anchor='BOTTOM')

    # upper storey
    box("UpperFacade", (-3.5, 1.82, 4.20), (11.05, 8.30, 2.82), M["wall"], "02_Building", bevel=.03, anchor='BOTTOM')
    box("UpperBand", (-3.5, -2.32, 4.20), (11.15, .15, .30), M["steel_dark"], "02_Building", bevel=.015, anchor='BOTTOM')
    # roof slab + parapet
    box("RoofSlab", (-3.5, 1.75, 7.02), (11.25, 8.55, .28), M["wall_gray"], "02_Building", bevel=.025, anchor='BOTTOM')
    box("ParapetS", (-3.5, -2.42, 7.30), (11.3, .18, .50), M["wall"], "02_Building", bevel=.02, anchor='BOTTOM')
    box("ParapetE", (2.1, 1.75, 7.30), (.18, 8.55, .50), M["wall"], "02_Building", bevel=.02, anchor='BOTTOM')
    box("ParapetW", (-9.1, 1.75, 7.30), (.18, 8.55, .50), M["wall"], "02_Building", bevel=.02, anchor='BOTTOM')
    box("ParapetN", (-3.5, 5.95, 7.30), (11.3, .18, .50), M["wall"], "02_Building", bevel=.02, anchor='BOTTOM')

    # canopy
    box("CanopyS", (-3.55, -3.02, 3.08), (11.05, 1.02, .16), M["steel_dark"], "02_Building", bevel=.03, anchor='BOTTOM')
    box("CanopyS_face", (-3.55, -3.52, 3.01), (11.05, .08, .26), M["white"], "02_Building", bevel=.02, anchor='BOTTOM')
    box("CanopyS_stripe", (-3.55, -3.565, 3.02), (10.95, .03, .09), M["canopy_neon"], "02_Building", anchor='BOTTOM')
    box("CanopyE", (2.50, 1.25, 3.08), (1.02, 7.55, .16), M["steel_dark"], "02_Building", bevel=.03, anchor='BOTTOM')
    box("CanopyE_face", (3.02, 1.25, 3.01), (.08, 7.55, .26), M["white"], "02_Building", bevel=.02, anchor='BOTTOM')
    box("CanopyE_stripe", (3.065, 1.25, 3.02), (.03, 7.45, .09), M["canopy_neon"], "02_Building", anchor='BOTTOM')
    # canopy downlights
    for i, x in enumerate([-8.2, -5.5, -2.8, -0.2, 1.5]):
        cylinder(f"CanopyLightS{i}", (x, -3.02, 3.07), .10, .03, M["warm_light"], "02_Building", vertices=16)
    for i, y in enumerate([-1.2, 1.1, 3.4, 5.3]):
        cylinder(f"CanopyLightE{i}", (2.52, y, 3.07), .10, .03, M["warm_light"], "02_Building", vertices=16)

    # upper windows and balcony (south)
    box("BalconySlab", (-3.65, -2.85, 4.64), (4.3, 1.15, .16), M["concrete"], "02_Building", bevel=.03, anchor='BOTTOM')
    box("BalconyRailTop", (-3.65, -3.39, 5.30), (4.3, .06, .06), M["steel"], "02_Building", anchor='BOTTOM')
    box("BalconyRailMid", (-3.65, -3.39, 5.00), (4.3, .04, .04), M["steel"], "02_Building", anchor='BOTTOM')
    for i, x in enumerate([-5.7, -4.55, -3.4, -2.25, -1.6]):
        box(f"BalconyPost{i}", (x, -3.39, 4.80), (.045, .045, .56), M["steel"], "02_Building", anchor='BOTTOM')
    # sliding glass door on balcony
    box("BalconyDoor", (-4.1, -2.36, 4.78), (2.0, .06, 1.62), glass_material("BalconyGlass", (0.30, 0.24, 0.16), .28),
        "02_Building", anchor='BOTTOM')
    window_frame("BalconyDoorFrame", -4.1, -2.32, 4.72, 2.10, 1.76, M["steel_dark"], "02_Building", facing='S', depth=.10)
    # second upper window
    box("UpperWindow1", (0.1, -2.38, 4.86), (1.25, .06, 1.45), glass_material("UpperGlass1", (0.30, 0.22, 0.14), .30),
        "02_Building", anchor='BOTTOM')
    window_frame("UpperWindow1_frame", 0.1, -2.34, 4.80, 1.40, 1.58, M["steel_dark"], "02_Building", facing='S')
    for i, x in enumerate([-7.8, -7.0]):
        box(f"UpperWindow2_{i}", (x, -2.38, 4.90), (1.0, .06, 1.25), glass_material(f"UpperGlass2_{i}", (0.28, 0.2, 0.12), .35),
            "02_Building", anchor='BOTTOM')
        window_frame(f"UpperWindow2Frame_{i}", x, -2.34, 4.84, 1.12, 1.36, M["steel_dark"], "02_Building", facing='S')
    # east upper window
    box("UpperWindowE", (2.08, 3.0, 4.86), (.06, 1.6, 1.35), glass_material("UpperGlassE", (0.30, 0.22, 0.15), .3),
        "02_Building", anchor='BOTTOM')
    window_frame("UpperWindowEFrame", 2.10, 3.0, 4.80, 1.70, 1.48, M["steel_dark"], "02_Building", facing='E')
    # warm curtains behind the upstairs glazing (no people, but a home feels lived in)
    box("CurtainBalcony", (-4.1, -2.45, 4.78), (1.85, .02, 1.54), M["warm_curtain"], "02_Building", anchor='BOTTOM')
    box("CurtainWin1", (0.1, -2.45, 4.86), (1.12, .02, 1.36), M["warm_curtain"], "02_Building", anchor='BOTTOM')
    box("CurtainWin2a", (-7.8, -2.45, 4.90), (.92, .02, 1.16), M["warm_curtain"], "02_Building", anchor='BOTTOM')
    box("CurtainWin2b", (-7.0, -2.45, 4.90), (.92, .02, 1.16), M["cool_window"], "02_Building", anchor='BOTTOM')
    box("CurtainE", (2.045, 3.0, 4.86), (.02, 1.48, 1.24), M["warm_curtain"], "02_Building", anchor='BOTTOM')
    point_light("UpperRoomGlow", (-2.8, -1.5, 5.5), 30, (1.0,0.55,0.22), .4)

    # utility details on facade
    cylinder("DownpipeS", (-8.75, -2.58, 0.0), .055, 3.5, M["steel_dark"], "02_Building", vertices=12, anchor='BOTTOM')
    cylinder("DownpipeE", (2.25, 5.72, 0.0), .055, 3.5, M["steel_dark"], "02_Building", vertices=12, anchor='BOTTOM')
    for i, z in enumerate([1.2, 2.5]):
        box(f"MeterBox{i}", (-8.8, -2.38, z), (.28, .12, .38), M["steel"], "02_Building", bevel=.015)
    for i in range(3):
        cylinder(f"PipeS{i}", (-8.82, -2.30 - i*.08, 0.0), .035, 2.8, M["concrete"], "02_Building", vertices=8, anchor='BOTTOM')

    # rooftop details
    box("StairHouse", (-6.4, 4.2, 7.30), (1.9, 1.7, 1.6), M["wall_gray"], "02_Building", bevel=.03, anchor='BOTTOM')
    box("StairHouseDoor", (-6.4, 3.33, 7.35), (.75, .06, 1.35), M["steel_dark"], "02_Building", anchor='BOTTOM')
    cylinder("WaterTank", (1.0, 4.3, 8.45), .72, 1.35, M["white"], "02_Building", vertices=24, anchor='BOTTOM')
    for i, z in enumerate([8.55, 9.70]):
        torus(f"WaterTankRing{i}", (1.0, 4.3, z), .74, .035, M["steel"], "02_Building", rot=(0,0,0), major_segments=24, minor_segments=5)
    for i in range(4):
        a = TAU * i / 4
        cylinder(f"TankLeg{i}", (1.0 + .5*math.cos(a), 4.3 + .5*math.sin(a), 7.30), .04, 1.15, M["steel"], "02_Building",
                 vertices=8, anchor='BOTTOM')
    # antenna
    cylinder("AntennaMast", (-8.2, 4.8, 7.30), .035, 1.4, M["steel"], "02_Building", vertices=8, anchor='BOTTOM')
    for i in range(3):
        box(f"AntennaBar{i}", (-8.2, 4.8, 7.75 + i*.22), (1.2 - i*.2, .035, .035), M["steel"], "02_Building")
    # roof vent
    cylinder("RoofVent", (-2.0, 5.0, 7.30), .15, .55, M["steel"], "02_Building", vertices=16, anchor='BOTTOM')
    cylinder("RoofVentCap", (-2.0, 5.0, 7.88), .22, .08, M["steel_dark"], "02_Building", vertices=16)

    # store sign band (main south)
    build_signage()


def build_rooftop_life():
    # laundry pole and two towels on the roof
    for i, x in enumerate([-5.0, -2.0]):
        cylinder(f"LaundryPole{i}", (x, 5.15, 7.30), .035, 1.85, M["steel"], "02_Building", vertices=8, anchor='BOTTOM')
    cylinder("LaundryBar", (-3.5, 5.15, 8.85), .028, 3.2, M["steel"], "02_Building", vertices=8, rot=(0,90*D2R,0))
    box("Towel1", (-4.2, 5.15, 8.25), (.66, .03, .95), M["white"], "02_Building", bevel=.01, anchor='BOTTOM')
    box("Towel2", (-2.9, 5.15, 8.38), (.58, .03, .72), M["sign_blue"], "02_Building", bevel=.01, anchor='BOTTOM')
    # satellite dish
    cylinder("SatelliteDish", (-7.8, 4.0, 7.98), .42, .05, M["white"], "02_Building",
             vertices=24, rot=(64*D2R, 0, 0))
    cylinder("SatelliteMast", (-7.8, 4.0, 7.30), .035, .70, M["steel"], "02_Building", vertices=8, anchor='BOTTOM')
    # potted plants along the parapet
    for i, (x, y, r) in enumerate([(-8.55, -1.8, .18), (-8.0, -1.85, .15), (-2.0, -2.0, .16)]):
        cylinder(f"RoofPot{i}", (x, y, 7.30), r, .30, M["wood_dark"], "02_Building", vertices=10, anchor='BOTTOM')
        ico(f"RoofPlant{i}", (x, y, 7.64), r*1.4, M["leaf2"] if i%2 else M["leaf1"], "02_Building", subdiv=2, scale=(1,1,1.2))
    # balcony planter
    box("BalconyPlanter", (-1.35, -3.10, 4.66), (.65, .28, .25), M["wood_dark"], "02_Building", bevel=.01, anchor='BOTTOM')
    for i in range(3):
        ico(f"BalconyPlant{i}", (-1.55+i*.20, -3.10, 4.98), .16, M["leaf3"] if i==1 else M["leaf1"],
            "02_Building", subdiv=2, scale=(.9,1.1,1.3))
    # rooftop vent hood
    cylinder("KitchenHood", (-7.2, 5.4, 7.30), .20, .55, M["steel"], "02_Building", vertices=14, anchor='BOTTOM')
    cylinder("KitchenHoodCap", (-7.2, 5.4, 7.83), .26, .08, M["steel_dark"], "02_Building", vertices=14)


def INKTEXT(name, body, loc, size, mat=None, coll="02_Building", rot=(90*D2R,0,0), extrude=.008, font=None, spacing=1.0):
    return text_obj(name, body, loc, size, M["ink_unlit"], coll, rot=rot, extrude=extrude, font=font, spacing=spacing)


# ------------------------------------------------------------------ signage
def build_signage():
    # main fascia lightbox
    box("SignBoxS", (-3.65, -2.63, 3.78), (10.75, .24, .86), M["sign_white"], "02_Building", bevel=.035)
    box("SignBoxS_top", (-3.65, -2.755, 4.205), (10.85, .05, .06), M["steel_dark"], "02_Building")
    box("SignBoxS_bot", (-3.65, -2.755, 3.355), (10.85, .05, .06), M["steel_dark"], "02_Building")
    box("SignBoxS_l", (-9.045, -2.755, 3.78), (.06, .05, .90), M["steel_dark"], "02_Building")
    box("SignBoxS_r", (1.745, -2.755, 3.78), (.06, .05, .90), M["steel_dark"], "02_Building")
    # green logo block on left
    box("SignLogoBlock", (-8.25, -2.765, 3.78), (1.25, .04, .74), M["sign_green"], "02_Building", bevel=.02)
    # simple star logo
    star_mat = M["sign_white"]
    for i in range(4):
        box(f"SignStar{i}", (-8.25, -2.80, 3.78), (.52, .02, .10), star_mat, "02_Building", rot=(0, 0, i*45*D2R))
    INKTEXT("SignEnglish", "HOSHIMI MART", (-2.9, -2.785, 3.92), .48, M["text_dark"], "02_Building",
             rot=(90*D2R, 0, 0), extrude=.012, font=L.FONT_EN, spacing=1.02)
    INKTEXT("SignJapanese", "ほしみマート", (-2.9, -2.792, 3.54), .25, M["text_dark"], "02_Building",
             rot=(90*D2R, 0, 0), extrude=.006, font=L.FONT_JP)
    INKTEXT("Sign24H", "24H", (1.02, -2.795, 3.78), .26, M["text_dark"], "02_Building",
             rot=(90*D2R, 0, 0), extrude=.006, font=L.FONT_EN)
    # colour stripe under sign
    box("SignStripeG", (-6.6, -2.70, 3.36), (4.1, .03, .08), M["sign_green"], "02_Building")
    box("SignStripeB", (-2.6, -2.70, 3.36), (3.8, .03, .08), M["sign_blue"], "02_Building")
    box("SignStripeO", (1.0, -2.70, 3.36), (3.1, .03, .08), M["sign_orange"], "02_Building")

    # east fascia sign (facing +X)
    box("SignBoxE", (2.08, 1.3, 3.80), (.24, 7.55, .82), M["sign_white"], "02_Building", bevel=.03)
    INKTEXT("SignEnglishE", "HOSHIMI MART", (2.215, 1.3, 3.90), .34, M["text_dark"], "02_Building",
             rot=(90*D2R, 0, 90*D2R), extrude=.008, font=L.FONT_EN)
    INKTEXT("SignJapaneseE", "ほしみマート", (2.215, 1.3, 3.55), .18, M["text_dark"], "02_Building",
             rot=(90*D2R, 0, 90*D2R), extrude=.005, font=L.FONT_JP)
    box("SignStripeE", (2.215, 1.3, 3.45), (.03, 7.3, .07), M["sign_green"], "02_Building")

    # corner blade sign: two panels forming corner volume
    box("BladeSign", (2.32, -2.72, 4.55), (.42, .42, 2.15), M["sign_white"], "02_Building", bevel=.04, rot=(0,0,45*D2R))
    box("BladeSignCap", (2.32, -2.72, 5.64), (.50, .50, .08), M["sign_green"], "02_Building", rot=(0,0,45*D2R), bevel=.02)
    text_obj("BladeText1", "24H", (2.50, -2.90, 4.95), .30, M["green"], "02_Building",
             rot=(90*D2R, 0, 45*D2R), extrude=.008, font=L.FONT_EN)
    text_obj("BladeText2", "ほしみ", (2.49, -2.89, 4.45), .22, M["orange"], "02_Building",
             rot=(90*D2R, 0, 45*D2R), extrude=.006, font=L.FONT_JP)
    # a readable south face for the projecting corner sign
    box("BladeSouthPanel", (2.32, -3.035, 4.55), (.56, .026, 1.78), M["sign_green"], "02_Building", bevel=.015)
    box("BladeSouthStripe", (2.32, -3.050, 3.72), (.58, .012, .10), M["sign_orange"], "02_Building")
    text_obj("BladeSouth24", "24H", (2.32, -3.055, 5.26), .20, M["unlit_white"], "02_Building",
             rot=(90*D2R,0,0), extrude=.002, font=L.FONT_EN)
    for i, ch in enumerate(["ほ", "し", "み"]):
        text_obj(f"BladeSouthJP{i}", ch, (2.32, -3.058, 4.92-i*.29), .19, M["unlit_cream"], "02_Building",
                 rot=(90*D2R,0,0), extrude=.002, font=L.FONT_JP)
    text_obj("BladeSouthMart", "MART", (2.32, -3.059, 3.98), .09, M["unlit_white"], "02_Building",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)
    # string of warm bulbs under the canopy edge
    for i in range(9):
        x = -8.45 + i * 1.30
        cylinder(f"CanopyBulb{i}", (x, -3.55, 3.03), .035, .055, M["warm_light"], "02_Building", vertices=10)
    # little projecting hot-food / ATM signs above the glass
    for i, (x, col, txt) in enumerate([(-5.2, M["sign_orange"], "HOT"), (-1.7, M["sign_blue"], "ATM")]):
        box(f"MiniSign{i}", (x, -2.535, 2.58), (.50, .025, .20), col, "02_Building", bevel=.01)
        text_obj(f"MiniSignText{i}", txt, (x, -2.552, 2.58), .10, M["unlit_white"], "02_Building",
                 rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)
    # under-sign spot lamps
    for i, x in enumerate([-7.6, -4.3, -.7]):
        box(f"SignGooseneck{i}", (x, -2.90, 3.32), (.05, .05, .18), M["steel_dark"], "02_Building", anchor='BOTTOM')
        cylinder(f"SignLamp{i}", (x, -3.04, 3.31), .09, .10, M["lamp_glass"], "02_Building", vertices=12, rot=(90*D2R,0,0))


# ------------------------------------------------------------------ interior
def build_interior():
    # floor and ceiling
    box("InteriorFloor", (-3.5, 1.75, .225), (10.75, 8.15, .12), M["interior_floor"], "03_Interior", bevel=.02)
    # tile seams on floor
    for i in range(9):
        x = -8.6 + i * 1.2
        box(f"FloorSeamX{i}", (x, 1.7, .288), (.012, 7.9, .004), M["ceiling"], "03_Interior")
    for i in range(6):
        y = -2.1 + i * 1.3
        box(f"FloorSeamY{i}", (-3.5, y, .288), (10.5, .012, .004), M["ceiling"], "03_Interior")
    box("InteriorCeiling", (-3.5, 1.75, 3.03), (10.75, 8.15, .14), M["ceiling"], "03_Interior", bevel=.02)
    # light panels in ceiling
    for ix, x in enumerate([-7.2, -5.1, -3.0, -.9, 1.0]):
        for iy, y in enumerate([-1.1, 1.2, 3.5, 5.2]):
            box(f"CeilPanel{ix}_{iy}", (x, y, 2.945), (.92, .28, .035), M["warm_light"], "03_Interior", bevel=.01)
    # tracks and spots
    for i, y in enumerate([-0.8, 2.0, 4.8]):
        box(f"CeilTrack{i}", (-3.5, y, 2.9), (10.2, .06, .05), M["steel_dark"], "03_Interior", anchor='BOTTOM')
        for j, x in enumerate([-7.2, -4.6, -2.0, .7]):
            cylinder(f"CeilSpot{i}_{j}", (x, y, 2.84), .085, .10, M["warm_light"], "03_Interior", vertices=12)
    # back wall / office door
    box("BackWallIn", (-3.5, 5.78, 0.0), (10.75, .10, 3.0), M["interior_wall"], "03_Interior", bevel=.02, anchor='BOTTOM')
    box("BackOfficeDoor", (-1.2, 5.70, .05), (.95, .07, 2.15), M["steel_dark"], "03_Interior", anchor='BOTTOM')
    box("BackOfficeDoorWin", (-1.2, 5.655, 1.55), (.65, .02, .70), glass_material("OfficeGlass", (0.2,0.25,0.2), .4), "03_Interior", anchor='BOTTOM')
    box("BackOfficeSign", (-1.2, 5.63, 2.45), (.7, .02, .20), M["sign_white_soft"], "03_Interior", anchor='BOTTOM')
    text_obj("BackOfficeText", "STAFF ONLY", (-1.2, 5.615, 2.45), .10, M["text_dark"], "03_Interior",
             rot=(90*D2R,0,0), extrude=.003, font=L.FONT_EN)
    # back walls posters
    for i, (x, mat, txt) in enumerate([(-6.6, M["mag2"], "SAFE"), (-5.4, M["mag1"], "HOT"), (-4.2, M["mag4"], "NEW")]):
        box(f"BackPoster{i}", (x, 5.715, 1.35), (.85, .03, 1.0), mat, "03_Interior", bevel=.01, anchor='BOTTOM')
        text_obj(f"BackPosterText{i}", txt, (x, 5.69, 2.45), .15, M["white"], "03_Interior",
                 rot=(90*D2R,0,0), extrude=.002, font=L.FONT_EN)
    # fridge bank along back wall
    build_fridges()
    # central gondola shelving
    build_gondolas()
    # window magazine rack
    build_magazine_rack()
    # checkout counter
    build_counter()
    # ATM, coffee, posters, hanging signs
    build_interior_extras()
    build_interior_graphics()


def build_fridges():
    x0 = -8.35
    n = 6
    unit_w = 1.02
    for i in range(n):
        x = x0 + i * unit_w
        # open-front refrigerated case
        box(f"FridgeBack{i}", (x, 5.58, .02), (unit_w - .06, .18, 2.55), M["shelf"], "03_Interior", bevel=.02, anchor='BOTTOM')
        box(f"FridgeSideL{i}", (x - unit_w/2 + .04, 5.24, .02), (.08, .58, 2.55), M["shelf"], "03_Interior", bevel=.01, anchor='BOTTOM')
        box(f"FridgeSideR{i}", (x + unit_w/2 - .04, 5.24, .02), (.08, .58, 2.55), M["shelf"], "03_Interior", bevel=.01, anchor='BOTTOM')
        box(f"FridgeBottom{i}", (x, 5.24, .02), (unit_w - .10, .58, .18), M["shelf"], "03_Interior", anchor='BOTTOM')
        box(f"FridgeTop{i}", (x, 5.24, 2.44), (unit_w - .10, .58, .13), M["shelf"], "03_Interior", anchor='BOTTOM')
        box(f"FridgeCav{i}", (x, 5.48, .18), (unit_w - .14, .03, 2.22), M["cool_light"], "03_Interior", anchor='BOTTOM')
        # shelves + bottles
        for s in range(4):
            z = .55 + s * .42
            box(f"FridgeShelf{i}_{s}", (x, 5.20, z), (unit_w - .14, .48, .035), M["shelf"], "03_Interior", anchor='BOTTOM')
            for b in range(4):
                yy = 5.08 + (b % 2) * .16
                r = .052
                colr = M[f"prod{(i*4+s*3+b) % 12}"]
                cylinder(f"Bottle{i}_{s}_{b}", (x - .30 + b*.20, yy, z + .04), r, .20, colr,
                         "03_Interior", vertices=8, anchor='BOTTOM')
        # little price strips on the shelf noses
        for s in range(4):
            z = .55 + s * .42
            box(f"FridgePrice{i}_{s}", (x, 4.955, z + .02), (unit_w - .22, .012, .06), M["price"], "03_Interior", anchor='BOTTOM')
        # glass doors with frames
        box(f"FridgeDoorGlass{i}", (x, 4.92, .10), (unit_w - .12, .02, 2.35), glass_material(f"FridgeDoorGlass{i}", (0.55,0.75,0.85), .16, .6),
            "03_Interior", anchor='BOTTOM')
        box(f"FridgeDoorFrameL{i}", (x - unit_w/2 + .07, 4.91, .08), (.05, .04, 2.45), M["steel"], "03_Interior", anchor='BOTTOM')
        box(f"FridgeDoorFrameR{i}", (x + unit_w/2 - .07, 4.91, .08), (.05, .04, 2.45), M["steel"], "03_Interior", anchor='BOTTOM')
        box(f"FridgeHandle{i}", (x + .30, 4.88, 1.20), (.04, .06, .55), M["steel"], "03_Interior", anchor='BOTTOM')
        # top brand strip
        box(f"FridgeBrand{i}", (x, 4.90, 2.55), (unit_w - .12, .04, .14), M["sign_blue"], "03_Interior", anchor='BOTTOM')
        text_obj(f"FridgeBrandText{i}", "COLD DRINK", (x, 4.875, 2.57), .065, M["white"], "03_Interior",
                 rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)


def build_gondolas():
    # two island shelf runs
    for gi, x in enumerate([-6.35, -4.05]):
        y0, y1 = .35, 3.45
        # base plinth
        box(f"GondolaBase{gi}", (x, (y0+y1)/2, .12), (.95, y1-y0, .22), M["steel_dark"], "03_Interior", bevel=.02, anchor='BOTTOM')
        # vertical ends
        for i, y in enumerate([y0, y1]):
            box(f"GondolaEnd{gi}_{i}", (x, y, .12), (.97, .06, 1.55), M["shelf"], "03_Interior", bevel=.01, anchor='BOTTOM')
        # shelves, both sides
        for s in range(4):
            z = .55 + s * .38
            box(f"GondolaShelf{gi}_{s}", (x, (y0+y1)/2, z), (.86, y1-y0-.20, .045), M["shelf"], "03_Interior", anchor='BOTTOM')
            for side in [-1, 1]:
                yy = (y0+y1)/2
                # uprights near ends
                for k in range(8):
                    py = y0 + .25 + k * .42
                    if py > y1 - .15:
                        continue
                    mat = M[f"prod{(gi*5+s*3+k+ (0 if side==1 else 2)) % 12}"]
                    box(f"ProductG{gi}_{s}_{side}_{k}", (x + side*.38, py, z + .12), (.16, .28, .20), mat, "03_Interior", bevel=.008, anchor='BOTTOM')
                    box(f"PriceG{gi}_{s}_{side}_{k}", (x + side*.47, py-.01, z + .055), (.012, .20, .08), M["price"], "03_Interior", anchor='BOTTOM')
        # top header
        box(f"GondolaHeader{gi}", (x, (y0+y1)/2, 2.02), (.92, y1-y0-.15, .34), M["sign_white_soft"], "03_Interior", bevel=.02, anchor='BOTTOM')
        text_obj(f"GondolaHeaderText{gi}", "おにぎり・パン・日用品", (x, (y0+y1)/2, 2.04), .16, M["text_dark"], "03_Interior",
                 rot=(90*D2R,0,0), extrude=.002, font=L.FONT_JP)
    # small endcap display near front
    box("Endcap", (-6.35, -.15, .15), (1.0, .55, 1.05), M["shelf"], "03_Interior", bevel=.02, anchor='BOTTOM')
    for i in range(6):
        box(f"EndcapItem{i}", (-6.65 + i*.13, -.15, .98), (.10, .16, .22), M[f"prod{i%12}"], "03_Interior", bevel=.006, anchor='BOTTOM')


def build_magazine_rack():
    # low magazine rack along south window, lets you see over it
    box("MagRack", (-7.25, -1.82, .12), (2.65, .50, .92), M["shelf"], "03_Interior", bevel=.02, anchor='BOTTOM')
    for row in range(3):
        z = .18 + row * .26
        for i in range(6):
            x = -8.35 + i * .40
            mat = M[["mag1","mag2","mag3","mag4"][(row+i) % 4]]
            box(f"Magazine{row}_{i}", (x, -1.48, z), (.30, .035, .22), mat, "03_Interior", bevel=.004, anchor='BOTTOM', rot=(14*D2R,0,0))
    # small crisp display
    box("SnackRack", (-4.9, -1.78, .12), (1.4, .5, .82), M["shelf"], "03_Interior", bevel=.02, anchor='BOTTOM')
    for i in range(5):
        for j in range(2):
            box(f"Snack{i}_{j}", (-5.45 + i*.27, -1.64 + j*.18, .76), (.18, .16, .24), M[f"prod{(i+j*3)%12}"], "03_Interior",
                bevel=.005, anchor='BOTTOM')


def build_counter():
    # main counter
    box("CounterBase", (-.45, 2.25, .08), (3.1, .78, .85), M["shelf"], "03_Interior", bevel=.03, anchor='BOTTOM')
    box("CounterTop", (-.45, 2.25, .93), (3.24, .88, .10), M["wood"], "03_Interior", bevel=.02, anchor='BOTTOM')
    box("CounterFrontPanel", (-.45, 1.845, .12), (3.12, .04, .72), M["sign_green"], "03_Interior", anchor='BOTTOM')
    # back return
    box("CounterReturn", (1.02, 3.15, .08), (1.02, 1.35, .85), M["shelf"], "03_Interior", bevel=.03, anchor='BOTTOM')
    box("CounterReturnTop", (1.02, 3.15, .93), (1.12, 1.45, .10), M["wood"], "03_Interior", bevel=.02, anchor='BOTTOM')
    # register / POS
    box("RegisterBase", (-1.0, 2.26, 1.03), (.38, .28, .12), M["black"], "03_Interior", bevel=.015, anchor='BOTTOM')
    box("RegisterStem", (-1.0, 2.18, 1.10), (.08, .08, .28), M["steel_dark"], "03_Interior", anchor='BOTTOM')
    box("RegisterScreen", (-1.0, 2.12, 1.34), (.48, .05, .30), M["screen"], "03_Interior", anchor='BOTTOM', rot=(-12*D2R,0,0))
    box("CardReader", (-.55, 2.34, 1.03), (.22, .18, .10), M["black"], "03_Interior", bevel=.012, anchor='BOTTOM')
    box("ReceiptPrinter", (-1.45, 2.28, 1.03), (.28, .24, .13), M["black"], "03_Interior", bevel=.012, anchor='BOTTOM')
    # hot snack case
    build_hot_case()
    # coffee machine on return
    build_coffee_machine()
    # cigarette rack behind
    box("CigaretteRack", (1.73, 2.78, .45), (.16, 2.15, 1.95), M["shelf"], "03_Interior", bevel=.02, anchor='BOTTOM')
    for r in range(5):
        for c in range(9):
            y = 1.85 + c * .21
            z = .65 + r * .27
            box(f"CigPack{r}_{c}", (1.63, y, z), (.10, .13, .17), M[f"prod{(r*3+c)%12}"], "03_Interior", bevel=.004, anchor='BOTTOM')
    text_obj("CigRackText", "たばこ", (1.73, 2.7, 2.52), .17, M["text_dark"], "03_Interior",
             rot=(90*D2R,0,0), extrude=.002, font=L.FONT_JP)
    # small hanging menu signs
    for i, (x, txt, mat) in enumerate([(-2.1, "ホット", M["orange"]), (-1.2, "コーヒー", M["wood"]), (1.1, "ATM", M["sign_blue"])]):
        box(f"HangingSign{i}", (x, 1.62, 2.62), (.45, .04, .22), mat, "03_Interior", bevel=.01)
        text_obj(f"HangingText{i}", txt, (x, 1.595, 2.62), .10, M["white"], "03_Interior",
                 rot=(90*D2R,0,0), extrude=.002, font=L.FONT_JP)
    # countertop clutter
    cylinder("CupStack", (-.2, 2.45, 1.03), .10, .22, M["white"], "03_Interior", vertices=14, anchor='BOTTOM')
    box("NapkinBox", (0.3, 2.62, 1.03), (.22, .14, .10), M["white"], "03_Interior", bevel=.01, anchor='BOTTOM')
    box("DonationBox", (1.3, 3.75, 1.03), (.22, .22, .25), glass_material("DonationGlass", (0.8,0.7,0.4), .25), "03_Interior", anchor='BOTTOM')
    # floor mat inside door
    box("InnerMat", (0.55, -1.05, .29), (1.55, 1.15, .035), M["green"], "03_Interior", bevel=.01, anchor='BOTTOM')
    text_obj("InnerMatText", "WELCOME", (0.55, -1.05, .313), .16, M["white"], "03_Interior",
             rot=(0,0,0), extrude=.001, font=L.FONT_EN)


def build_hot_case():
    box("HotCaseBase", (-1.85, 1.82, 1.03), (.62, .48, .16), M["steel_dark"], "03_Interior", bevel=.02, anchor='BOTTOM')
    for i in range(3):
        box(f"HotCaseGlass{i}", (-2.15 + i*.30, 1.82, 1.19), (.02, .46, .42), glass_material(f"HotGlass{i}", (0.8,0.7,0.5), .2), "03_Interior", anchor='BOTTOM')
    box("HotCaseTop", (-1.85, 1.82, 1.61), (.70, .52, .06), M["steel"], "03_Interior", anchor='BOTTOM')
    for i in range(4):
        cylinder(f"Sausage{i}", (-2.05 + i*.13, 1.78, 1.23), .045, .20, M["food"], "03_Interior", vertices=10, rot=(0,90*D2R,0))
    box("HotCaseLight", (-1.85, 1.82, 1.53), (.55, .32, .02), M["warm_light"], "03_Interior", anchor='BOTTOM')
    text_obj("HotCaseText", "HOT", (-1.85, 1.58, 1.10), .10, M["orange"], "03_Interior",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)


def build_coffee_machine():
    box("CoffeeBody", (.85, 3.25, 1.03), (.50, .48, .72), M["black"], "03_Interior", bevel=.04, anchor='BOTTOM')
    box("CoffeeFace", (.85, 3.00, 1.24), (.40, .03, .35), M["sign_white_soft"], "03_Interior", anchor='BOTTOM')
    box("CoffeePanel", (.85, 2.97, 1.29), (.30, .02, .18), M["screen"], "03_Interior", anchor='BOTTOM')
    box("CoffeeTray", (.85, 2.93, 1.07), (.34, .22, .03), M["steel"], "03_Interior", anchor='BOTTOM')
    cylinder("CoffeeCup", (.85, 2.92, 1.10), .055, .10, M["white"], "03_Interior", vertices=12, anchor='BOTTOM')
    text_obj("CoffeeText", "COFFEE", (.85, 3.02, 1.52), .09, M["text_dark"], "03_Interior",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)


def build_interior_extras():
    # ATM at back-left
    box("ATM", (-8.1, 4.55, 0.0), (.72, .72, 1.55), M["steel"], "03_Interior", bevel=.03, anchor='BOTTOM')
    box("ATMFace", (-8.1, 4.18, .82), (.54, .05, .72), M["sign_blue"], "03_Interior", anchor='BOTTOM')
    box("ATMScreen", (-8.1, 4.145, 1.05), (.38, .02, .26), M["screen"], "03_Interior", anchor='BOTTOM')
    text_obj("ATMText", "ATM", (-8.1, 4.13, 1.36), .16, M["white"], "03_Interior",
             rot=(90*D2R,0,0), extrude=.002, font=L.FONT_EN)
    # poster wall near ATM
    for i, (x, mat, txt) in enumerate([(-7.2, M["mag4"], "POST"), (-6.35, M["mag1"], "SALE")]):
        box(f"PosterWall{i}", (x, 5.71, 1.38), (.75, .025, .80), mat, "03_Interior", bevel=.005, anchor='BOTTOM')
        text_obj(f"PosterWallText{i}", txt, (x, 5.69, 1.48), .13, M["white"], "03_Interior",
                 rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)
    # community board inside near window
    box("WindowPosterA", (-8.65, -2.20, 1.95), (.55, .03, .90), M["sign_green"], "03_Interior", anchor='BOTTOM')
    text_obj("WindowPosterAText", "コピー", (-8.65, -2.23, 2.15), .14, M["white"], "03_Interior",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_JP)
    box("WindowPosterB", (-4.55, -2.20, 1.95), (.55, .03, .90), M["sign_orange"], "03_Interior", anchor='BOTTOM')
    text_obj("WindowPosterBText", "からあげ", (-4.55, -2.23, 2.10), .13, M["white"], "03_Interior",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_JP)
    # small plant inside
    cylinder("InnerPot", (-2.6, 4.9, .35), .12, .24, M["wood_dark"], "03_Interior", vertices=12, anchor='BOTTOM')
    ico("InnerPlant", (-2.6, 4.9, .68), .28, M["plant2"], "03_Interior", subdiv=2, scale=(1,1,1.2))


def build_interior_graphics():
    # hanging aisle banners inside, facing the street
    for i, (x, y, col, txt) in enumerate([
        (-7.6, 2.05, M["sign_orange"], "HOT"),
        (-3.0, 2.15, M["sign_green"], "FRESH"),
        (0.8, 1.55, M["sign_blue"], "ATM"),
    ]):
        box(f"AisleBanner{i}", (x, y, 2.38), (.55, .03, .74), col, "03_Interior", bevel=.01)
        text_obj(f"AisleBannerText{i}", txt, (x, y-.025, 2.46), .13, M["unlit_white"], "03_Interior",
                 rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)
        box(f"AisleBannerRod{i}", (x, y, 2.77), (.60, .025, .025), M["steel_dark"], "03_Interior")
    # glass decals / window lettering
    for txt, x, z, sz, col, font in [
        ("24H", -8.15, 1.62, .26, M["ink_green"], L.FONT_EN),
        ("ATM", -3.72, 2.18, .16, M["sign_blue"], L.FONT_EN),
        ("COFFEE", -5.50, 1.48, .12, M["ink_unlit"], L.FONT_EN),
        ("コピー", -7.72, 2.25, .11, M["ink_green"], L.FONT_JP),
    ]:
        text_obj(f"GlassDecal_{txt}", txt, (x, -2.515, z), sz, col, "03_Interior",
                 rot=(90*D2R,0,0), extrude=.001, font=font)
    # shopping basket stack just inside the door
    for i in range(5):
        box(f"Basket{i}", (1.32, -1.22, .32 + i*.055), (.52, .36, .17),
            M["sign_green"] if i % 2 == 0 else M["sign_blue"], "03_Interior", bevel=.02, anchor='BOTTOM')
        box(f"BasketInner{i}", (1.32, -1.22, .405 + i*.055), (.44, .28, .025), M["black"], "03_Interior", anchor='BOTTOM')
    # bright promo cards on the counter glass
    box("PromoCard1", (-1.6, 1.815, 1.05), (.35, .02, .46), M["mag1"], "03_Interior", bevel=.005, anchor='BOTTOM')
    box("PromoCard2", (-.75, 1.815, 1.02), (.30, .02, .40), M["mag3"], "03_Interior", bevel=.005, anchor='BOTTOM')
    text_obj("PromoText1", "NEW", (-1.6, 1.800, 1.26), .10, M["unlit_white"], "03_Interior",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)
    text_obj("PromoText2", "SALE", (-.75, 1.800, 1.21), .09, M["ink_unlit"], "03_Interior",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)
    # floor direction decal
    box("FloorArrowStem", (0.55, -1.75, .302), (.13, .52, .006), M["sign_green"], "03_Interior")
    box("FloorArrowHeadL", (0.45, -2.02, .302), (.30, .11, .006), M["sign_green"], "03_Interior", rot=(0,0,45*D2R))
    box("FloorArrowHeadR", (0.65, -2.02, .302), (.30, .11, .006), M["sign_green"], "03_Interior", rot=(0,0,-45*D2R))
    # back wall brand panel
    box("BackBrandPanel", (-4.1, 5.705, 2.42), (2.6, .02, .52), M["sign_green"], "03_Interior", bevel=.01)
    text_obj("BackBrandText", "HOSHIMI MART", (-4.1, 5.680, 2.44), .20, M["unlit_white"], "03_Interior",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)
    text_obj("BackBrandJp", "ほしみマート 24H", (-4.1, 5.679, 2.27), .10, M["unlit_cream"], "03_Interior",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_JP)


# ==================================================================
# EXTRA STREET LIFE
# ==================================================================
def build_extra_materials():
    M["vend_white"] = material("VendingWhite", (0.93, 0.93, 0.90), rough=.38)
    M["vend_red"] = material("VendingRed", (0.72, 0.055, 0.045), rough=.42)
    M["vend_blue"] = material("VendingBlue", (0.04, 0.20, 0.52), rough=.42)
    M["vend_dark"] = material("VendingDark", (0.025, 0.03, 0.035), rough=.4)
    M["cork"] = material("CorkBoard", (0.40, 0.26, 0.13), rough=.92)
    M["cardboard"] = material("Cardboard", (0.55, 0.38, 0.20), rough=.92)
    M["crate"] = material("CrateWood", (0.34, 0.22, 0.12), rough=.88)
    M["wire"] = L.unlit_material("OverheadWire", (0.009, 0.012, 0.020))
    M["brick"] = material("BrickDark", (0.14, 0.10, 0.085), rough=.88)
    M["neighbor"] = material("NeighborFacade", (0.095, 0.10, 0.11), rough=.82)
    M["neighbor2"] = material("NeighborFacade2", (0.14, 0.13, 0.12), rough=.82)
    M["shutter"] = material("Shutter", (0.22, 0.24, 0.25), rough=.55, metallic=.5)
    M["warm_curtain"] = emission_material("WarmCurtain", (1.0, 0.62, 0.28), .75, base=(0.7, 0.4, 0.2))
    M["cool_window"] = emission_material("CoolWindow", (0.35, 0.55, 0.95), .45, base=(0.1, 0.2, 0.4))
    M["noren"] = material("NorenIndigo", (0.035, 0.075, 0.14), rough=.9)
    M["gold"] = material("WarmGold", (0.80, 0.54, 0.18), rough=.32, metallic=.55)
    M["red_paint"] = material("PostBoxRed", (0.62, 0.04, 0.03), rough=.38)
    M["leaf1"] = material("TreeLeaf1", (0.035, 0.20, 0.10), rough=.68)
    M["leaf2"] = material("TreeLeaf2", (0.06, 0.30, 0.13), rough=.65)
    M["leaf3"] = material("TreeLeaf3", (0.10, 0.36, 0.16), rough=.62)
    M["bulb"] = emission_material("StringBulb", (1.0, 0.66, 0.24), 4.0)
    M["lantern"] = emission_material("RedLantern", (1.0, 0.15, 0.05), 1.7, base=(0.55, 0.04, 0.02))
    M["rain_mat"] = material("RainMaterial", (0.65, 0.82, 1.0), rough=.1, alpha=.32,
                             emission=(0.60, 0.78, 1.0), emission_strength=.45)
    M["rain_mat"].surface_render_method = 'DITHERED'
    M["reflection_pool"] = material("ReflectionPool", (1.0, 0.58, 0.25), rough=.15, alpha=.12,
                                    emission=(1.0, 0.58, 0.24), emission_strength=.55)
    M["reflection_pool"].surface_render_method = 'DITHERED'
    M["mirror"] = material("ConvexMirror", (0.52, 0.64, 0.72), rough=.04, metallic=.92)
    M["mirror_rim"] = material("MirrorRim", (0.90, 0.42, 0.08), rough=.35)
    M["flag_cloth"] = material("NoboriCloth", (0.88, 0.88, 0.80), rough=.75,
                               emission=(0.88, 0.85, 0.75), emission_strength=.12)


def build_vending_and_bins():
    # Two machines stand on the corner and face the street (-Y).
    for idx, (cx, accent, label, glow) in enumerate([
        (3.12, M["vend_red"], "DRINK", (0.85, 0.12, 0.07)),
        (4.38, M["vend_blue"], "COFFEE", (0.10, 0.35, 0.95)),
    ]):
        cy = -3.28
        base_z = .15
        # open-front cabinet shell (the dark interior is actually visible)
        box(f"VendingBack{idx}", (cx, cy+.40, base_z), (1.15, .12, 1.93), accent, "04_Props", bevel=.02, anchor='BOTTOM')
        box(f"VendingSideL{idx}", (cx-.535, cy, base_z), (.08, .90, 1.93), M["vend_white"], "04_Props", bevel=.02, anchor='BOTTOM')
        box(f"VendingSideR{idx}", (cx+.535, cy, base_z), (.08, .90, 1.93), M["vend_white"], "04_Props", bevel=.02, anchor='BOTTOM')
        box(f"VendingLower{idx}", (cx, cy, base_z), (1.08, .86, .86), accent, "04_Props", bevel=.03, anchor='BOTTOM')
        box(f"VendingTop{idx}", (cx, cy, base_z+1.76), (1.08, .86, .17), accent, "04_Props", bevel=.02, anchor='BOTTOM')
        box(f"VendingFoot{idx}", (cx, cy, base_z), (1.10, .84, .09), M["vend_dark"], "04_Props", anchor='BOTTOM')
        box(f"VendingLowerPanel{idx}", (cx, cy-.456, base_z+.48), (1.02, .02, .35), M["vend_white"], "04_Props", anchor='BOTTOM')
        box(f"VendingFrameTop{idx}", (cx, cy-.455, base_z+1.66), (1.10, .02, .05), M["vend_white"], "04_Props", anchor='BOTTOM')
        box(f"VendingFrameBot{idx}", (cx, cy-.455, base_z+.87), (1.10, .02, .05), M["vend_white"], "04_Props", anchor='BOTTOM')
        box(f"VendingFrameL{idx}", (cx-.53, cy-.455, base_z+.90), (.05, .02, .84), M["vend_white"], "04_Props", anchor='BOTTOM')
        box(f"VendingFrameR{idx}", (cx+.53, cy-.455, base_z+.90), (.05, .02, .84), M["vend_white"], "04_Props", anchor='BOTTOM')
        # lit display cavity set behind the bottles
        box(f"VendingCavity{idx}", (cx, cy+.33, base_z+.88), (1.00, .03, .96), M["vend_dark"], "04_Props", anchor='BOTTOM')
        box(f"VendingLight{idx}", (cx, cy+.305, base_z+.91), (.92, .02, .86), M["sign_white_soft"], "04_Props", anchor='BOTTOM')
        # bottles in three rows, positioned between glass and backlight
        for row in range(3):
            for k in range(5):
                z = base_z + 1.02 + row * .25
                xx = cx - .39 + k * .19
                mat = M[f"prod{(idx*5+row*3+k) % 12}"]
                cylinder(f"VendBottle{idx}_{row}_{k}", (xx, cy+.10, z), .036, .16, mat,
                         "04_Props", vertices=8, anchor='BOTTOM')
        box(f"VendingGlass{idx}", (cx, cy-.44, base_z+.90), (1.02, .018, .95), M["glass_vend"], "04_Props", anchor='BOTTOM')
        # header
        box(f"VendingHeader{idx}", (cx, cy-.445, base_z+1.72), (1.04, .06, .19), accent, "04_Props", anchor='BOTTOM')
        text_obj(f"VendingLabel{idx}", label, (cx, cy-.485, base_z+1.79), .13, M["unlit_white"], "04_Props",
                 rot=(90*D2R, 0, 0), extrude=.002, font=L.FONT_EN)
        # button strip and coin panel
        box(f"VendingButtons{idx}", (cx, cy-.455, base_z+.80), (.74, .02, .11), M["vend_dark"], "04_Props", anchor='BOTTOM')
        for k in range(6):
            box(f"VendingBtn{idx}_{k}", (cx-.30+k*.12, cy-.468, base_z+.845), (.055, .008, .035), M[f"prod{k%12}"], "04_Props")
        box(f"VendingCoin{idx}", (cx+.43, cy-.456, base_z+.75), (.16, .02, .23), M["vend_dark"], "04_Props", anchor='BOTTOM')
        box(f"VendingCoinSlot{idx}", (cx+.43, cy-.468, base_z+.84), (.03, .008, .08), M["steel"], "04_Props")
        box(f"VendingChute{idx}", (cx, cy-.455, base_z+.28), (.74, .02, .19), M["vend_dark"], "04_Props", anchor='BOTTOM')
        point_light(f"VendingLightPoint{idx}", (cx, cy-.60, base_z+1.25), 42, glow, .25)
        box(f"VendingCap{idx}", (cx, cy, base_z+1.93), (1.19, .94, .06), M["vend_white"], "04_Props", bevel=.02, anchor='BOTTOM')

    # recycle bins next to the vending machines, facing south
    for idx, (xx, color, txt) in enumerate([(5.08, M["sign_blue"], "かん"), (5.66, M["sign_green"], "ペット")]):
        box(f"Bin{idx}", (xx, -3.28, .15), (.52, .55, .88), M["vend_white"], "04_Props", bevel=.04, anchor='BOTTOM')
        box(f"BinFace{idx}", (xx, -3.57, .52), (.38, .02, .50), color, "04_Props", anchor='BOTTOM')
        cylinder(f"BinHole{idx}", (xx, -3.585, .82), .095, .02, M["vend_dark"], "04_Props", vertices=18, rot=(90*D2R,0,0))
        text_obj(f"BinLabel{idx}", txt, (xx, -3.59, .66), .075, M["unlit_white"], "04_Props",
                 rot=(90*D2R, 0, 0), extrude=.001, font=L.FONT_JP)
        box(f"BinCap{idx}", (xx, -3.28, 1.03), (.56, .59, .07), M["vend_dark"], "04_Props", bevel=.02, anchor='BOTTOM')
    box("AshtrayStand", (5.55, -2.52, .15), (.18, .18, .95), M["steel"], "04_Props", bevel=.02, anchor='BOTTOM')
    cylinder("AshtrayTop", (5.55, -2.52, 1.10), .16, .08, M["steel_dark"], "04_Props", vertices=16)


def build_bicycle():
    y = -3.35
    ground = .155
    rear_x, front_x = -8.30, -6.92
    wheel_r = .33
    hub_z = ground + wheel_r
    frame_mat = material("BikeFrame", (0.055, 0.32, 0.30), rough=.35, metallic=.35)
    for i, x in enumerate([rear_x, front_x]):
        torus(f"BikeTire{i}", (x, y, hub_z), wheel_r, .028, M["tire"], "04_Props", rot=(90*D2R, 0, 0), major_segments=36, minor_segments=8)
        torus(f"BikeRim{i}", (x, y, hub_z), wheel_r-.032, .010, M["alu"], "04_Props", rot=(90*D2R, 0, 0), major_segments=36, minor_segments=6)
        cylinder(f"BikeHub{i}", (x, y, hub_z), .045, .10, M["steel"], "04_Props", rot=(90*D2R, 0, 0), vertices=12)
        for k in range(8):
            a = TAU * k / 8
            tube(f"BikeSpoke{i}_{k}", [
                (x, y, hub_z),
                (x + math.cos(a)*(wheel_r-.035), y, hub_z + math.sin(a)*(wheel_r-.035))
            ], .004, M["alu"], "04_Props")
    # frame tubes
    tube("BikeDownTube", [(rear_x, y, hub_z), (-7.77, y, hub_z+.46), (-7.60, y, hub_z+.10), (front_x, y, hub_z)], .023, frame_mat, "04_Props")
    tube("BikeSeatTube", [(-7.77, y, hub_z+.46), (-7.88, y, hub_z+.72), (-7.88, y, hub_z+.55), (-7.80, y, hub_z+.18)], .022, frame_mat, "04_Props")
    tube("BikeTopTube", [(-7.77, y, hub_z+.46), (-7.55, y, hub_z+.67), (-7.18, y, hub_z+.64), (-7.04, y, hub_z+.46)], .020, frame_mat, "04_Props")
    tube("BikeFork", [(-7.04, y, hub_z+.46), (-6.98, y, hub_z+.22), (front_x, y, hub_z)], .018, M["alu"], "04_Props")
    tube("BikeRearStay", [(rear_x, y, hub_z), (-7.82, y, hub_z+.28), (-7.78, y, hub_z+.48)], .014, M["steel"], "04_Props")
    tube("BikeSeatStay", [(rear_x, y, hub_z), (-7.95, y, hub_z+.65), (-7.87, y, hub_z+.73)], .012, M["steel"], "04_Props")
    # saddle and handlebar
    box("BikeSaddle", (-7.92, y, hub_z+.75), (.28, .12, .06), M["black"], "04_Props", bevel=.025)
    tube("BikeHandleStem", [(-7.05, y, hub_z+.46), (-7.02, y, hub_z+.84)], .015, M["steel"], "04_Props")
    tube("BikeHandlebar", [(-7.02, y-.22, hub_z+.84), (-7.02, y+.22, hub_z+.84)], .015, M["steel"], "04_Props")
    for s in (-1, 1):
        tube(f"BikeGrip{s}", [(-7.02, y+s*.18, hub_z+.84), (-7.02, y+s*.28, hub_z+.84)], .023, M["black"], "04_Props")
    # front basket
    bx, bz = -6.72, hub_z+.48
    box("BikeBasketBase", (bx, y, bz), (.42, .34, .05), M["steel"], "04_Props", bevel=.01)
    for i in range(4):
        box(f"BikeBasketWire{i}", (bx-.20+i*.13, y, bz+.16), (.012, .34, .32), M["steel"], "04_Props")
    for i in range(3):
        box(f"BikeBasketHoriz{i}", (bx, y-.16+i*.16, bz+.16), (.42, .012, .32), M["steel"], "04_Props")
    # kickstand and small lamp
    tube("BikeKickstand", [(-7.82, y, hub_z+.10), (-7.72, y+.12, ground)], .012, M["steel"], "04_Props")
    cylinder("BikeLamp", (-7.03, y, hub_z+.58), .045, .07, M["lamp_glass"], "04_Props", rot=(0,90*D2R,0), vertices=12)
    point_light("BikeLampGlow", (-7.0, y, hub_z+.58), 8, (1.0,0.6,0.2), .1)
    # a second simple bicycle further back, mostly silhouette
    box("BikeRack", (-8.55, -3.8, .15), (.10, 1.2, .45), M["steel"], "04_Props", bevel=.02, anchor='BOTTOM')


def build_umbrella_stand():
    x, y, z = -.95, -3.16, .155
    cylinder("UmbrellaBucket", (x, y, z), .23, .56, M["steel"], "04_Props", vertices=18, anchor='BOTTOM')
    torus("UmbrellaBucketRim", (x, y, z+.55), .23, .025, M["steel"], "04_Props", major_segments=20, minor_segments=5)
    colors = [M["red"], M["sign_blue"], M["sign_orange"], M["glass"]]
    for i in range(4):
        a = TAU * i / 4 + .4
        dx, dy = math.cos(a)*.10, math.sin(a)*.10
        # shaft
        tube(f"UmbrellaShaft{i}", [(x+dx*.3, y+dy*.3, z+.05), (x+dx, y+dy, z+1.32)], .010, M["steel"], "04_Props")
        # folded canopy - tapered cylinder
        cylinder(f"UmbrellaCanopy{i}", (x+dx, y+dy, z+.82), .07, .83, colors[i], "04_Props", vertices=10,
                 radius2=.018, anchor='BOTTOM')
        torus(f"UmbrellaTip{i}", (x+dx, y+dy, z+1.28), .03, .012, colors[i], "04_Props", major_segments=12, minor_segments=4)
        tube(f"UmbrellaHandle{i}", [(x+dx, y+dy, z+1.31), (x+dx+.06, y+dy, z+1.34), (x+dx+.11, y+dy, z+1.29)],
             .014, M["wood_dark"], "04_Props")
    # small puddle under it
    polygon("UmbrellaPuddle", (x, y, .158), [(-.35,-.2),(-.1,-.32),(.28,-.2),(.32,.12),(.08,.28),(-.25,.2)], M["puddle"], "04_Props")


def build_doormat_and_aboard():
    # outside doormat
    box("OuterMat", (0.55, -2.93, .155), (1.75, .92, .035), M["green"], "04_Props", bevel=.01, anchor='BOTTOM')
    box("OuterMatBorderS", (0.55, -3.39, .157), (1.75, .04, .006), M["paint"], "04_Props")
    box("OuterMatBorderN", (0.55, -2.47, .157), (1.75, .04, .006), M["paint"], "04_Props")
    text_obj("OuterMatText", "WELCOME", (0.55, -2.93, .191), .19, M["unlit_white"], "04_Props",
             rot=(0,0,0), extrude=.001, font=L.FONT_EN)
    # A-frame sale board
    x, y = -1.75, -3.30
    for s in (-1, 1):
        box(f"AboardPanel{s}", (x, y+s*.11, .62), (.72, .04, .92), M["sign_white_soft"], "04_Props", rot=(s*10*D2R,0,0), bevel=.01)
    box("AboardTop", (x, y, 1.07), (.78, .28, .05), M["steel"], "04_Props", bevel=.01)
    text_obj("AboardText1", "からあげ", (x, y-.155, .83), .17, M["ink_unlit"], "04_Props",
             rot=(90*D2R,0,0), extrude=.002, font=L.FONT_JP)
    text_obj("AboardText2", "100円", (x, y-.157, .53), .20, M["ink_unlit"], "04_Props",
             rot=(90*D2R,0,0), extrude=.002, font=L.FONT_JP)
    box("AboardBase", (x, y, .155), (.80, .34, .04), M["steel_dark"], "04_Props", bevel=.01, anchor='BOTTOM')


def build_street_lamp():
    x, y = 5.36, -4.85
    cylinder("LampBase", (x, y, .15), .19, .30, M["steel_dark"], "05_Utility", vertices=16, anchor='BOTTOM', bevel=.02)
    cylinder("LampPole", (x, y, .15), .085, 5.25, M["steel"], "05_Utility", vertices=16, radius2=.06, anchor='BOTTOM')
    tube("LampArm", [(x, y, 5.26), (x-.30, y, 5.50), (x-.72, y, 5.40), (x-.92, y, 5.16)], .055, M["steel"], "05_Utility")
    cylinder("LampShade", (x-.92, y, 5.11), .20, .11, M["steel_dark"], "05_Utility", vertices=20, radius2=.12)
    cylinder("LampGlowDisc", (x-.92, y, 5.03), .16, .025, M["lamp_glass"], "05_Utility", vertices=20)
    # decorative banner
    box("LampBanner", (x+.001, y, 3.55), (.04, .62, 1.15), M["sign_green"], "05_Utility", bevel=.01, anchor='BOTTOM')
    text_obj("LampBannerText", "星見町", (x+.03, y, 3.58), .15, M["unlit_white"], "05_Utility",
             rot=(90*D2R,0,90*D2R), extrude=.002, font=L.FONT_JP)
    # lights
    spot_light("StreetLampSpot", (x-.92, y, 5.02), 650, (1.0,0.70,0.38), 100, target=(x-.4, y+.2, 0.0), radius=.12)
    point_light("StreetLampGlow", (x-.92, y, 4.95), 110, (1.0,0.64,0.30), .20)
    # small bin / base clutter
    cylinder("LampBollard", (x-.05, y+1.0, .15), .09, .55, M["steel"], "05_Utility", vertices=12, anchor='BOTTOM')


def utility_pole(name, x, y, height, radius=.18, with_arms=True):
    """Concrete Japanese utility pole: tapered shaft, step bolts, three braced
    crossarms with ceramic insulators, transformer with radiators, fuse cutouts,
    pole plate, poster and reflective wrap."""
    top_r = radius * .62
    # scene_lib.cylinder() keeps the mesh centred on the object origin, so every
    # part below is placed by its centre (bottom + depth/2) to make it sit at the
    # intended height instead of sinking into the ground.
    cylinder(name+"_pole", (x, y, height*.5), radius, height, M["concrete"], "05_Utility",
             vertices=16, radius2=top_r)
    cylinder(name+"_base", (x, y, .225), radius*1.35, .45, M["concrete_dark"], "05_Utility",
             vertices=16)
    cylinder(name+"_cap", (x, y, height + .035), top_r*1.2, .07, M["concrete_dark"], "05_Utility",
             vertices=16)

    # step bolts every 45 cm, alternating around the shaft
    steps = max(4, int((height - 1.4) / 0.45))
    for i in range(steps):
        z = .80 + i * .45
        r = radius + (top_r - radius) * (z / height)
        along_x = (i % 2 == 0)
        cylinder("%s_step%d" % (name, i), (x, y, z), .012, r*2 + .13, M["steel_dark"],
                 "05_Utility", vertices=8, rot=(0, 90*D2R, 0) if along_x else (90*D2R, 0, 0))

    if with_arms:
        for ai, (hf, w) in enumerate([(0.800, 2.35), (0.875, 1.95), (0.945, 1.55)]):
            z = height * hf
            box("%s_arm%d" % (name, ai), (x, y, z), (w, .09, .09), M["steel_dark"],
                "05_Utility", bevel=.008)
            # angle-steel braces from the shaft up to the arm ends
            for s in (-1, 1):
                tube("%s_brace%d%s" % (name, ai, 'L' if s < 0 else 'R'),
                     [(x, y, z - .58), (x + s*(w*.5 - .20), y, z - .05)],
                     .020, M["steel_dark"], "05_Utility")
            for k, ox in enumerate([-w*.5 + .30, 0.0, w*.5 - .30]):
                cx = x + ox
                cylinder("%s_ins%d_%d" % (name, ai, k), (cx, y, z + .14), .075, .16,
                         M["white"], "05_Utility", vertices=12)
                cylinder("%s_inscap%d_%d" % (name, ai, k), (cx, y, z + .24), .098, .04,
                         M["white"], "05_Utility", vertices=12)

    # transformer drum with four radiators and three bushings
    tz = height * .615
    tx = x + .34
    cylinder(name+"_transformer", (tx, y, tz + .40), .255, .80, M["steel"], "05_Utility",
             vertices=16)
    for i, (dx, dy, sx, sy) in enumerate([(.265, 0, .05, .34), (-.265, 0, .05, .34),
                                          (0, .265, .34, .05), (0, -.265, .34, .05)]):
        box("%s_fin%d" % (name, i), (tx + dx, y + dy, tz + .40), (sx, sy, .62),
            M["steel_dark"], "05_Utility")
    for i, ox in enumerate([-.13, 0.0, .13]):
        cylinder("%s_bushing%d" % (name, i), (tx + ox, y, tz + .875), .042, .15,
                 M["white"], "05_Utility", vertices=10)
        cylinder("%s_bushcap%d" % (name, i), (tx + ox, y, tz + .965), .055, .03,
                 M["steel_dark"], "05_Utility", vertices=10)
    for i, sz in enumerate([tz + .18, tz + .64]):
        torus("%s_strap%d" % (name, i), (x, y, sz), radius + .012, .020,
              M["steel_dark"], "05_Utility", major_segments=18, minor_segments=4)
        box("%s_trbar%d" % (name, i), (x + .19, y, sz), (.34, .05, .05),
            M["steel_dark"], "05_Utility")

    # drop-out fuse cutouts on the opposite side, just under the top arm
    fx = x - .32
    box(name+"_fusebar", (fx, y, height*.885), (.07, .36, .05), M["steel_dark"], "05_Utility")
    for i, oy in enumerate([-.11, 0.0, .11]):
        cylinder("%s_fuse%d" % (name, i), (fx, y + oy, height*.885 + .15), .030, .22,
                 M["white"], "05_Utility", vertices=8)

    # pole plate, poster and reflective wrap
    box(name+"_plate", (x-.20, y-.01, 2.45), (.02, .22, .30), M["sign_blue"], "05_Utility", anchor='BOTTOM')
    text_obj(name+"_plateText", "星見町", (x-.215, y, 2.55), .085, M["unlit_white"], "05_Utility",
             rot=(90*D2R,0,90*D2R), extrude=.001, font=L.FONT_JP)
    box(name+"_poster", (x-.20, y+.12, 1.55), (.015, .34, .48), M["sign_white_soft"], "05_Utility", anchor='BOTTOM')
    for i, wz in enumerate([1.08, 1.19]):
        cylinder("%s_wrap%d" % (name, i), (x, y, wz), radius*1.03, .045,
                 M["white"], "05_Utility", vertices=16)
    return (x, y, height*.94)


def build_utility_poles():
    a = utility_pole("MainPole", -12.42, -5.02, 9.3, .21, True)
    b = utility_pole("EastPole", 5.15, -3.55, 7.7, .16, True)
    c = utility_pole("NorthPole", 5.15, 12.45, 7.8, .16, True)
    # wires
    def wire(name, p0, p1, sag, offs):
        pts = []
        for t in [0, .25, .5, .75, 1.0]:
            x = p0[0] + (p1[0]-p0[0])*t + offs[0]
            y = p0[1] + (p1[1]-p0[1])*t + offs[1]
            z = p0[2] + (p1[2]-p0[2])*t - math.sin(math.pi*t)*sag + offs[2]
            pts.append((x, y, z))
        curve_line(name, pts, .018, M["wire"], "07_Wires")
    for i, (z0, z1, sag, dy) in enumerate([
        (8.9, 7.3, .55, .0), (8.7, 7.15, .75, .20), (8.5, 7.0, .95, .40), (8.3, 6.9, 1.15, .62)
    ]):
        wire(f"WireWest{i}", a, b, sag, (0, dy, 0))
        wire(f"WireNorth{i}", a, c, sag, (dy*0.8, 0, 0))
    for i, (z0, z1) in enumerate([(7.4, 6.9), (7.2, 6.7)]):
        wire(f"WireStoreDrop{i}", (b[0]-.1, b[1], z0), (2.0, 4.2, z1), .35, (0,0,0))
    # service cable to neighbor
    wire("WireNeighbor", (b[0], b[1], 6.4), (-10.4, 1.8, 5.7), .3, (0,0,0))
    # hanging cable loops on main pole
    for i in range(3):
        torus(f"PoleLoop{i}", (5.15+i*.10, -3.55, 6.0-i*.18), .28, .018, M["wire"], "07_Wires",
              rot=(0, 90*D2R, 0), major_segments=20, minor_segments=5)


def build_street_signs():
    x, y = 4.38, -5.08
    cylinder("SignPole", (x, y, .15), .045, 3.15, M["steel"], "05_Utility", vertices=12, anchor='BOTTOM')
    # main green district sign
    box("DistrictSign", (x, y, 2.65), (1.55, .08, .44), M["sign_green"], "05_Utility", bevel=.02)
    box("DistrictSignBorder", (x, y-.045, 2.65), (1.58, .02, .47), M["white"], "05_Utility", bevel=.01)
    box("DistrictSignFace", (x, y-.062, 2.65), (1.47, .01, .36), M["sign_green"], "05_Utility")
    text_obj("DistrictText", "星見町三丁目", (x, y-.070, 2.66), .155, M["unlit_white"], "05_Utility",
             rot=(90*D2R,0,0), extrude=.002, font=L.FONT_JP)
    text_obj("DistrictSub", "HOSHIMI 3-CHOME", (x, y-.071, 2.51), .065, M["unlit_white"], "05_Utility",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)
    # blue arrow plate
    box("DirectionSign", (x+.02, y, 3.00), (1.18, .06, .26), M["sign_blue"], "05_Utility", bevel=.015)
    box("DirectionSignFace", (x+.02, y-.04, 3.00), (1.10, .01, .20), M["sign_blue"], "05_Utility")
    text_obj("DirectionText", "駅前通り  →", (x+.02, y-.047, 3.00), .11, M["unlit_white"], "05_Utility",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_JP)
    # pole cap
    cylinder("SignPoleCap", (x, y, 3.30), .06, .10, M["steel_dark"], "05_Utility", vertices=12)

    # parking sign
    px, py = 12.35, 5.20
    cylinder("ParkingPole", (px, py, .03), .04, 2.45, M["steel"], "05_Utility", vertices=10, anchor='BOTTOM')
    box("ParkingSign", (px, py, 2.15), (.52, .06, .62), M["sign_blue"], "05_Utility", bevel=.02)
    text_obj("ParkingPText", "P", (px, py-.04, 2.22), .42, M["unlit_white"], "05_Utility",
             rot=(90*D2R,0,0), extrude=.003, font=L.FONT_EN)
    box("ParkingSignWhite", (px, py-.037, 1.95), (.38, .01, .10), M["white"], "05_Utility")
    text_obj("ParkingSub", "24H", (px, py-.043, 1.95), .075, M["ink_unlit"], "05_Utility",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)


def build_guardrail():
    rail = material("GuardRail", (0.80, 0.82, 0.78), rough=.35, metallic=.4)
    # east curb rail
    for i, yy in enumerate([-.2, 1.3, 2.8, 4.3]):
        cylinder(f"RailPostE{i}", (6.02, yy, .15), .045, .90, M["steel"], "05_Utility", vertices=10, anchor='BOTTOM')
        box(f"RailRefE{i}", (6.07, yy, .70), (.02, .10, .16), M["sign_blue"], "05_Utility")
    for i, zz in enumerate([.62, .92]):
        cylinder(f"RailBarE{i}", (6.02, 2.05, zz), .035, 5.1, rail, "05_Utility", vertices=10, rot=(90*D2R, 0, 0))
    # south curb rail
    for i, xx in enumerate([9.55, 11.15, 12.75]):
        cylinder(f"RailPostS{i}", (xx, -5.52, .15), .045, .90, M["steel"], "05_Utility", vertices=10, anchor='BOTTOM')
        box(f"RailRefS{i}", (xx, -5.57, .70), (.10, .02, .16), M["sign_blue"], "05_Utility")
    for i, zz in enumerate([.62, .92]):
        cylinder(f"RailBarS{i}", (11.15, -5.52, zz), .035, 3.5, rail, "05_Utility", vertices=10, rot=(0, 90*D2R, 0))
    # short corner guard
    cylinder("CornerRailPost", (6.02, -5.52, .15), .05, .92, M["steel"], "05_Utility", vertices=10, anchor='BOTTOM')


def build_bulletin_board():
    x, y, z = 2.08, 4.30, 1.30
    box("BulletinBack", (x, y, z), (.07, 1.55, 1.25), M["wood_dark"], "04_Props", bevel=.02)
    box("BulletinCork", (x+.045, y, z+.02), (.02, 1.38, 1.05), M["cork"], "04_Props")
    # little roof
    box("BulletinRoof", (x+.06, y, z+.71), (.28, 1.70, .07), M["steel_dark"], "04_Props", rot=(12*D2R,0,0), bevel=.01)
    # posters on board
    poster_data = [
        (-.48, .18, .43, .54, M["mag2"], "町内会"),
        (0.02, .25, .40, .46, M["mag1"], "SALE"),
        (.46, .08, .34, .42, M["mag4"], "あんぜん"),
    ]
    for i, (dy, dz, w, h, mat, txt) in enumerate(poster_data):
        box(f"BoardPoster{i}", (x+.058, y+dy, z+dz), (.01, w, h), mat, "04_Props", bevel=.004)
        text_obj(f"BoardPosterText{i}", txt, (x+.067, y+dy, z+dz+.04), .075, M["unlit_white"], "04_Props",
                 rot=(90*D2R,0,90*D2R), extrude=.001, font=L.FONT_JP)
    # header strip
    box("BulletinHeader", (x+.07, y, z+.75), (.05, 1.45, .24), M["sign_white_soft"], "04_Props", bevel=.01)
    text_obj("BulletinHeaderText", "HOSHIMI NEWS", (x+.10, y, z+.75), .11, M["ink_unlit"], "04_Props",
             rot=(90*D2R,0,90*D2R), extrude=.001, font=L.FONT_EN)
    # tiny gooseneck lamp
    box("BoardLampArm", (x+.20, y+.62, z+.90), (.28, .03, .03), M["steel_dark"], "04_Props")
    cylinder("BoardLamp", (x+.33, y+.62, z+.84), .055, .09, M["lamp_glass"], "04_Props", vertices=10)


def build_air_conditioners():
    # wall unit in the alley
    for idx, (x, y, z, facing) in enumerate([
        (-9.38, 1.30, .55, 'W'),
        (-9.38, 3.00, 3.55, 'W'),
        (-10.10, 5.00, .70, 'E'),
    ]):
        box(f"ACBody{idx}", (x, y, z), (.46, .78, .62), M["white"], "04_Props", bevel=.03, anchor='BOTTOM')
        # face
        fx = x-.24 if facing == 'W' else x+.24
        box(f"ACFace{idx}", (fx, y, z+.06), (.02, .68, .50), M["steel_dark"], "04_Props", anchor='BOTTOM')
        torus(f"ACGrille{idx}", (fx-(.012 if facing=='W' else -.012), y, z+.33), .19, .012, M["steel"], "04_Props",
              rot=(0, 90*D2R, 0), major_segments=20, minor_segments=4)
        for k in range(3):
            box(f"ACFan{idx}_{k}", (fx, y-.05+k*.05, z+.33), (.015, .22, .04), M["steel"], "04_Props", rot=(0,0,0))
        # pipes
        tube(f"ACPipe{idx}", [(fx, y+.30, z+.48), (fx, y+.42, z+.88), (fx, y+.42, z+1.2), (fx, y+.22, z+1.5)],
             .018, M["concrete"], "04_Props")
        box(f"ACBracket{idx}", (x, y, z-.08), (.55, .84, .06), M["steel_dark"], "04_Props", anchor='BOTTOM')
    # balcony ac on south facade
    box("BalconyAC", (-2.2, -2.98, 4.78), (.55, .36, .44), M["white"], "04_Props", bevel=.03, anchor='BOTTOM')
    box("BalconyACFace", (-2.2, -3.17, 4.82), (.46, .02, .34), M["steel_dark"], "04_Props", anchor='BOTTOM')
    torus("BalconyACGrille", (-2.2, -3.185, 5.00), .14, .01, M["steel"], "04_Props", rot=(90*D2R,0,0), major_segments=16, minor_segments=4)


def build_alley():
    # neighbor building on the left
    box("NeighborBody", (-11.72, 3.8, 0.0), (2.55, 11.4, 5.8), M["neighbor"], "06_Alley", bevel=.03, anchor='BOTTOM')
    box("NeighborParapet", (-11.72, 3.8, 5.80), (2.65, 11.5, .32), M["neighbor2"], "06_Alley", bevel=.02, anchor='BOTTOM')
    box("NeighborBand", (-11.72, -1.82, 2.55), (2.58, .10, .16), M["neighbor2"], "06_Alley", anchor='BOTTOM')
    # closed shutter
    box("NeighborShutter", (-11.7, -1.86, .18), (1.95, .06, 2.10), M["shutter"], "06_Alley", anchor='BOTTOM')
    for i in range(18):
        box(f"ShutterRib{i}", (-11.7, -1.895, .25+i*.11), (1.92, .015, .025), M["steel_dark"], "06_Alley")
    box("ShutterSign", (-11.7, -1.93, 2.28), (1.2, .03, .24), M["sign_white_soft"], "06_Alley", bevel=.01)
    text_obj("ShutterSignText", "CLOSED", (-11.7, -1.948, 2.28), .12, M["ink_unlit"], "06_Alley",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_EN)
    # upper windows
    for i, (x, z, mat) in enumerate([(-12.35, 3.55, M["warm_curtain"]), (-11.05, 3.55, M["cool_window"])]):
        box(f"NeighborWin{i}", (x, -1.83, z), (.62, .04, .72), mat, "06_Alley", anchor='BOTTOM')
        box(f"NeighborWinFrame{i}", (x, -1.86, z-.06), (.74, .06, .84), M["steel_dark"], "06_Alley", anchor='BOTTOM')
    # small entrance awning and a row of dim upper windows
    box("NeighborAwning", (-11.7, -2.03, 2.42), (2.1, .72, .07), M["steel_dark"], "06_Alley", bevel=.01, anchor='BOTTOM', rot=(5*D2R,0,0))
    box("NeighborAwningEdge", (-11.7, -2.38, 2.34), (2.1, .04, .16), M["sign_green"], "06_Alley", anchor='BOTTOM')
    point_light("NeighborAwningGlow", (-11.7, -2.25, 2.18), 55, (1.0,0.55,0.25), .35)
    for i, x in enumerate([-12.8, -10.65]):
        box(f"NeighborUpperWin{i}", (x, -1.84, 4.45), (.42, .03, .55), M["warm_curtain"] if i==0 else M["cool_window"], "06_Alley", anchor='BOTTOM')
        box(f"NeighborUpperFrame{i}", (x, -1.87, 4.39), (.52, .05, .66), M["steel_dark"], "06_Alley", anchor='BOTTOM')
    cylinder("NeighborDrainpipe", (-10.55, -1.92, 0.0), .045, 5.55, M["steel_dark"], "06_Alley", vertices=10, anchor='BOTTOM')
    for i, z in enumerate([1.2, 2.8, 4.4]):
        box(f"NeighborLedge{i}", (-11.7, -1.86, z), (2.2, .06, .06), M["neighbor2"], "06_Alley")
    # balcony on neighbor
    box("NeighborBalcony", (-11.7, -2.15, 4.66), (2.2, .58, .12), M["concrete"], "06_Alley", bevel=.02, anchor='BOTTOM')
    for i, x in enumerate([-12.6, -11.9, -11.2, -10.7]):
        box(f"NeighborBalPost{i}", (x, -2.42, 4.78), (.04, .04, .55), M["steel"], "06_Alley", anchor='BOTTOM')
    box("NeighborBalRail", (-11.7, -2.42, 5.32), (2.1, .05, .05), M["steel"], "06_Alley", anchor='BOTTOM')
    # vertical neon sign on the south face
    sx, sy, sz = -12.55, -1.95, 2.45
    box("SnackSignBox", (sx, sy, sz), (.46, .12, 1.85), M["neighbor2"], "06_Alley", bevel=.03)
    box("SnackSignFace", (sx, sy-.08, sz), (.34, .02, 1.62), M["black"], "06_Alley")
    chars = ["ス", "ナ", "ッ", "ク"]
    for i, ch in enumerate(chars):
        text_obj(f"SnackChar{i}", ch, (sx, sy-.095, sz+.60-i*.34), .24, M["neon_pink"], "06_Alley",
                 rot=(90*D2R,0,0), extrude=.004, font=L.FONT_JP)
    point_light("SnackSignGlow", (sx+.1, sy-.4, sz+.2), 60, (1.0,0.1,0.35), .30)
    # rooftop clutter
    box("NeighborRooftopBox", (-12.2, 4.6, 5.82), (.85, .95, .75), M["wall_gray"], "06_Alley", bevel=.02, anchor='BOTTOM')
    cylinder("NeighborVent", (-11.2, 2.0, 5.82), .13, .55, M["steel"], "06_Alley", vertices=14, anchor='BOTTOM')

    # alley floor / drain
    box("AlleyFloor", (-9.62, 3.0, .02), (1.15, 11.2, .04), M["concrete_dark"], "06_Alley")
    box("AlleyDrain", (-9.62, 2.6, .045), (.16, 10.2, .018), M["steel_dark"], "06_Alley")
    for i in range(10):
        box(f"AlleyDrainSlot{i}", (-9.62, -2.0+i*1.0, .056), (.12, .30, .009), M["black"], "06_Alley")
    polygon("AlleyPuddle", (-9.25, 1.1, .052), [(-.25,-1.4),(.12,-1.8),(.32,-.3),(.22,1.5),(-.14,1.8),(-.34,.4)], M["puddle"], "06_Alley")
    polygon("AlleyPuddle2", (-9.55, 5.6, .052), [(-.3,-.8),(.18,-1.0),(.30,.6),(.05,1.0),(-.30,.5)], M["puddle"], "06_Alley")

    # crates and cardboard
    for i in range(3):
        x = -9.28 + (i%2)*.35
        y = 6.55 + (i//2)*.45
        z = .06 + (i%2)*.32
        box(f"AlleyCrate{i}", (x, y, z), (.52, .42, .32), M["crate"], "06_Alley", bevel=.01, anchor='BOTTOM')
        for j in range(3):
            box(f"AlleyCrateSlat{i}_{j}", (x, y-.215, z+.07+j*.08), (.54, .02, .03), M["wood_dark"], "06_Alley")
    box("AlleyBox1", (-9.30, 1.80, .06), (.42, .46, .40), M["cardboard"], "06_Alley", bevel=.01, anchor='BOTTOM')
    box("AlleyBox2", (-9.40, 2.30, .06), (.36, .32, .32), M["cardboard"], "06_Alley", bevel=.01, anchor='BOTTOM')
    # noren at alley entrance
    for i in range(4):
        box(f"NorenPanel{i}", (-9.95+i*.235, -2.46, 2.45), (.21, .02, .62), M["noren"], "06_Alley", anchor='BOTTOM')
    cylinder("NorenRod", (-9.6, -2.48, 3.08), .025, 1.0, M["wood_dark"], "06_Alley", vertices=10, rot=(0,90*D2R,0))
    box("AlleySignBox", (-9.6, -2.52, 2.36), (.52, .05, .22), M["sign_white_soft"], "06_Alley", bevel=.01)
    text_obj("AlleySignText", "路地", (-9.6, -2.55, 2.36), .11, M["ink_unlit"], "06_Alley",
             rot=(90*D2R,0,0), extrude=.001, font=L.FONT_JP)
    # red lantern
    lx, ly, lz = -9.85, -1.90, 2.58
    cylinder("LanternRod", (lx, ly, lz+.55), .018, .48, M["steel_dark"], "06_Alley", vertices=8, rot=(0,90*D2R,0))
    ico("LanternBody", (lx, ly, lz), .20, M["lantern"], "06_Alley", subdiv=2, scale=(1,1,1.28))
    cylinder("LanternTop", (lx, ly, lz+.23), .11, .05, M["black"], "06_Alley", vertices=12)
    cylinder("LanternBot", (lx, ly, lz-.23), .11, .05, M["black"], "06_Alley", vertices=12)
    text_obj("LanternText", "酒", (lx, ly-.20, lz), .13, M["ink_unlit"], "06_Alley",
             rot=(90*D2R,0,0), extrude=.002, font=L.FONT_JP)
    point_light("LanternGlow", (lx, ly-.2, lz), 45, (1.0,0.25,0.08), .25)
    # string lights down the alley
    tube("AlleyString", [(-9.10, -2.2, 3.25), (-9.1, .0, 3.42), (-9.12, 2.6, 3.38), (-9.10, 5.6, 3.30), (-9.10, 8.7, 3.34)],
         .008, M["wire"], "06_Alley")
    for i in range(7):
        yy = -1.6 + i*1.5
        cylinder(f"AlleyBulb{i}", (-9.10, yy, 3.30), .045, .10, M["bulb"], "06_Alley", vertices=8)
        point_light(f"AlleyBulbGlow{i}", (-9.10, yy, 3.22), 10, (1.0,0.55,0.18), .12)
    # small service door on the east face of neighbor
    box("AlleyDoor", (-10.42, 7.1, .04), (.05, .85, 2.05), M["wood_dark"], "06_Alley", anchor='BOTTOM')
    text_obj("AlleyDoorText", "STAFF", (-10.46, 7.1, 1.72), .10, M["unlit_cream"], "06_Alley",
             rot=(90*D2R,0,90*D2R), extrude=.001, font=L.FONT_EN)
    # small step and mat
    box("AlleyStep", (-10.45, 7.1, .04), (.32, 1.02, .08), M["concrete"], "06_Alley", bevel=.01, anchor='BOTTOM')


def build_backdrop():
    # dark apartment block behind the store, kept low-contrast
    box("BackBlock", (-3.1, 11.15, 0.0), (11.8, 3.7, 7.4), M["neighbor"], "06_Alley", bevel=.03, anchor='BOTTOM')
    box("BackBlockParapet", (-3.1, 11.15, 7.4), (11.9, 3.8, .35), M["neighbor2"], "06_Alley", bevel=.02, anchor='BOTTOM')
    for fy, z in [(9.28, 4.1), (9.28, 5.8), (9.28, 7.0)]:
        for i, x in enumerate([-8.2, -6.2, -4.2, -2.2, -.2, 1.8]):
            lit = (i + int(z*2)) % 4 == 0
            mat = M["warm_curtain"] if lit else M["black"]
            box(f"BackWin{x}_{z}", (x, 9.27, z), (.60, .03, .66), mat, "06_Alley")
            box(f"BackWinFrame{x}_{z}", (x, 9.25, z-.02), (.70, .04, .76), M["steel_dark"], "06_Alley")
    # roof clutter
    cylinder("BackTank", (1.0, 11.2, 7.75), .60, 1.15, M["white"], "06_Alley", vertices=20, anchor='BOTTOM')
    for i, z in enumerate([7.8, 8.9]):
        torus(f"BackTankRing{i}", (1.0, 11.2, z), .62, .025, M["steel"], "06_Alley", major_segments=20, minor_segments=4)
    cylinder("BackMast", (-6.0, 11.4, 7.75), .03, 1.5, M["steel"], "06_Alley", vertices=8, anchor='BOTTOM')
    for i in range(3):
        box(f"BackMastBar{i}", (-6.0, 11.4, 8.05+i*.25), (.9-i*.2, .03, .03), M["steel"], "06_Alley")
    box("BackAC", (2.1, 9.95, 7.60), (.6, .45, .38), M["white"], "06_Alley", bevel=.02, anchor='BOTTOM')


def build_tree_and_bench():
    x, y = -10.95, -4.42
    box("TreePlanter", (x, y, .15), (.82, .82, .40), M["concrete"], "04_Props", bevel=.04, anchor='BOTTOM')
    box("TreeSoil", (x, y, .50), (.68, .68, .05), M["wood_dark"], "04_Props", anchor='BOTTOM')
    tube("TreeTrunk", [(x, y, .52), (x+.02, y, 1.45), (x-.04, y, 2.25), (x+.1, y, 2.95)], .085, M["trunk"], "04_Props")
    tube("TreeBranch1", [(x, y, 2.15), (x-.42, y-.16, 2.65), (x-.72, y-.2, 2.92)], .035, M["trunk"], "04_Props")
    tube("TreeBranch2", [(x, y, 2.40), (x+.52, y+.12, 2.78), (x+.82, y+.22, 3.08)], .030, M["trunk"], "04_Props")
    leaves = [
        (x-.55, y-.15, 2.95, .42, M["leaf1"]), (x-.05, y-.05, 3.15, .55, M["leaf2"]),
        (x+.48, y+.12, 2.90, .40, M["leaf3"]), (x-.15, y+.38, 2.75, .38, M["leaf1"]),
        (x+.20, y-.35, 2.60, .34, M["leaf2"]),
    ]
    for i, (lx, ly, lz, r, mat) in enumerate(leaves):
        ico(f"TreeLeaf{i}", (lx, ly, lz), r, mat, "04_Props", subdiv=2, scale=(1.1, 1.0, .8))
    # bench beneath tree facing the street
    box("BenchSeat", (x+1.05, y-.55, .48), (1.4, .42, .08), M["wood"], "04_Props", bevel=.03, anchor='BOTTOM')
    for i, dx in enumerate([-.55, .55]):
        box(f"BenchLeg{i}", (x+1.05+dx, y-.55, .15), (.08, .34, .34), M["steel_dark"], "04_Props", anchor='BOTTOM')
    box("BenchBack", (x+1.05, y-.77, .63), (1.4, .06, .38), M["wood"], "04_Props", bevel=.02, anchor='BOTTOM')
    for i in range(4):
        box(f"BenchSlat{i}", (x+1.05, y-.54, .53), (1.4, .08, .02), M["wood_dark"], "04_Props")


def build_postbox():
    x, y = 4.78, 5.62
    cylinder("PostboxBase", (x, y, .15), .30, .10, M["steel_dark"], "04_Props", vertices=20, anchor='BOTTOM')
    cylinder("PostboxBody", (x, y, .25), .27, 1.10, M["red_paint"], "04_Props", vertices=20, anchor='BOTTOM')
    cylinder("PostboxTop", (x, y, 1.35), .30, .14, M["red_paint"], "04_Props", vertices=20, anchor='BOTTOM')
    box("PostboxSlot", (x, y-.28, 1.05), (.34, .04, .10), M["black"], "04_Props")
    text_obj("PostboxMark", "〒", (x, y-.295, .86), .20, M["unlit_white"], "04_Props",
             rot=(90*D2R,0,0), extrude=.002, font=L.FONT_JP)


def build_street_typography_and_mirror():
    # painted stop warning on the wet road
    text_obj("RoadStop", "止まれ", (-6.0, -7.55, .046), 1.62, M["paint"], "01_Street",
             rot=(0, 0, 0), extrude=.002, font=L.FONT_JP)
    text_obj("RoadStopEn", "STOP", (-6.0, -8.48, .046), .48, M["paint"], "01_Street",
             rot=(0, 0, 0), extrude=.001, font=L.FONT_EN)
    box("RoadStopLine", (-6.0, -8.9, .040), (5.0, .18, .012), M["paint"], "01_Street")
    # convex corner mirror attached to the tall utility pole
    mx, my, mz = -11.88, -5.28, 3.05
    box("MirrorBracket", (-12.15, -5.15, mz), (.42, .05, .05), M["steel_dark"], "05_Utility")
    cylinder("MirrorBack", (mx, my, mz), .38, .05, M["mirror_rim"], "05_Utility",
             vertices=28, rot=(90*D2R, 0, 0))
    cylinder("MirrorGlass", (mx, my-.035, mz), .33, .02, M["mirror"], "05_Utility",
             vertices=28, rot=(90*D2R, 0, 0))
    torus("MirrorRim", (mx, my-.05, mz), .345, .025, M["mirror_rim"], "05_Utility",
          rot=(90*D2R, 0, 0), major_segments=28, minor_segments=5)
    text_obj("MirrorLabel", "カーブミラー", (mx, my-.06, 2.58), .08, M["unlit_cream"], "05_Utility",
             rot=(90*D2R, 0, 0), extrude=.001, font=L.FONT_JP)
    # security lamp on the tall pole
    box("PoleLampArm", (-12.15, -4.95, 4.15), (.55, .04, .04), M["steel_dark"], "05_Utility")
    box("PoleLampHousing", (-11.86, -4.95, 4.03), (.38, .16, .09), M["white"], "05_Utility", bevel=.02)
    box("PoleLampTube", (-11.86, -4.94, 3.97), (.30, .10, .025), M["cool_light"], "05_Utility")
    spot_light("PoleSecurityLight", (-11.86, -4.98, 3.96), 320, (0.72,0.86,1.0), 95,
               target=(-11.0, -4.4, .2), radius=.08)
    point_light("AlleyEntranceGlow", (-9.55, -2.15, 2.72), 70, (1.0, 0.45, 0.18), .35)

    # two nobori flags at the storefront
    for i, (x, y, col, txt, rotz) in enumerate([
        (-8.48, -3.12, M["sign_green"], "ほしみ", 8*D2R),
        (1.38, -3.15, M["sign_orange"], "24H", -6*D2R),
    ]):
        cylinder(f"NoboriPole{i}", (x, y, .15), .022, 2.25, M["steel"], "04_Props", vertices=8, anchor='BOTTOM')
        box(f"NoboriCloth{i}", (x+.24, y, 1.52), (.46, .018, 1.16), M["flag_cloth"], "04_Props", rot=(0,0,rotz), bevel=.005, anchor='BOTTOM')
        box(f"NoboriBand{i}", (x+.24, y-.012, 2.02), (.46, .012, .16), col, "04_Props", rot=(0,0,rotz), anchor='BOTTOM')
        text_obj(f"NoboriText{i}", txt, (x+.24, y-.022, 1.59), .18, M["ink_unlit"], "04_Props",
                 rot=(90*D2R,0,0), extrude=.001, font=L.FONT_JP if i==0 else L.FONT_EN)
    # small vertical OPEN sign at the corner column
    box("CornerOpenBox", (2.30, -2.50, 2.30), (.16, .34, .62), M["black"], "02_Building", bevel=.02)
    text_obj("CornerOpenText", "OPEN", (2.38, -2.50, 2.41), .11, M["neon_cyan"], "02_Building",
             rot=(90*D2R,0,90*D2R), extrude=.003, font=L.FONT_EN)
    text_obj("Corner24Text", "24H", (2.38, -2.50, 2.20), .10, M["neon_pink"], "02_Building",
             rot=(90*D2R,0,90*D2R), extrude=.003, font=L.FONT_EN)


def build_rain():
    import random
    random.seed(77)
    verts = []
    faces = []
    count = 0
    for i in range(650):
        x = random.uniform(-12.5, 12.5)
        y = random.uniform(-12.5, 12.5)
        # keep rain out of the store interior volume
        if -9.2 < x < 2.2 and -2.7 < y < 6.2:
            continue
        z = random.uniform(0.2, 15.0)
        ln = random.uniform(0.38, 0.78)
        dx, dy = random.uniform(-.06, .06), random.uniform(-.03, .03)
        w = .011
        p0 = (x, y, z)
        p1 = (x+dx, y+dy, z-ln)
        # quad perpendicular-ish to view
        v = len(verts)
        verts += [(p0[0]-w, p0[1], p0[2]), (p0[0]+w, p0[1], p0[2]),
                  (p1[0]+w, p1[1], p1[2]), (p1[0]-w, p1[1], p1[2])]
        faces.append((v, v+1, v+2, v+3))
        count += 1
    me = bpy.data.meshes.new("Rain_mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new("Rain", me)
    L.col("08_Rain").objects.link(ob)
    ob.data.materials.append(M["rain_mat"])
    ob.location.z = 0.0
    # animate gentle fall, still loopless within the shot
    ob.location.z = 0.0
    ob.keyframe_insert("location", frame=240)
    ob.location.z = -2.2
    ob.keyframe_insert("location", frame=288)
    for fc in L.action_fcurves(ob):
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
    print("RAIN", count)


def build_ground_reflections():
    # wet foreground puddles with broken neon streaks
    puddle_specs = [
        ("ForePuddle1", (-9.7, -8.5), [(-2.4,-1.0),(-1.2,-1.7),(.8,-1.5),(2.3,-.5),(1.5,.9),(-.4,1.2),(-2.2,.6)]),
        ("ForePuddle2", (-3.2, -6.8), [(-1.7,-.7),(-.6,-1.2),(1.2,-.9),(1.8,.2),(.5,1.0),(-1.1,.7)]),
        ("ForePuddle3", (7.2, -8.1), [(-1.3,-.7),(-.2,-1.1),(1.3,-.5),(1.5,.5),(.3,.9),(-.9,.5)]),
    ]
    for name, (x, y), pts in puddle_specs:
        polygon(name, (x, y, .043), pts, M["puddle"], "01_Street")
        for k in range(2):
            torus(f"{name}Ripple{k}", (x+random.uniform(-.7,.7), y+random.uniform(-.5,.5), .046),
                  .22+k*.25, .008, M["ripple"], "01_Street", major_segments=22, minor_segments=4)
    # long neon reflections, strongest in the foreground
    strips = [
        ("ReflectWarm1", (-3.3, -4.15, .163), (4.8, .10, .006), M["fake_reflect_warm"], 0),
        ("ReflectGreen", (-7.8, -4.55, .164), (2.0, .08, .006), M["fake_reflect_green"], -.08),
        ("ReflectPink", (-10.6, -2.10, .164), (1.2, .10, .006), M["fake_reflect_pink"], .3),
        ("ReflectCyan", (4.8, -4.55, .164), (1.8, .08, .006), M["fake_reflect_cyan"], .2),
        ("ReflectWarm2", (-9.4, -7.7, .048), (.22, 3.5, .006), M["fake_reflect_warm"], .02),
        ("ReflectWarm3", (-8.2, -8.8, .048), (.14, 2.2, .006), M["fake_reflect_warm"], -.02),
        ("ReflectRed", (3.55, -7.4, .048), (.18, 3.2, .006), M["fake_reflect_pink"], -.01),
        ("ReflectRed2", (4.05, -7.7, .048), (.10, 2.0, .006), M["fake_reflect_pink"], .02),
        ("ReflectBlue", (7.9, -7.0, .048), (.18, 2.8, .006), M["fake_reflect_cyan"], 0),
        ("ReflectGreen2", (-9.2, -7.2, .048), (.16, 2.6, .006), M["fake_reflect_green"], .02),
        ("ReflectPink2", (-9.8, -6.8, .048), (.11, 1.8, .006), M["fake_reflect_pink"], -.02),
    ]
    for name, loc, size, mat, rz in strips:
        box(name, loc, size, mat, "01_Street", rot=(0,0,rz))
    # glow pool from the store
    box("StoreGlowPool", (-3.2, -4.2, .163), (7.0, 2.1, .004), M["reflection_pool"], "01_Street")
    # broken reflections beneath sign / vending machines
    for i in range(10):
        x = -8.2 + random.uniform(0, 10.2)
        y = -4.6 + random.uniform(-.35, .35)
        box(f"SignRefl{i}", (x, y, .042), (random.uniform(.25,.7), .035, .005),
            M["fake_reflect_green" if i%3 else "fake_reflect_warm"], "01_Street")
    for i in range(6):
        box(f"VendRefl{i}", (3.9+random.uniform(-.35,.35), -5.5-i*.20, .048),
            (.12, random.uniform(.25,.55), .005), M["fake_reflect_pink" if i%2 else "fake_reflect_cyan"], "01_Street")
    # small wet glints / splash specks
    for i in range(40):
        x = random.uniform(-12, 12)
        y = random.uniform(-12.5, -5.8)
        box(f"RoadGlint{i}", (x, y, .049), (random.uniform(.06,.22), random.uniform(.012,.035), .004),
            M["fake_reflect_warm" if i%2 else "fake_reflect_cyan"], "01_Street", rot=(0,0,random.uniform(-.4,.4)))


# ------------------------------------------------------------------ scheduling
def schedule_all():
    # Remove any prior actions and animate every mesh by collection and height.
    import hashlib
    def h(name):
        return int(hashlib.md5(name.encode('utf-8')).hexdigest()[:6], 16) / 0xFFFFFF

    groups = {
        "00_Base": (0.00, .35, 'grow'),
        "01_Street": (0.30, .75, 'pop'),
        "02_Building": (1.55, .30, 'grow'),
        "03_Interior": (3.20, .35, 'pop'),
        "04_Props": (5.30, .75, 'pop'),
        "05_Utility": (6.55, .70, 'pop'),
        "06_Alley": (4.55, .65, 'pop'),
        "07_Wires": (8.10, .45, 'pop'),
    }
    for name, (base, spread, mode_default) in groups.items():
        c = bpy.data.collections.get(name)
        if not c:
            continue
        for ob in c.objects:
            if ob.type != 'MESH':
                continue
            if getattr(ob, "animation_data", None) and ob.animation_data.action:
                continue
            bb = [ob.matrix_world @ Vector(corner) for corner in ob.bound_box]
            zmin = min(v.z for v in bb)
            zmax = max(v.z for v in bb)
            height = zmax - zmin
            r = h(ob.name)
            if name == "00_Base":
                start = base + r * .15
            elif name == "01_Street":
                start = base + r * spread + max(0, min(1, (zmin+.5)/1.5))*.35
            elif name == "02_Building":
                start = base + max(0, zmin)*.20 + r*.45
            elif name == "03_Interior":
                start = base + max(0, zmin)*.20 + r*.55
            elif name == "06_Alley":
                start = base + max(0, zmin)*.16 + r*.55
            elif name == "05_Utility":
                start = base + max(0, zmin)*.15 + r*.55
            elif name == "07_Wires":
                start = base + r*.55
            else:
                start = base + max(0, zmin)*.12 + r*spread
            mode = 'grow' if (height > 1.2 and zmin < 1.0) else 'pop'
            if name in ("02_Building", "06_Alley") and height > 1.0:
                mode = 'grow'
            anim(ob, start, .48 + r*.16, mode, drop=.55)
    print("SCHEDULED", len(L.ASSEMBLY), "meshes")


def animate_lights_and_camera(cam):
    # moon and ambient
    for nm in ["MoonKey", "FillWest", "FillSouth"]:
        ob = bpy.data.objects.get(nm)
        if ob:
            final = ob.data.energy
            fade_light(ob, 0.0, 1.6, final)
    for nm in ["BaseRim", "GroundBounceWarm"]:
        ob = bpy.data.objects.get(nm)
        if ob:
            final = ob.data.energy
            fade_light(ob, 1.2, 3.0, final)
    for nm in ["InteriorWarm1", "InteriorWarm2", "InteriorWarm3", "InteriorWarm4", "StoreSpill"]:
        ob = bpy.data.objects.get(nm)
        if ob:
            final = ob.data.energy
            fade_light(ob, 3.4, 5.8, final)
    for nm in ["VendingLightPoint0", "VendingLightPoint1", "VendingGlow", "AlleyNeon",
               "SnackSignGlow", "LanternGlow", "StreetLampSpot", "StreetLampGlow",
               "BoardLampGlow", "AlleyBulbGlow1", "AlleyBulbGlow3", "AlleyBulbGlow5"]:
        ob = bpy.data.objects.get(nm)
        if ob:
            final = ob.data.energy
            fade_light(ob, 7.0 + random.random()*.8, 8.6 + random.random()*.5, final)

    # gentle camera drift, still a clean three-quarter view
    f0, f1, f2 = 1, 140, 288
    key_frames = [
        (f0, (-37.0, -38.5, 24.0), (-0.2, -0.1, 2.4)),
        (f1, (-35.6, -40.8, 22.7), (-0.3, 0.0, 2.3)),
        (f2, (-34.5, -42.5, 21.5), (-0.4, 0.0, 2.2)),
    ]
    for fr, loc, tgt in key_frames:
        cam.location = loc
        d = Vector(tgt) - cam.location
        cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        cam.keyframe_insert("location", frame=fr)
        cam.keyframe_insert("rotation_euler", frame=fr)


# ------------------------------------------------------------------ call build
def main():
    L.reset_scene()
    L.make_collections()
    L.load_fonts()
    build_materials()
    build_extra_materials()
    build_base()
    build_street()
    build_store_shell()
    build_rooftop_life()
    build_interior()
    # street props and surroundings
    build_vending_and_bins()
    build_bicycle()
    build_umbrella_stand()
    build_doormat_and_aboard()
    build_street_lamp()
    build_utility_poles()
    build_street_signs()
    build_guardrail()
    build_bulletin_board()
    build_air_conditioners()
    build_alley()
    build_backdrop()
    build_tree_and_bench()
    build_postbox()
    build_street_typography_and_mirror()
    build_ground_reflections()
    build_rain()

    # camera / render
    L.setup_render(bpy.context.scene, samples=48, freestyle=True, res=1600)
    cam = L.add_camera(loc=(-34.5, -42.5, 21.5), target=(-0.4, 0.0, 2.2), lens=55)
    # lights
    area_light("MoonKey", (16, -12, 22), 850, (0.58, 0.70, 1.0), 14, target=(0, 0, 2.5), shape='DISK')
    area_light("FillWest", (-17, -8, 12), 380, (0.55, 0.48, 1.0), 9, target=(-3, 0, 2.0), shape='DISK')
    area_light("FillSouth", (8, -20, 12), 300, (0.52, 0.62, 1.0), 10, target=(0, -3, 2.0), shape='DISK')
    area_light("StoreSpill", (-2.0, -4.2, 2.4), 1250, (1.0, 0.65, 0.35), 4.5, target=(-2, -1, 1.2), shape='DISK')
    point_light("InteriorWarm1", (-6.2, 1.2, 2.6), 300, (1.0, 0.72, 0.42), .5)
    point_light("InteriorWarm2", (-2.2, 1.8, 2.6), 330, (1.0, 0.73, 0.43), .5)
    point_light("InteriorWarm3", (-4.8, 4.6, 2.6), 280, (1.0, 0.72, 0.42), .5)
    point_light("InteriorWarm4", (0.2, .1, 2.65), 190, (1.0, 0.80, 0.55), .35)
    point_light("VendingGlow", (3.8, -3.9, 1.35), 90, (0.45, 0.75, 1.0), .25)
    point_light("AlleyNeon", (-9.6, 0.6, 2.8), 160, (1.0, 0.15, 0.4), .3)
    # subtle ground bounce
    point_light("GroundBounceWarm", (-3.0, -3.0, .6), 90, (1.0, 0.62, 0.35), 1.5)
    point_light("BaseRim", (0, -9.0, -0.2), 45, (0.35, 0.55, 1.0), 3.0)

    # convert procedural text / curves so glTF can carry every detail
    L.convert_texts_to_mesh()
    L.convert_curves_to_mesh()
    schedule_all()
    L.apply_assembly()
    animate_lights_and_camera(cam)
    # soft hero light at the end
    bpy.context.scene.frame_end = 288
    bpy.context.scene.frame_set(288)
    L.save_blend(BLEND_PATH)


if __name__ == "__main__":
    main()
