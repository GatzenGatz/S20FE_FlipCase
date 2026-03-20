"""
FlipCase Animation Script for Blender
======================================
Animation sequence:
  0–60   : Phone spins in place (360° on Z)
  60–120 : Phone drops/snaps into the case (case rises up to meet it)
  120–180: Case morphs/cross-fades into the flipcase (scale + opacity trick)
  180–240: Flipcase cover swings shut (hinge rotation on X)

HOW TO USE
----------
1. Open Blender (3.x or 4.x).
2. Go to the Scripting workspace.
3. Paste / open this file.
4. Edit the three STL_* paths below to match where your files are.
5. Press "Run Script".
6. Switch to the Timeline / Animation workspace and hit Space to preview.
   Render > Render Animation for a full export.

DEPENDENCIES
------------
- Blender 3.3+ or 4.x (auto-detects correct STL importer)
- STL files: phone.stl, case.stl, flipcase.stl
"""

import bpy
import math
import os

# ── USER SETTINGS ────────────────────────────────────────────────────────────

# Adjust these paths to wherever your STL files live.
# You can use an absolute path, e.g. r"C:\Users\You\Desktop\phone.stl"
STL_PHONE    = "//phone.stl"       # '//' means relative to the .blend file
STL_CASE     = "//case.stl"
STL_FLIPCASE = "//flipcase.stl"

FPS          = 24
TOTAL_FRAMES = 240   # 10 seconds @ 24 fps

# Phone dimensions from SCAD (mm → Blender units, 1 unit = 1 mm here)
PHONE_HEIGHT = 8.4   # h
PHONE_LENGTH = 159.8 # l
THICKNESS    = 1.5

# ── HELPERS ──────────────────────────────────────────────────────────────────

def set_frame(f):
    bpy.context.scene.frame_set(f)

def insert_kf(obj, data_path, frame=None):
    if frame is not None:
        bpy.context.scene.frame_set(frame)
    obj.keyframe_insert(data_path=data_path)

def ease_in_out(fcurves):
    """Set all keyframes on an object's fcurves to BEZIER with AUTO handles."""
    for fc in fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type  = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'

def import_stl(path, name):
    filepath = bpy.path.abspath(path)
    # Blender 4.0+ moved STL import; try new operator first, fall back to old
    try:
        bpy.ops.wm.stl_import(filepath=filepath)
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=filepath)
    obj = bpy.context.selected_objects[0]
    obj.name = name
    return obj

def center_origin(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')

def add_material(obj, name, color, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND' if alpha < 1.0 else 'OPAQUE'
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Alpha"].default_value = alpha
        bsdf.inputs["Roughness"].default_value = 0.25
        bsdf.inputs["Metallic"].default_value = 0.15
        bsdf.inputs["Specular IOR Level"].default_value = 0.5
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return mat

def set_blend_mode(obj, mode):
    """Switch material blend mode (needed when alpha animates through transparent)."""
    if obj.data.materials:
        obj.data.materials[0].blend_method = mode

def set_alpha(obj, alpha, frame):
    mat = obj.data.materials[0]
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Alpha"].default_value = alpha
        bsdf.inputs["Alpha"].keyframe_insert("default_value", frame=frame)

# ── SCENE SETUP ──────────────────────────────────────────────────────────────

scene = bpy.context.scene
scene.render.fps = FPS

# Dark world background so we dont get a gray render
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.02, 0.02, 0.02, 1.0)
    bg.inputs["Strength"].default_value = 0.5
scene.frame_start = 1
scene.frame_end = TOTAL_FRAMES

# Remove default cube / light / camera if present, keep camera & light useful
for obj in list(bpy.data.objects):
    if obj.name in ("Cube",):
        bpy.data.objects.remove(obj, do_unlink=True)

# Camera
if "Camera" not in bpy.data.objects:
    bpy.ops.object.camera_add(location=(0, -400, 150))
    cam = bpy.context.object
    cam.name = "Camera"
else:
    cam = bpy.data.objects["Camera"]
cam.location = (0, -400, 150)
cam.rotation_euler = (math.radians(70), 0, 0)
cam.data.lens = 50
# Track-to constraint so camera always faces the scene center
if "Track To" not in [c.name for c in cam.constraints]:
    track = cam.constraints.new(type="TRACK_TO")
    track.name = "Track To"
    track.target = None  # will track world origin
    track.up_axis = "UP_Y"
    track.track_axis = "TRACK_NEGATIVE_Z"
scene.camera = cam

# Key light
if "Sun" not in bpy.data.objects:
    bpy.ops.object.light_add(type='SUN', location=(100, -100, 200))
    sun = bpy.context.object
    sun.name = "Sun"
    sun.data.energy = 3.0

# Fill light
bpy.ops.object.light_add(type='AREA', location=(-100, -50, 100))
fill = bpy.context.object
fill.name = "Fill"
fill.data.energy = 500

# ── IMPORT OBJECTS ───────────────────────────────────────────────────────────

phone    = import_stl(STL_PHONE,    "Phone")
case_obj = import_stl(STL_CASE,     "Case")
flip_obj = import_stl(STL_FLIPCASE, "FlipCase")

for o in (phone, case_obj, flip_obj):
    center_origin(o)

# Materials
add_material(phone,    "PhoneMat",    (0.05, 0.05, 0.05))   # near-black
add_material(case_obj, "CaseMat",     (0.2,  0.5,  0.9))    # blue
add_material(flip_obj, "FlipcaseMat", (0.15, 0.4,  0.75))   # slightly deeper blue

# ── INITIAL POSITIONS ────────────────────────────────────────────────────────
# Everything starts at origin; we'll animate from there.

# Phone: sits above where the case will be, centred
PHONE_START_Z  = PHONE_HEIGHT / 2 + THICKNESS + 60   # floating above
PHONE_REST_Z   = PHONE_HEIGHT / 2 + THICKNESS         # seated inside case

phone.location    = (0, 0, PHONE_START_Z)
phone.rotation_euler = (0, 0, 0)

# Case: starts just below where it will be, rises to meet phone
CASE_START_Z = -20
CASE_REST_Z  = 0

case_obj.location = (0, 0, CASE_START_Z)
case_obj.scale    = (1, 1, 1)

# Flipcase: starts invisible (scale 0 → 1 morph)
flip_obj.location = (0, 0, 0)
flip_obj.scale    = (0.001, 0.001, 0.001)

# The flipcase cover hinge: the cover is on one long side.
# From the SCAD the flip cover is appended in +X direction then rotated 180°.
# We'll animate a child Empty as a hinge pivot.
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
hinge = bpy.context.object
hinge.name = "HingePivot"
# Parent the flipcase to the hinge but keep transform
flip_obj.parent = hinge
flip_obj.matrix_parent_inverse = hinge.matrix_world.inverted()

# ── ANIMATION ────────────────────────────────────────────────────────────────

# ── PHASE 1: Phone spin  (frames 1 → 60) ─────────────────────────────────────
# Phone spins 360° on Z, floats in place

set_frame(1)
phone.location    = (0, 0, PHONE_START_Z)
phone.rotation_euler = (0, 0, 0)
phone.keyframe_insert("location")
phone.keyframe_insert("rotation_euler")

set_frame(60)
phone.rotation_euler = (0, 0, math.radians(360))
phone.keyframe_insert("rotation_euler")
# Keep same height
phone.location = (0, 0, PHONE_START_Z)
phone.keyframe_insert("location")

# Case stays put during spin
set_frame(1)
case_obj.location = (0, 0, CASE_START_Z)
case_obj.keyframe_insert("location")
set_frame(60)
case_obj.location = (0, 0, CASE_START_Z)
case_obj.keyframe_insert("location")

# ── PHASE 2: Phone drops into case  (frames 60 → 120) ────────────────────────
# Phone rotation settles to 0, case rises, phone drops to rest inside

set_frame(60)
phone.rotation_euler = (0, 0, math.radians(360))
phone.keyframe_insert("rotation_euler")
case_obj.location = (0, 0, CASE_START_Z)
case_obj.keyframe_insert("location")

set_frame(120)
phone.location = (0, 0, PHONE_REST_Z)
phone.rotation_euler = (0, 0, math.radians(360))
phone.keyframe_insert("location")
phone.keyframe_insert("rotation_euler")

case_obj.location = (0, 0, CASE_REST_Z)
case_obj.keyframe_insert("location")

# ── PHASE 3: Case morphs into FlipCase  (frames 120 → 180) ───────────────────
# Case shrinks / fades out while flipcase grows / fades in
# We fake morphing with a scale + alpha cross-dissolve

# Case: full → invisible (scale 1 → 0.001)
set_frame(120)
case_obj.scale = (1, 1, 1)
case_obj.keyframe_insert("scale")
set_alpha(case_obj, 1.0, 120)

set_frame(180)
case_obj.scale = (0.001, 0.001, 0.001)
case_obj.keyframe_insert("scale")
set_alpha(case_obj, 0.0, 180)

# Phone also fades slightly (it's now inside the flipcase body)
set_alpha(phone, 1.0, 120)
set_alpha(phone, 0.0, 165)

# FlipCase: tiny → full (scale 0.001 → 1)
set_frame(120)
flip_obj.scale = (0.001, 0.001, 0.001)
flip_obj.keyframe_insert("scale")
set_alpha(flip_obj, 0.0, 120)

set_frame(180)
flip_obj.scale = (1, 1, 1)
flip_obj.keyframe_insert("scale")
set_alpha(flip_obj, 1.0, 180)

# ── PHASE 4: Flipcase claps shut  (frames 180 → 240) ─────────────────────────
# The flip cover rotates ~180° around the hinge (X axis).
# The hinge pivot is positioned at the spine of the case.
# From SCAD: phone w=74.5, thickness=1.5 → spine at x ≈ w/2+thickness = 38.75 mm
# We move the hinge empty to the spine edge.
SPINE_X = (74.5 / 2) + THICKNESS   # ≈ 38.75

hinge.location = (SPINE_X, 0, 0)

set_frame(180)
hinge.rotation_euler = (0, 0, 0)
hinge.keyframe_insert("rotation_euler")

set_frame(240)
# Cover swings 175° (leaving 5° gap so it's clearly shut, not past)
hinge.rotation_euler = (math.radians(-175), 0, 0)
hinge.keyframe_insert("rotation_euler")

# ── EASING ───────────────────────────────────────────────────────────────────

for obj in (phone, case_obj, flip_obj, hinge):
    if obj.animation_data and obj.animation_data.action:
        ease_in_out(obj.animation_data.action.fcurves)

# ── RENDER SETTINGS (optional quick setup) ───────────────────────────────────

scene.render.engine = 'BLENDER_EEVEE_NEXT'  # faster, works on apt Blender
scene.eevee.taa_render_samples = 64  # EEVEE render quality
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = "//flipcase_animation.mp4"

# ── VIEWPORT SHADING ─────────────────────────────────────────────────────────

# (viewport shading skipped - not available in background/headless mode)

# SAVE SCENE + RENDER
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
blend_path = os.path.join(script_dir, "flipcase_scene.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print("Scene saved to: " + blend_path)

scene.render.filepath = os.path.join(script_dir, "flipcase_animation.mp4")
print("Rendering to:   " + scene.render.filepath)
print("Rendering all frames, this may take a while...")
bpy.ops.render.render(animation=True)

print("=" * 60)
print("FlipCase animation script complete!")
print(f"  Frames: 1 – {TOTAL_FRAMES}  ({TOTAL_FRAMES/FPS:.1f} s @ {FPS} fps)")
print("  Phase 1  1–60   : Phone spin")
print("  Phase 2  60–120 : Phone drops into case")
print("  Phase 3  120–180: Case morphs into flipcase")
print("  Phase 4  180–240: Flipcase claps shut")
print()
print("Tip: render with Render > Render Animation (Ctrl+F12)")
print("Output file: flipcase_animation.mp4 (next to your .blend)")
print("=" * 60)
