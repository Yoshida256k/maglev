import math, maglev_floor_drive_model as c, cadquery as cq
asm = cq.Assembly(); c.build_fixed(asm, 60, 120, lit_center=90); c.add_cart(asm)
parts = {ch.name:(ch.obj.val() if hasattr(ch.obj,"val") else ch.obj) for ch in asm.children}
cartk=[k for k in parts if k.startswith(("cart","lev_cart","magnet","body","roller","frp","underglow","wheelwell"))]
fixk=[k for k in parts if k not in cartk and k!="floor_glow_vis"]
hits=[]
for a in cartk:
    for b in fixk:
        v=parts[a].intersect(parts[b]).Volume()
        if v>0.05: hits.append((a,b,round(v,2)))
print("cart vs fixed:", hits or "none")
fh=[]
fk=list(fixk)
for i,a in enumerate(fk):
    for b in fk[i+1:]:
        if a.startswith("led") and b.startswith("led"): continue
        v=parts[a].intersect(parts[b]).Volume()
        if v>0.05: fh.append((a,b,round(v,1)))
print("fixed vs fixed:", fh[:8] or "none")
d=lambda a,b: round(parts[a].distance(parts[b]),2)
print("roller out low -> outer fence:", d("roller_F_out_low","outer_clear_fence"), " roller in -> inner fence:", d("roller_F_in_low","inner_clear_fence"))
print("drive magnet -> nearest coil:", min(d("magnet_drive_2_S",k) for k in parts if k.startswith("coil_")))
print("chassis -> floor cover (visible gap):", d("cart_chassis","floor_cover_mirror"))
print("sensor magnet -> hall:", min(d("magnet_sensor_2_S",k) for k in parts if k.startswith("hall_g")))
print("cart lev -> floor lev:", d("lev_cart_432_1","lev_floor_row0"))
bb=parts["body_shell"].BoundingBox(); print("body top z=%.1f"%bb.zmax, " roller top z=%.1f"%parts["roller_F_out_up"].BoundingBox().zmax)
