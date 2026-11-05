# -*- coding: utf-8 -*-
import bpy, os
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__))
sc=bpy.context.scene
cam=sc.camera
sc.frame_set(288)
if cam.animation_data: cam.animation_data_clear()
cam.location=(-34.5,-42.5,21.5)
d=Vector((-0.4,0.0,2.2))-cam.location
cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
cam.data.lens=55
sc.render.resolution_x=1400
sc.render.resolution_y=1400
sc.render.resolution_percentage=100
sc.eevee.taa_render_samples=28
sc.render.use_freestyle=True
sc.render.filepath=os.path.join(HERE,'renders','rainy_konbini_hero.png')
bpy.ops.render.render(write_still=True)
print('HERO DONE')
rain=bpy.data.objects.get('Rain')
if rain: rain.hide_render=True
cam.location=(-4.2,-12.5,2.9)
d=Vector((-3.5,1.6,1.9))-cam.location
cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
cam.data.lens=45
sc.render.resolution_x=1400
sc.render.resolution_y=900
sc.eevee.taa_render_samples=22
sc.render.filepath=os.path.join(HERE,'renders','konbini_storefront.png')
bpy.ops.render.render(write_still=True)
print('CLOSE DONE')
