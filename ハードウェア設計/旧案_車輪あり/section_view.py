import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.font_manager as fm
import linear_course_model as c
fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
plt.rcParams["font.family"] = "Noto Sans CJK JP"
fig, ax = plt.subplots(figsize=(11, 8.5))
def box(r0, r1, z0, z1, col, lab=None, ec="k", alpha=1, hatch=None):
    ax.add_patch(Rectangle((r0, z0), r1-r0, z1-z0, fc=col, ec=ec, lw=0.8, alpha=alpha, hatch=hatch))
    if lab: ax.text((r0+r1)/2, (z0+z1)/2, lab, ha="center", va="center", fontsize=8)
# 固定側
box(370, c.FLOOR_R_OUT, -c.FLOOR_T, 0, "#e9e2d0", "床")
box(c.R_WALL_IN, c.R_WALL_OUT, 0, c.WALL_H, "#c8ccd6")
ax.text(c.R_WALL_OUT+2, 60, "外壁", fontsize=9, va="center")
box(c.R_COIL_IN, c.R_COIL_OUT, c.COIL_Z-c.COIL_OD/2, c.COIL_Z+c.COIL_OD/2, "#e67e22")
box(c.R_COIL_IN, c.R_COIL_OUT, c.COIL_Z-c.COIL_ID/2, c.COIL_Z+c.COIL_ID/2, "white")
ax.text(c.R_COIL_OUT+14, c.COIL_Z, "コイル\nφ50/φ20 t8", fontsize=8, va="center")
box(c.SENSOR_RAIL_R_IN, c.R_WALL_IN, *c.SENSOR_RAIL_Z, "#7fa77f")
box(c.R_COIL_IN, c.R_COIL_IN+c.HALL_D, c.HALL_Z-c.HALL_H/2, c.HALL_Z+c.HALL_H/2, "#111")
ax.text(c.R_WALL_OUT+2, c.HALL_Z, "ホールセンサー列\n（コイル上端から20mm上）", fontsize=8, va="center")
box(c.RAIL_R_IN, c.R_WALL_IN, *c.RAIL_Z, "#9aa0a8")
ax.text(c.R_WALL_OUT+2, sum(c.RAIL_Z)/2+4, "ガイドレール", fontsize=8, va="center")
# 台車側
cr_in = c.R_MAG_IN-6
box(380, cr_in, 22, 60, "#f4f4f8", "台車本体")
box(cr_in, c.R_MAG_IN, 20, 100, "#3d4249")
box(c.R_MAG_IN, c.R_MAG_OUT, c.COIL_Z-c.MAG_H/2, c.COIL_Z+c.MAG_H/2, "#2b3fa8")
ax.text(c.R_MAG_IN-8, c.COIL_Z, "主磁石\n厚10×高40", fontsize=8, ha="right", va="center", color="#2b3fa8")
sw, st, sh = c.SENS_MAG
box(c.R_COIL_IN-c.GAP-st, c.R_COIL_IN-c.GAP, c.HALL_Z-sh/2, c.HALL_Z+sh/2, "#2b3fa8")
ax.text(c.R_MAG_IN-8, c.HALL_Z, "センサー用\n小磁石", fontsize=8, ha="right", va="center", color="#2b3fa8")
rc = c.RAIL_R_IN - c.ROLLER_R
box(rc-c.ROLLER_R, rc+c.ROLLER_R, *c.RAIL_Z, "#333")
box(rc-3, rc+3, 100, c.RAIL_Z[0], "#888")
ax.text(rc-12, sum(c.RAIL_Z)/2+8, "ガイドローラー", fontsize=8, ha="right")
for r in (395, 440):
    box(r-4, r+4, 0, 20, "#111")
ax.text(417, 5, "車輪", fontsize=8, ha="center")
# 寸法
def dim(x0, x1, y, txt):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((x0+x1)/2, y+2, txt, ha="center", fontsize=8)
dim(c.R_MAG_OUT, c.R_COIL_IN, 18, "隙間 5")
dim(c.R_COIL_IN-c.GAP, c.R_COIL_IN, 104, "5")
ax.annotate("", (c.R_COIL_OUT+8, c.COIL_Z+c.COIL_OD/2), (c.R_COIL_OUT+8, c.HALL_Z), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(c.R_COIL_OUT+9, (c.COIL_Z+c.COIL_OD/2+c.HALL_Z)/2, "20", fontsize=8, va="center")
ax.axvline(c.R_C, ls="--", lw=0.6, color="gray"); ax.text(c.R_C, -22, f"コイル中心 R={c.R_C:.1f}", ha="center", fontsize=8, color="gray")
ax.set_xlim(370, 540); ax.set_ylim(-28, 130); ax.set_aspect("equal")
ax.set_xlabel("半径 R [mm]（左がコース中心側）"); ax.set_ylabel("高さ z [mm]（床面=0）")
ax.set_title("断面図（台車位置、単位 mm）")
ax.grid(alpha=0.2)
plt.tight_layout(); plt.savefig("view_section.png", dpi=150)
print("ok")
