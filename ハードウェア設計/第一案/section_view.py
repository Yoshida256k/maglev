import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.font_manager as fm
import maglev_course_model as c
fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
plt.rcParams["font.family"]="Noto Sans CJK JP"
fig,ax=plt.subplots(figsize=(12,7.2))
def box(r0,r1,z0,z1,col,lab=None,alpha=1,fs=8,tc="k"):
    ax.add_patch(Rectangle((r0,z0),r1-r0,z1-z0,fc=col,ec="k",lw=0.7,alpha=alpha))
    if lab: ax.text((r0+r1)/2,(z0+z1)/2,lab,ha="center",va="center",fontsize=fs,color=tc)
rm=(c.R_INWALL_OUT+c.R_SHEET_IN)/2
box(c.R_BASE_IN,c.R_FRAME_OUT+10,-c.BASE_T,0,"#333","ベース",tc="w")
for rr in c.LEV_ROWS:
    box(rr-c.LEV_W/2,rr+c.LEV_W/2,0,c.LEV_H,"#c62828")
    box(rr-c.LIFT_MAG[1]/2,rr+c.LIFT_MAG[1]/2,c.CHASSIS_Z0,c.CHASSIS_Z0+c.LIFT_MAG[2],"#c62828")
    ax.text(rr,-4,"N↑",ha="center",fontsize=7,color="w"); 
ax.text(c.LEV_ROWS[0]-9,2.5,"床の浮上磁石\n（N上向き）",ha="right",va="center",fontsize=8,color="#c62828")
ax.text(c.LEV_ROWS[0]-9,c.CHASSIS_Z0+2.5,"台車の浮上磁石（N下向き）",ha="right",va="center",fontsize=8,color="#c62828")
ax.annotate("",(c.LEV_ROWS[1]+12,c.LEV_H),(c.LEV_ROWS[1]+12,c.CHASSIS_Z0),arrowprops=dict(arrowstyle="<->",lw=0.8))
ax.text(c.LEV_ROWS[1]+14,(c.LEV_H+c.CHASSIS_Z0)/2,"浮上 6",fontsize=8,va="center")
box(c.R_INWALL_OUT-c.INWALL_T,c.R_INWALL_OUT,0,c.INWALL_H,"#9fd3f0",alpha=0.6)
ax.text(c.R_INWALL_OUT-4,c.INWALL_H+3,"内側 透明板",ha="right",fontsize=8)
box(c.R_SHEET_IN,c.R_SHEET_OUT,0,c.SHEET_H,"#9fd3f0",alpha=0.8)
ax.text(c.R_SHEET_IN-1,c.SHEET_H+3,"外側 透明シート 1mm",ha="right",fontsize=8)
box(c.R_COIL_IN,c.R_COIL_OUT,c.COIL_Z-c.COIL_OD/2,c.COIL_Z+c.COIL_OD/2,"#e67e22")
box(c.R_COIL_IN,c.R_COIL_OUT,c.COIL_Z-c.COIL_ID/2,c.COIL_Z+c.COIL_ID/2,"white")
box(c.R_FRAME_IN,c.R_FRAME_OUT,0,c.FRAME_H,"#9fd3f0",alpha=0.6)
box(c.R_SHEET_OUT,c.R_FRAME_IN,0,10,"#9fd3f0",alpha=0.6); box(c.R_SHEET_OUT,c.R_FRAME_IN,c.FRAME_H-8,c.FRAME_H,"#9fd3f0",alpha=0.6)
ax.text(c.R_FRAME_OUT+3,c.FRAME_H-4,"コイル枠も透明\n（背板：PC板、上下縁：アクリル）",fontsize=8,va="center")
box(c.R_SHEET_OUT+c.HALL_D,c.R_FRAME_IN,c.HALL_Z-10,c.HALL_Z+10,"#7fa77f")
box(c.R_SHEET_OUT,c.R_SHEET_OUT+c.HALL_D,c.HALL_Z-2.25,c.HALL_Z+2.25,"#111")
ax.text(c.R_FRAME_OUT+3,c.COIL_Z,"コイル φ50\n（コイル枠に固定）",fontsize=8,va="center")
ax.text(c.R_FRAME_OUT+3,c.HALL_Z,"ホールセンサー列",fontsize=8,va="center")
zc0=c.CHASSIS_Z0+c.LIFT_MAG[2]
box(c.R_INWALL_OUT+14,c.R_MAG_IN,zc0,zc0+c.CHASSIS_T,"#2e3036")
box(rm-46,rm+30,zc0+c.CHASSIS_T,zc0+c.CHASSIS_T+22,"#1a52cc","ボディ",tc="w")
box(c.R_MAG_IN-5,c.R_MAG_IN,zc0,c.HALL_Z+8,"#33508c",alpha=0.6)
box(c.R_MAG_IN,c.R_MAG_OUT,c.COIL_Z-c.MAG_H/2,c.COIL_Z+c.MAG_H/2,"#2b3fa8","駆動\n磁石",tc="w",fs=7)
sw,st,sh=c.SENS_MAG
box(c.R_MAG_OUT-st,c.R_MAG_OUT,c.HALL_Z-sh/2,c.HALL_Z+sh/2,"#2b3fa8")
for rc in (c.R_SHEET_IN-c.ROLLER_R-0.3, c.R_INWALL_OUT+c.ROLLER_R+0.3):
    for z in c.ROLLER_Z: box(rc-c.ROLLER_R,rc+c.ROLLER_R,z,z+c.ROLLER_H,"#e6c229")
    box(rc-1.6,rc+1.6,zc0,c.ROLLER_Z[1]+c.ROLLER_H+2,"#999")
ax.text(c.R_INWALL_OUT+16,c.ROLLER_Z[1]+3,"2段ローラー\n（φ13）",fontsize=8,va="center")
def dim(x0,x1,y,t):
    ax.annotate("",(x0,y),(x1,y),arrowprops=dict(arrowstyle="<->",lw=0.8)); ax.text((x0+x1)/2,y+1.5,t,ha="center",fontsize=8)
dim(c.R_MAG_OUT,c.R_COIL_IN,c.COIL_Z+c.MAG_H/2+3,"5")
dim(c.R_INWALL_OUT,c.R_SHEET_IN,c.SHEET_H+12,f"走行路の幅 {c.TRACK_W:.0f}")
ax.set_xlim(c.R_BASE_IN-5,c.R_FRAME_OUT+50); ax.set_ylim(-14,128); ax.set_aspect("equal")
ax.set_xlabel("半径 R [mm]（左がコース中心側）"); ax.set_ylabel("高さ z [mm]")
ax.set_title("断面図（台車位置、単位 mm）※ローラーは台車の前後端にあるものを重ねて表示"); ax.grid(alpha=0.2)
plt.tight_layout(); plt.savefig("m_section.png",dpi=150); print("ok")
