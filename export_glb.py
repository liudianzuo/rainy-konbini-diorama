# -*- coding: utf-8 -*-
import bpy, os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0,HERE)
import scene_lib as L
sc=bpy.context.scene
sc.frame_set(288)
# Bake the fully assembled frame into static node transforms.  The web viewer
# plays its own assembly animation from the per-object `asm_*` extras.
for ob in list(bpy.data.objects):
    if ob.type == 'MESH':
        mw = ob.matrix_world.copy()
        if ob.animation_data:
            ob.animation_data_clear()
        ob.matrix_world = mw
# The viewer adds live volumetric rain; keep the glb light.
rain=bpy.data.objects.get('Rain')
if rain:
    bpy.data.objects.remove(rain, do_unlink=True)
# Make sure no camera/lights are selected; export everything visible.
for ob in bpy.context.selected_objects:
    ob.select_set(False)
out=os.path.join(HERE,'rainy_konbini.glb')
bpy.ops.export_scene.gltf(
    filepath=out,
    export_format='GLB',
    use_selection=False,
    export_apply=True,
    export_yup=True,
    export_extras=True,
    export_animations=False,
    export_lights=False,
    export_cameras=False,
    export_materials='EXPORT',
    export_image_format='AUTO',
    export_normals=True,
    export_tangents=False,
    export_texcoords=False,
)
print('GLB SIZE', os.path.getsize(out))
