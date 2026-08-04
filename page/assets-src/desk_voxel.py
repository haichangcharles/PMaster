import bpy, math, sys
from mathutils import Vector

PREVIEW = '--preview' in sys.argv
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.use_denoising=False
sc.cycles.samples=48 if PREVIEW else 300
sc.render.film_transparent=True
sc.render.resolution_x=800 if PREVIEW else 1700
sc.render.resolution_y=600 if PREVIEW else 1280

def hexc(h):
    h=h.lstrip('#')
    return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)
def srgb(c):  # gamma to linear approx
    return tuple((v/1.0)**2.2 if i<3 else v for i,v in enumerate(c))

PAL={
 'desk':   srgb(hexc('#E2E4E9')),
 'white':  srgb(hexc('#FAFAFC')),
 'panel':  srgb(hexc('#EDEEF2')),
 'chip':   srgb(hexc('#D8DAE1')),
 'graph':  srgb(hexc('#3A3D45')),
 'blue':   srgb(hexc('#2F7CF6')),
 'bluel':  srgb(hexc('#7FB0F9')),
 'coffee': srgb(hexc('#7A4A22')),
 'cream':  srgb(hexc('#F4EFE6')),
}
def mat(name,c,rough=0.75):
    m=bpy.data.materials.new(name);m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=c
    b.inputs['Roughness'].default_value=rough
    return m
M={k:mat(k,v) for k,v in PAL.items()}

U=0.13  # voxel unit

def vox(x,y,z,sx,sy,sz,mk,bev=0.012,rz=0.0,name='v'):
    """place a box spanning sx,sy,sz units with MIN corner at (x,y,z) units (desk-top space)"""
    bpy.ops.mesh.primitive_cube_add(size=2)
    o=bpy.context.object;o.name=name
    o.scale=(sx*U/2,sy*U/2,sz*U/2)
    bpy.ops.object.transform_apply(scale=True)
    bv=o.modifiers.new('b','BEVEL');bv.width=min(bev,min(sx,sy,sz)*U/2*.8);bv.segments=2
    o.data.materials.append(M[mk])
    o.rotation_euler=(0,0,rz)
    o.location=((x+sx/2)*U,(y+sy/2)*U,(z+sz/2)*U)
    return o

# ---------------- desk slab ----------------
DW,DD,DH=46,32,2
vox(-DW/2,-DD/2,0,DW,DD,DH,'desk',bev=0.05,name='desk')
T=DH  # desktop z in units

# ---------------- laptop ----------------
# base
LX,LY=-9,2   # min corner units
BW,BD=20,13
vox(LX,LY,T,BW,BD,1,'panel',name='lap_base')
# keyboard keys (graphite grid)
for r in range(4):
    for c in range(14):
        vox(LX+2+c*1.2,LY+5.6+r*1.5,T+1,1,1,0.5,'graph',bev=0.008,name=f'key{r}{c}')
# trackpad
vox(LX+7.5,LY+1.2,T+1,5,3.2,0.3,'chip',name='trackpad')
# screen: vertical slab at back of base
SH=14
vox(LX,LY+BD,T,BW,1,SH+2,'white',name='screen')
# bezel inner
vox(LX+0.8,LY+BD-0.15,T+1.2,BW-1.6,0.3,SH-0.8,'panel',name='display_bg')
# kanban chips on display (protruding voxels)
cols=[(LX+1.8,4.6),(LX+8.0,4.6),(LX+14.2,4.6)]  # (x,width)
hdr_z=T+SH-1.2
for i,(cx,cw) in enumerate(cols):
    vox(cx,LY+BD-0.45,hdr_z,cw*0.6,0.35,0.9,'chip',name=f'hdr{i}')
counts=[3,2,2]
for i,(cx,cw) in enumerate(cols):
    for r in range(counts[i]):
        mk='blue' if (i==1 and r==0) else 'chip'
        vox(cx,LY+BD-0.5,hdr_z-2.2-r*2.4,cw,0.4,1.7,mk,name=f'card{i}{r}')
        if mk=='blue':
            vox(cx+0.7,LY+BD-0.55,hdr_z-2.2-r*2.4+0.9,cw*0.55,0.4,0.35,'white',name='cline1')
            vox(cx+0.7,LY+BD-0.55,hdr_z-2.2-r*2.4+0.35,cw*0.35,0.4,0.3,'bluel',name='cline2')

# ---------------- phone ----------------
ph=vox(-17,-8,T,5,9,0.8,'graph',rz=math.radians(14),name='phone')
vox(-16.4,-7.4,T+0.8,3.9,7.8,0.15,'panel',rz=math.radians(14),name='phone_scr')
# fix: rotate around own center — vox rotates around center already; offsets approximate

# ---------------- notepad ----------------
NX,NY=8,-9
vox(NX,NY,T,8,10,1,'cream',rz=math.radians(-7),name='pad')
for i in range(4):
    vox(NX+1.4,NY+2+i*2,T+1,5,0.6,0.2,'chip',rz=math.radians(-7),name=f'pline{i}')

# ---------------- pen ----------------
vox(2,-12,T,7,0.9,0.9,'graph',rz=math.radians(18),name='pen')
vox(8.6,-11.2,T,1.2,0.9,0.9,'chip',rz=math.radians(18),name='pen_tip')

# ---------------- coffee (chunky voxel cup) ----------------
CX,CY=-5,-9
vox(CX,CY,T,4,4,3.4,'white',name='cup')
vox(CX+0.7,CY+0.7,T+3.25,2.6,2.6,0.3,'coffee',name='coffee')
vox(CX+4,CY+1.2,T+1.2,1.4,1.6,1.6,'white',name='handle')
vox(CX+4.7,CY+1.6,T+1.55,0.7,0.8,0.9,'desk',name='handle_hole')  # illusion of hole
vox(CX-0.8,CY-0.8,T,5.6,5.6,0.35,'panel',name='saucer')

# ---------------- sticky notes ----------------
vox(-13,-13,T,3.6,3.6,0.4,'blue',rz=math.radians(10),name='sticky1')
vox(-9.5,-14,T,3.6,3.6,0.3,'chip',rz=math.radians(-6),name='sticky2')

# ---------------- shadow catcher ----------------
bpy.ops.mesh.primitive_plane_add(size=60,location=(0,0,0))
g=bpy.context.object;g.name='ground';g.is_shadow_catcher=True

# ---------------- lights ----------------
bpy.ops.object.light_add(type='SUN',location=(6,-7,12))
sun=bpy.context.object
sun.data.energy=5.0; sun.data.angle=math.radians(6)
d=Vector((0,0,0))-sun.location
sun.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA',location=(-7,-4,8))
fl=bpy.context.object;fl.data.energy=420;fl.data.size=8
d=Vector((0,0,0.5))-fl.location
fl.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True
w.node_tree.nodes['Background'].inputs['Strength'].default_value=0.65
w.node_tree.nodes['Background'].inputs['Color'].default_value=(1,1,1,1)

# ---------------- camera: classic isometric ----------------
az=math.radians(45)
dist=16
cam_loc=Vector((math.cos(az)*dist, -math.sin(az)*dist, dist*0.82))
bpy.ops.object.camera_add(location=cam_loc)
cam=bpy.context.object
cam.data.type='ORTHO';cam.data.ortho_scale=8.8
d=Vector((0.35,-0.15,0.75))-cam.location
cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
sc.camera=cam

bpy.ops.render.render(write_still=True)
bpy.data.images['Render Result'].save_render('/home/claude/desk_voxel.png')
if PREVIEW:
    bpy.ops.object.camera_add(location=(0,0,18))
    top=bpy.context.object;top.data.type='ORTHO';top.data.ortho_scale=8.5
    top.rotation_euler=(0,0,0);sc.camera=top
    bpy.ops.render.render(write_still=True)
    bpy.data.images['Render Result'].save_render('/home/claude/desk_voxel_top.png')
print('RENDER DONE')
