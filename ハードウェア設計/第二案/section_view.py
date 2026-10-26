import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.font_manager as fm
import maglev_floor_drive_model as c
fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
plt.rcParams["font.family"]="Noto Sans CJK JP"
fig,ax=plt.subplots(figsize=(12,6.2))
def box(r0,r1,z0,z1,col,lab=None,alpha=1,fs=8,tc="k"):
    ax.add_patch(Rectangle((r0,z0),r1-r0,z1-z0,fc=col,ec="k",lw=0.6,alpha=alpha))
    if lab: ax.text((r0+r1)/2,(z0+z1)/2,lab,ha="center",va="center",fontsize=fs,color=tc)
R=c.R_C
box(c.R_BASE_IN,c.R_BASE_OUT,c.BASE_Z0,c.COIL_Z0,"#222")
ax.text(c.R_BASE_IN+8,(c.BASE_Z0+c.COIL_Z0)/2,"土台",fontsize=8,color="w",va="center")
box(R-c.COIL_OD/2,R-c.COIL_ID/2,c.COIL_Z0,c.COIL_Z1,"#e67e22"); box(R+c.COIL_ID/2,R+c.COIL_OD/2,c.COIL_Z0,c.COIL_Z1,"#e67e22")
ax.text(R,c.COIL_Z0-4,"コイル（寝かせて床下に並べる）",ha="center",fontsize=8,color="w")
for rr in c.LEV_ROWS:
    box(rr-c.LEV_W/2,rr+c.LEV_W/2,c.COIL_Z1-c.LEV_H,c.COIL_Z1,"#c62828")
ax.text(c.LEV_ROWS[1],c.COIL_Z0-4,"浮上磁石（N↑）",ha="center",fontsize=8,color="#ff8a80")
box(c.R_IN_FACE,c.R_OUT_FACE,-c.COVER_T,0,"#9aa3ad")
ax.text(c.R_OUT_FACE+5,-1,"← 床カバー 1mm\n（ミラー or 黒アクリル）",fontsize=8,va="center")
box(c.R_IN_FACE-c.WALL_T,c.R_IN_FACE,c.COIL_Z0,c.WALL_H_IN,"#9fd3f0",alpha=0.7)
box(c.R_OUT_FACE,c.R_OUT_FACE+c.WALL_T,c.COIL_Z0,c.WALL_H_OUT,"#9fd3f0",alpha=0.7)
ax.text(c.R_IN_FACE-3,c.WALL_H_IN+2,"内側 透明フェンス",ha="right",fontsize=8)
ax.text(c.R_OUT_FACE+3,c.WALL_H_OUT+2,"外側 透明フェンス",fontsize=8)
box(c.R_OUT_FACE+c.WALL_T,c.R_OUT_FACE+c.WALL_T+3,c.WALL_H_OUT-6,c.WALL_H_OUT-2,"#33e0f0")
ax.text(c.R_OUT_FACE+8,c.WALL_H_OUT-4,"LED帯",fontsize=8,va="center")
box(c.R_HALL_OUT-c.HALL_D,c.R_HALL_OUT,c.HALL_Z-2.25,c.HALL_Z+2.25,"#111")
box(c.R_HALL_OUT-c.HALL_D-1.6,c.R_HALL_OUT-c.HALL_D,c.HALL_Z-7,c.HALL_Z+7,"#3c7a46")
ax.text(c.R_HALL_OUT-6,c.HALL_Z+10,"ホール列",ha="right",fontsize=8)
# 台車
r_in_roll=c.R_IN_FACE+c.ROLLER_R+0.3; r_out_roll=c.R_OUT_FACE-c.ROLLER_R-0.3
box(r_in_roll+4,r_out_roll-4,c.CH_Z0,c.CH_Z0+c.CH_T,"#2a2c31")
for rr in c.LEV_ROWS: box(rr-c.LEV_W/2,rr+c.LEV_W/2,c.CH_Z0,c.CH_Z0+c.LEV_H,"#c62828")
box(R-c.DRV[1]/2,R+c.DRV[1]/2,c.CH_Z0,c.CH_Z0+c.DRV[2],"#2b3fa8","駆動磁石（下向き）",tc="w",fs=7)
box(R-46,R+46,c.CH_Z0+c.CH_T,c.CH_Z0+c.CH_T+24,"#1a5ce0",alpha=0.85)
ax.text(R,c.CH_Z0+c.CH_T+17,"ミニ四駆風ボディ",ha="center",fontsize=9,color="w")
sk=c.R_IN_FACE+c.SKIRT_GAP
box(sk,sk+c.SENS_MAG[1],c.HALL_Z-5,c.HALL_Z+5,"#2b3fa8")
for rc in (r_in_roll,r_out_roll):
    for z in c.ROLLER_Z: box(rc-c.ROLLER_R,rc+c.ROLLER_R,z,z+c.ROLLER_H,"#c9ccd2")
    box(rc-1.6,rc+1.6,c.CH_Z0+1,c.ROLLER_Z[1]+c.ROLLER_H+2,"#999")
box(r_in_roll+4,r_out_roll-4,c.CH_Z0-0.8,c.CH_Z0,"#33e0f0")
def vdim(x,z0,z1,t,side=1):
    ax.annotate("",(x,z0),(x,z1),arrowprops=dict(arrowstyle="<->",lw=0.8)); ax.text(x+2*side,(z0+z1)/2,t,fontsize=8,va="center",ha="left" if side>0 else "right")
vdim(R+30,0,c.CH_Z0,"見える浮上 6")
vdim(R-30,c.COIL_Z1,c.CH_Z0,"磁石〜コイル 7",-1)
vdim(c.R_OUT_FACE+40,0,c.ROLLER_Z[1]+c.ROLLER_H+2,"台車の高さ 約40\n（旧版 約92）")
ax.set_xlim(c.R_BASE_IN-40,c.R_BASE_OUT+40); ax.set_ylim(c.BASE_Z0-8,70); ax.set_aspect("equal")
ax.set_xlabel("半径 R [mm]（左がコース中心側）"); ax.set_ylabel("高さ z [mm]（床面=0）")
ax.set_title("床下駆動版 断面図（単位 mm）※ローラーは台車の前後端にあるものを重ねて表示"); ax.grid(alpha=0.2)
plt.tight_layout(); plt.savefig("f_section.png",dpi=150); print("ok")
