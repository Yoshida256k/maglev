import linear_course_model as course, cadquery as cq
asm = course.build()
parts = {}
for name, obj in [(c.name, c.obj) for c in asm.children]:
    parts[name] = obj.val() if hasattr(obj, "val") else obj
cart = {k:v for k,v in parts.items() if k.startswith(("cart","magnet","wheel","guide_roller","roller_post"))}
fixed = {k:v for k,v in parts.items() if k not in cart}
# only fixed parts near cart (angle 75..105)
import math
def near(s):
    c = s.Center(); a = math.degrees(math.atan2(c.y, c.x)) % 360
    return 60 < a < 120 or s.BoundingBox().xlen > 500
hits = []
for cn, cs in cart.items():
    for fn, fs in fixed.items():
        if not near(fs): continue
        if not cs.BoundingBox().enlarge(0.01).intersects(fs.BoundingBox()) if hasattr(cs.BoundingBox(),'intersects') else False: pass
        v = cs.intersect(fs).Volume()
        if v > 1e-3: hits.append((cn, fn, round(v,2)))
for cn, cs in cart.items():
    for cn2, cs2 in cart.items():
        if cn < cn2:
            v = cs.intersect(cs2).Volume()
            if v > 1e-3: hits.append(("CART:"+cn, cn2, round(v,2)))
print("interferences:", hits if hits else "none")
# min distance magnet face to coil face and to sensors
mag = parts["magnet_main_2_S"]; 
print("dist main magnet -> nearest coil:", min(mag.distance(parts[n]) for n in parts if n.startswith("coil_") and near(parts[n])) if hasattr(mag,'distance') else 'n/a')
