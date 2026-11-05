# -*- coding: utf-8 -*-
"""Reusable helpers for the rainy konbini diorama."""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

TAU = math.tau
D2R = math.pi / 180.0

ASSEMBLY = []
MATS = {}
COLLECTIONS = {}
FONT_JP = None
FONT_EN = None


# ------------------------------------------------------------------ scene
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x = 1400
    sc.render.resolution_y = 1400
    sc.render.resolution_percentage = 100
    sc.render.fps = 24
    sc.frame_start = 1
    sc.frame_end = 288
    return sc


def make_collections():
    root = bpy.data.collections.new("RAINY_KONBINI")
    bpy.context.scene.collection.children.link(root)
    names = [
        "00_Base", "01_Street", "02_Building", "03_Interior",
        "04_Props", "05_Utility", "06_Alley", "07_Wires", "08_Rain",
        "09_Lights", "10_Camera", "90_AnimHelpers",
    ]
    for n in names:
        c = bpy.data.collections.new(n)
        root.children.link(c)
        COLLECTIONS[n] = c
    return root


def col(name):
    return COLLECTIONS[name]


def link_obj(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


# ------------------------------------------------------------------ materials
def _set_input(node, name, value):
    inp = node.inputs.get(name)
    if inp is not None:
        inp.default_value = value


def material(name, color, rough=0.72, metallic=0.0, emission=None,
             emission_strength=0.0, alpha=1.0, spec=0.35, backface=False):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (380, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (80, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    _set_input(bsdf, "Base Color", (*color[:3], 1.0))
    _set_input(bsdf, "Roughness", rough)
    _set_input(bsdf, "Metallic", metallic)
    _set_input(bsdf, "IOR", 1.45)
    _set_input(bsdf, "Specular IOR Level", spec)
    _set_input(bsdf, "Alpha", alpha)
    if emission is not None:
        _set_input(bsdf, "Emission Color", (*emission[:3], 1.0))
        _set_input(bsdf, "Emission Strength", emission_strength)
    if alpha < 0.999:
        try:
            m.surface_render_method = 'DITHERED'
        except Exception:
            pass
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
        m.use_transparency_overlap = False
    if backface:
        m.use_backface_culling = False
    m.diffuse_color = (*color[:3], alpha)
    m.roughness = rough
    m.metallic = metallic
    MATS[name] = m
    return m


def glass_material(name, tint=(0.55, 0.72, 0.85), alpha=0.13, reflect=0.55):
    m = material(name, tint, rough=0.05, metallic=0.15, alpha=alpha, spec=reflect)
    try:
        m.surface_render_method = 'BLENDED'
        # Opaque shadows keep moonlight from washing out the lit interior.
        m.use_transparent_shadow = False
    except Exception:
        pass
    return m


def emission_material(name, color, strength=2.0, base=None):
    base = base or color
    return material(name, base, rough=0.5, emission=color, emission_strength=strength)


def unlit_material(name, color):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color[:3], 1.0)
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    m.diffuse_color = (*color[:3], 1.0)
    MATS[name] = m
    return m


# ------------------------------------------------------------------ mesh primitives
def _new_mesh_obj(name, verts, faces, mat, loc, rot, collection, smooth=False):
    me = bpy.data.meshes.new(name + "_mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    if mat is not None:
        ob.data.materials.append(mat)
    return ob


def box(name, loc, size, mat, collection="04_Props", rot=(0, 0, 0),
        bevel=0.0, segments=2, anchor='CENTER', smooth=False, parent=None):
    sx, sy, sz = size
    if anchor == 'BOTTOM':
        z0, z1 = 0.0, sz
    else:
        z0, z1 = -sz * 0.5, sz * 0.5
    x0, x1 = -sx * 0.5, sx * 0.5
    y0, y1 = -sy * 0.5, sy * 0.5
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    ob = _new_mesh_obj(name, verts, faces, mat, loc, rot, col(collection), smooth)
    if bevel > 0:
        mod = ob.modifiers.new("soft_edges", 'BEVEL')
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = 'ANGLE'
        mod.angle_limit = math.radians(40)
    if parent:
        ob.parent = parent
    return ob


def plane(name, loc, size, mat, collection="04_Props", rot=(0, 0, 0)):
    sx, sy = size
    verts = [(-sx/2, -sy/2, 0), (sx/2, -sy/2, 0), (sx/2, sy/2, 0), (-sx/2, sy/2, 0)]
    return _new_mesh_obj(name, verts, [(0, 1, 2, 3)], mat, loc, rot, col(collection))


def polygon(name, loc, points, mat, collection="04_Props", rot=(0, 0, 0), z=0.0):
    verts = [(x, y, z) for x, y in points]
    return _new_mesh_obj(name, verts, [tuple(range(len(points)))], mat, loc, rot, col(collection))


def cylinder(name, loc, radius, depth, mat, collection="04_Props", rot=(0, 0, 0),
             vertices=20, smooth=True, radius2=None, anchor='CENTER', bevel=0.0):
    me = bpy.data.meshes.new(name + "_mesh")
    bm = bmesh.new()
    if radius2 is None:
        radius2 = radius
    z0 = 0 if anchor == 'BOTTOM' else -depth/2
    z1 = depth if anchor == 'BOTTOM' else depth/2
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=vertices,
                          radius1=radius, radius2=radius2, depth=depth)
    bm.to_mesh(me)
    bm.free()
    me.update()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    col(collection).objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    if mat:
        ob.data.materials.append(mat)
    if bevel > 0:
        mod = ob.modifiers.new("rim", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
    return ob


def torus(name, loc, major, minor, mat, collection="04_Props", rot=(0, 0, 0),
          major_segments=32, minor_segments=8):
    me = bpy.data.meshes.new(name + "_mesh")
    bm = bmesh.new()
    for i in range(major_segments):
        a = TAU * i / major_segments
        for j in range(minor_segments):
            b = TAU * j / minor_segments
            x = (major + minor * math.cos(b)) * math.cos(a)
            y = (major + minor * math.cos(b)) * math.sin(a)
            z = minor * math.sin(b)
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    for i in range(major_segments):
        for j in range(minor_segments):
            v1 = bm.verts[i * minor_segments + j]
            v2 = bm.verts[((i + 1) % major_segments) * minor_segments + j]
            v3 = bm.verts[((i + 1) % major_segments) * minor_segments + (j + 1) % minor_segments]
            v4 = bm.verts[i * minor_segments + (j + 1) % minor_segments]
            bm.faces.new((v1, v2, v3, v4))
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    col(collection).objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    ob.data.materials.append(mat)
    return ob


def ico(name, loc, radius, mat, collection="04_Props", subdiv=2, scale=(1, 1, 1)):
    me = bpy.data.meshes.new(name + "_mesh")
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    col(collection).objects.link(ob)
    ob.location = loc
    ob.scale = scale
    ob.data.materials.append(mat)
    return ob


def tube(name, points, radius, mat, collection="04_Props", resolution=2, cyclic=False):
    cu = bpy.data.curves.new(name + "_curve", 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = resolution
    cu.bevel_depth = radius
    cu.bevel_resolution = 2
    cu.resolution_u = 4
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(points) - 1)
    for bp, p in zip(sp.bezier_points, points):
        bp.co = Vector(p)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    sp.use_cyclic_u = cyclic
    ob = bpy.data.objects.new(name, cu)
    col(collection).objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def curve_line(name, points, radius, mat, collection="04_Props", poly=False):
    cu = bpy.data.curves.new(name + "_curve", 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 2
    cu.bevel_depth = radius
    cu.bevel_resolution = 1
    if poly:
        sp = cu.splines.new('POLY')
    else:
        sp = cu.splines.new('BEZIER')
    sp.points.add(len(points) - 1) if poly else sp.bezier_points.add(len(points) - 1)
    if poly:
        for p, (x, y, z) in zip(sp.points, points):
            p.co = (x, y, z, 1.0)
    else:
        for bp, p in zip(sp.bezier_points, points):
            bp.co = Vector(p)
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new(name, cu)
    col(collection).objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def text_obj(name, body, loc, size, mat, collection="04_Props", rot=(90*D2R, 0, 0),
             extrude=0.008, align='CENTER', font=None, spacing=1.0, parent=None,
             bevel=0.0):
    cu = bpy.data.curves.new(name + "_txt", 'FONT')
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.align_y = 'CENTER'
    cu.extrude = extrude
    cu.bevel_depth = bevel
    cu.space_character = spacing
    if font is not None:
        cu.font = font
    ob = bpy.data.objects.new(name, cu)
    col(collection).objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    ob.data.materials.append(mat)
    if parent:
        ob.parent = parent
    return ob


def load_fonts():
    global FONT_JP, FONT_EN
    for p in [r"C:\Windows\Fonts\YuGothB.ttc", r"C:\Windows\Fonts\msgothic.ttc"]:
        try:
            FONT_JP = bpy.data.fonts.load(p)
            break
        except Exception:
            pass
    for p in [r"C:\Windows\Fonts\bahnschrift.ttf", r"C:\Windows\Fonts\ARIALNB.TTF",
              r"C:\Windows\Fonts\NotoSans-Bold.ttf"]:
        try:
            FONT_EN = bpy.data.fonts.load(p)
            break
        except Exception:
            pass
    print("FONTS", FONT_JP.name if FONT_JP else None, FONT_EN.name if FONT_EN else None)
    return FONT_JP, FONT_EN


def convert_texts_to_mesh():
    for ob in list(bpy.data.objects):
        if ob.type == 'FONT':
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            try:
                bpy.ops.object.convert(target='MESH')
            except Exception as e:
                print("text convert failed", ob.name, e)
            ob.select_set(False)


def convert_curves_to_mesh():
    for ob in list(bpy.data.objects):
        if ob.type == 'CURVE':
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            try:
                bpy.ops.object.convert(target='MESH')
            except Exception as e:
                print("curve convert failed", ob.name, e)
            ob.select_set(False)


# ------------------------------------------------------------------ lights
def area_light(name, loc, energy, color, size, target=None, shape='DISK', size_y=None):
    data = bpy.data.lights.new(name + "_data", 'AREA')
    data.energy = energy
    data.color = color
    data.shape = shape
    data.size = size
    if size_y:
        data.size_y = size_y
    ob = bpy.data.objects.new(name, data)
    col("09_Lights").objects.link(ob)
    ob.location = loc
    if target is not None:
        point_at(ob, target)
    return ob


def point_light(name, loc, energy, color, radius=0.15, target=None):
    data = bpy.data.lights.new(name + "_data", 'POINT')
    data.energy = energy
    data.color = color
    data.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, data)
    col("09_Lights").objects.link(ob)
    ob.location = loc
    if target is not None:
        point_at(ob, target)
    return ob


def spot_light(name, loc, energy, color, size_deg=45, target=(0, 0, 0), radius=0.2):
    data = bpy.data.lights.new(name + "_data", 'SPOT')
    data.energy = energy
    data.color = color
    data.spot_size = size_deg * D2R
    data.spot_blend = 0.35
    data.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, data)
    col("09_Lights").objects.link(ob)
    ob.location = loc
    point_at(ob, target)
    return ob


def point_at(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def sun_light(name, rot, energy, color, angle=2.0):
    data = bpy.data.lights.new(name + "_data", 'SUN')
    data.energy = energy
    data.color = color
    data.angle = angle * D2R
    ob = bpy.data.objects.new(name, data)
    col("09_Lights").objects.link(ob)
    ob.rotation_euler = rot
    return ob


# ------------------------------------------------------------------ animation
def anim(ob, start_s, dur_s=0.5, mode='pop', drop=0.55, collection=None, tag=None):
    ASSEMBLY.append({
        "obj": ob, "start": int(round(1 + start_s * 24)),
        "dur": max(2, int(round(dur_s * 24))), "mode": mode,
        "drop": drop, "tag": tag,
    })
    return ob


def action_fcurves(ob):
    """Return every f-curve of an object's action (Blender 4.4+ layered actions)."""
    ad = getattr(ob, "animation_data", None)
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves"):
        return list(act.fcurves)
    curves = []
    for layer in getattr(act, "layers", []):
        for strip in getattr(layer, "strips", []):
            for bag in getattr(strip, "channelbags", []):
                curves.extend(list(bag.fcurves))
    return curves


def _insert_transform(ob, frame, loc, scale, rot=None):
    ob.location = loc
    ob.scale = scale
    if rot is not None:
        ob.rotation_euler = rot
    ob.keyframe_insert(data_path="location", frame=frame)
    ob.keyframe_insert(data_path="scale", frame=frame)
    if rot is not None:
        ob.keyframe_insert(data_path="rotation_euler", frame=frame)


def apply_assembly():
    """Staggered pop-in with a subtle rise, and bottom-up growth for shells."""
    for item in ASSEMBLY:
        ob = item["obj"]
        if ob.name not in bpy.data.objects:
            continue
        f0 = item["start"]
        dur = item["dur"]
        f1 = f0 + max(1, int(dur * 0.62))
        f2 = f0 + dur
        final_loc = ob.location.copy()
        final_scale = ob.scale.copy()
        final_rot = ob.rotation_euler.copy()
        mode = item["mode"]
        # extras for the web viewer's independent assembly animation
        try:
            ob["asm_t0"] = round((f0 - 1) / 24.0, 4)
            ob["asm_t1"] = round((f2 - 1) / 24.0, 4)
            ob["asm_mode"] = mode
            ob["asm_drop"] = float(item.get("drop", 0.55))
        except Exception:
            pass
        if mode == 'grow':
            s0 = (0.985, 0.985, 0.002)
            s1 = (1.015, 1.015, 1.015)
            l0 = final_loc.copy()
            l1 = final_loc.copy()
        elif mode == 'drop':
            s0 = (0.001, 0.001, 0.001)
            s1 = (1.04, 1.04, 1.04)
            l0 = final_loc + Vector((0, 0, item["drop"]))
            l1 = final_loc + Vector((0, 0, 0.035))
        elif mode == 'slide':
            s0 = (0.001, 0.001, 0.001)
            s1 = (1.03, 1.03, 1.03)
            l0 = final_loc + Vector((0.32, 0, 0))
            l1 = final_loc + Vector((-0.015, 0, 0))
        else:  # pop
            s0 = (0.001, 0.001, 0.001)
            s1 = (1.07, 1.07, 1.07)
            l0 = final_loc + Vector((0, 0, 0.09))
            l1 = final_loc + Vector((0, 0, 0.028))
        _insert_transform(ob, f0, l0, s0, final_rot)
        _insert_transform(ob, f1, l1, s1, final_rot)
        _insert_transform(ob, f2, final_loc, final_scale, final_rot)
        # ease
        for fc in action_fcurves(ob):
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'
    print("ANIMATED", len(ASSEMBLY), "objects")


def fade_light(ob, start_s, end_s, final_energy):
    data = ob.data
    f0 = int(1 + start_s * 24)
    f1 = int(1 + end_s * 24)
    data.energy = 0.0
    data.keyframe_insert(data_path="energy", frame=f0)
    data.energy = final_energy * 0.25
    data.keyframe_insert(data_path="energy", frame=int((f0 + f1) / 2))
    data.energy = final_energy
    data.keyframe_insert(data_path="energy", frame=f1)


def fade_emission(mat, start_s, end_s, final_strength):
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        return
    inp = bsdf.inputs.get("Emission Strength")
    if not inp:
        return
    f0 = int(1 + start_s * 24)
    f1 = int(1 + end_s * 24)
    inp.default_value = 0.0
    inp.keyframe_insert("default_value", frame=f0)
    inp.default_value = final_strength
    inp.keyframe_insert("default_value", frame=f1)


# ------------------------------------------------------------------ render
def setup_render(sc, samples=48, freestyle=True, res=1400):
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x = res
    sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.fps = 24
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.eevee.taa_render_samples = samples
    sc.eevee.use_shadows = True
    sc.eevee.use_raytracing = True
    try:
        sc.eevee.ray_tracing_options.resolution_scale = 1
        sc.eevee.ray_tracing_options.use_denoise = True
    except Exception:
        pass
    try:
        sc.eevee.shadow_resolution_scale = 2
        sc.eevee.shadow_pool_size = '2048'
        sc.eevee.shadow_ray_count = 1
        sc.eevee.shadow_step_count = 6
    except Exception:
        pass
    sc.render.film_transparent = False
    # Color management: crisp cel-animation palette, controlled highlights.
    try:
        sc.view_settings.view_transform = 'Standard'
        sc.view_settings.look = 'None'
    except Exception:
        try:
            sc.view_settings.view_transform = 'Filmic'
            sc.view_settings.look = 'Medium High Contrast'
        except Exception:
            pass
    sc.view_settings.exposure = 1.02
    sc.view_settings.gamma = 1.0

    # Freestyle ink lines
    sc.render.use_freestyle = freestyle
    if freestyle:
        vl = sc.view_layers[0]
        vl.use_freestyle = True
        fs = vl.freestyle_settings
        fs.crease_angle = math.radians(125)
        fs.use_smoothness = True
        while len(fs.linesets) > 0:
            fs.linesets.remove(fs.linesets[0])
        ls = fs.linesets.new("Ink")
        ls.select_silhouette = True
        ls.select_border = True
        ls.select_contour = True
        ls.select_crease = True
        ls.select_external_contour = True
        ls.select_material_boundary = False
        ls.select_suggestive_contour = False
        ls.select_ridge_valley = False
        ls.select_edge_mark = True
        st = ls.linestyle
        st.color = (0.018, 0.024, 0.055)
        st.thickness = 1.40
        st.alpha = 0.92
        # Slight taper so small props read lighter
        try:
            st.caps = 'ROUND'
        except Exception:
            pass

    # World: deep indigo rainy night
    world = bpy.data.worlds.new("RainyNightWorld")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.010, 0.017, 0.036, 1)
    bg.inputs["Strength"].default_value = 0.38
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    # Compositor (Blender 5.x uses a compositing node group)
    sc.use_nodes = True
    tree = bpy.data.node_groups.new("KonbiniCompositor", 'CompositorNodeTree')
    tree.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    sc.compositing_node_group = tree
    rl = tree.nodes.new("CompositorNodeRLayers")
    rl.location = (-650, 0)
    glare = tree.nodes.new("CompositorNodeGlare")
    glare.location = (-430, 0)
    glare.inputs["Type"].default_value = 'Fog Glow'
    glare.inputs["Quality"].default_value = 'High'
    glare.inputs["Threshold"].default_value = 0.85
    glare.inputs["Strength"].default_value = 1.15
    glare.inputs["Size"].default_value = 7
    glare.inputs["Saturation"].default_value = 1.05
    tree.links.new(rl.outputs["Image"], glare.inputs["Image"])

    hs = tree.nodes.new("CompositorNodeHueSat")
    hs.location = (-170, 0)
    hs.inputs["Saturation"].default_value = 1.28
    hs.inputs["Value"].default_value = 1.02
    tree.links.new(glare.outputs["Image"], hs.inputs["Image"])

    lens = tree.nodes.new("CompositorNodeLensdist")
    lens.location = (60, 0)
    lens.inputs["Distortion"].default_value = -0.008
    lens.inputs["Dispersion"].default_value = 0.012
    lens.inputs["Fit"].default_value = True
    tree.links.new(hs.outputs["Image"], lens.inputs["Image"])

    out = tree.nodes.new("NodeGroupOutput")
    out.location = (300, 0)
    tree.links.new(lens.outputs["Image"], out.inputs["Image"])
    print("RENDER SETUP", sc.render.engine, samples, "freestyle", freestyle)


def add_camera(loc=(-27.5, -31.0, 21.5), target=(0.2, 0.2, 3.1), lens=58):
    data = bpy.data.cameras.new("Camera")
    data.lens = lens
    data.sensor_width = 36
    ob = bpy.data.objects.new("Camera", data)
    col("10_Camera").objects.link(ob)
    ob.location = loc
    point_at(ob, target)
    bpy.context.scene.camera = ob
    return ob


# ------------------------------------------------------------------ misc
def smooth_shade(obj):
    if obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True


def apply_modifiers(obj):
    bpy.context.view_layer.objects.active = obj
    for m in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=m.name)
        except Exception:
            pass


def save_blend(path):
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print("SAVED", path)
