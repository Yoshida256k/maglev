import math, maglev_course_model as c
asm = c.build()
parts = {ch.name:(ch.obj.val() if hasattr(ch.obj,"val") else ch.obj) for ch in asm.children}
cartk = [k for k in parts if k.startswith(("cart","lev_cart","magnet","body","roller"))]
fixk = [k for k in parts if k not in cartk]
def near(s):
    bb=s.BoundingBox()
    if bb.xlen>500: return True
    cc=s.Center(); a=math.degrees(math.atan2(cc.y,cc.x))%360
    return 55<a<125
hits=[]
for a in cartk:
    for b in fixk:
        if not near(parts[b]): continue
        v=parts[a].intersect(parts[b]).Volume()
        if v>0.05: hits.append((a,b,round(v,2)))
print("cart vs fixed:", hits or "none")
# clearances
def d(a,b): return round(parts[a].distance(parts[b]),2)
print("roller F out low -> sheet:", d("roller_F_out_low","outer_clear_sheet"))
print("roller F in low -> inner wall:", d("roller_F_in_low","inner_clear_wall"))
print("drive magnet -> sheet:", d("magnet_drive_2_S","outer_clear_sheet"))
print("body -> inner wall:", d("body_shell","inner_clear_wall"), " body -> sheet:", d("body_shell","outer_clear_sheet"))
print("cart lev mag -> floor mag:", d("lev_cart_392_1","lev_floor_row0"))
print("chassis -> inner wall:", d("cart_chassis","inner_clear_wall"))
