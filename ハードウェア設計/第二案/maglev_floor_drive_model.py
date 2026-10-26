"""浮上式リニアモーターカー コースモデル v0.3（床下駆動版：浮いてるミニ四駆）

単位 mm。角度は +X 軸から反時計回り（FWD = 反時計回り）。床面（カバー上面）を z = 0 とする。
- 床下：コイル60個を寝かせて並べ（軸が上下）、その左右に浮上用磁石（N上向き）を2列
- 床面：1mm のミラーアクリル（または黒アクリル）でコイルと磁石を隠す
- 台車：底面に駆動磁石（5極、下向き）と浮上磁石（N下向き）。高さ 40mm 台のミニ四駆風ボディ
- 壁：内外とも透明フェンス。外壁の根元の裏にホールセンサー列、台車の外側スカートにセンサー用小磁石
- 演出：空のホイールハウス（中が光る）、アンダーグロー、外壁沿いの LED 帯（台車の通過に合わせて点灯）
"""
import math
import cadquery as cq
from maglev_course_model import ring_sector, placed_box, at_angle, to_track

# ---------- コイル（床下） ----------
CIRC = 3000.0
R_C = CIRC / (2 * math.pi)           # コイル中心半径 ≈ 477.46（= 走行路の中心）
N_COIL, COIL_PITCH, TAU, N_SEC = 60, 6.0, 4.5, 10
COIL_OD, COIL_ID, COIL_T = 48.0, 20.0, 8.0   # 50mm 間隔に並べるため外径 48（隣と 2mm 空ける）
COVER_T = 1.0                         # 床カバー（ミラーアクリル）
COIL_Z1 = -COVER_T                    # コイル上面
COIL_Z0 = COIL_Z1 - COIL_T
BASE_Z0 = COIL_Z0 - 8.0               # 土台の下面

# ---------- 浮上磁石 ----------
LEV_OFF = 45.0                        # コイル中心からの半径方向オフセット
LEV_ROWS = (R_C - LEV_OFF, R_C + LEV_OFF)
LEV_W, LEV_H = 10.0, 5.0
FLY = 6.0                             # 見える浮上高さ（床面〜台車底面）

# ---------- 壁（透明フェンス） ----------
HALF_W = 62.0
R_IN_FACE = R_C - HALF_W              # 内壁の走行面
R_OUT_FACE = R_C + HALF_W             # 外壁の走行面
WALL_T = 2.0
WALL_H_IN, WALL_H_OUT = 50.0, 55.0
R_BASE_IN, R_BASE_OUT = R_IN_FACE - 25.0, R_OUT_FACE + 30.0

# ---------- ホールセンサー（内側フェンスの根元の裏。外から見たときに隙間を隠さない） ----------
HALL_Z = 15.0
HALL_W, HALL_D, HALL_H = 4.0, 3.0, 4.5
N_GROUP, GROUP_PITCH, HALL_IN_GROUP = 20, 18.0, 3.0
R_HALL_OUT = R_IN_FACE - WALL_T          # センサー前面（台車側）

# ---------- 台車 ----------
CART_POLES = "SNSNS"
POLE_SPAN = TAU * len(CART_POLES)     # 22.5°
CART_CENTER = 90.0
CH_Z0 = FLY                           # シャーシ下面
CH_T = 5.0                            # シャーシ厚（浮上磁石を埋め込む）
DRV = (30.0, 40.0, 10.0)              # 駆動磁石 1極：周方向×半径方向×厚さ（30×20×10 を2個並べ）
SENS_MAG = (10.0, 5.0, 10.0)
ROLLER_R, ROLLER_H = 6.5, 6.0
ROLLER_Z = (9.0, 33.0)                # 下段・上段
SKIRT_GAP = 3.0                       # 外側スカート〜外壁のすき間


def coil_flat(ang):
    c = (cq.Workplane("XY").workplane(offset=COIL_Z0).circle(COIL_OD / 2).circle(COIL_ID / 2)
         .extrude(COIL_T).translate((R_C, 0, 0)))
    return at_angle(c, ang)


def cyl_z(r, z0, z1, rc, ang):
    return at_angle(cq.Workplane("XY").workplane(offset=z0).circle(r).extrude(z1 - z0)
                    .translate((rc, 0, 0)), ang)


def body_parts():
    """ミニ四駆風ボディ（ローカル座標：x=進行方向、y=外向き、z=上）"""
    L, W = 172.0, 92.0
    y0, y1 = -W / 2, W / 2
    zb = CH_Z0 + CH_T
    prof = [(-L/2, zb), (L/2, zb), (L/2, zb + 5), (L/2 - 40, zb + 17),
            (L/2 - 78, zb + 22), (-L/2 + 30, zb + 24), (-L/2 + 6, zb + 23), (-L/2, zb + 13)]
    shell = cq.Workplane("XZ").polyline(prof).close().extrude(-W).translate((0, y0, 0))
    for sel, r in (("|Z", 16.0), ("|Y", 3.0)):
        try:
            shell = shell.edges(sel).fillet(r)
        except Exception:
            pass
    # 空のホイールハウス（タイヤ位置をくり抜く）
    wells, glows = [], []
    for x in (L/2 - 34, -L/2 + 34):
        for y in (y0, y1):
            cut = (cq.Workplane("XZ").center(x, zb).circle(15).extrude(13, both=True)
                   .translate((0, y, 0)))
            shell = shell.cut(cut)
            g = (cq.Workplane("XZ").center(x, zb + 1).circle(9).extrude(1.0, both=True)
                 .translate((0, y - (6 if y > 0 else -6), 0)))
            glows.append(g)
    canopy = (cq.Workplane("XY").workplane(offset=zb + 18).center(-8, 0)
              .ellipse(30, 16).extrude(11))
    try:
        canopy = canopy.faces(">Z").edges().fillet(5.0)
    except Exception:
        pass
    wing = cq.Workplane("XY").box(20, W + 4, 2.5).translate((-L/2 + 8, 0, zb + 34))
    posts = (cq.Workplane("XY").pushPoints([(-L/2 + 10, -26), (-L/2 + 10, 26)])
             .rect(4, 3).extrude(12).translate((0, 0, zb + 22)))
    stripe = (cq.Workplane("XY").box(L - 40, 10, 1.0).translate((4, 0, zb + 22.6)))
    return shell, canopy, wing.union(posts), stripe, glows


def build_fixed(asm, a0=0.0, a1=360.0, lit_center=None, see_through=False):
    full = (a1 - a0) >= 359.9
    clear = cq.Color(0.70, 0.86, 0.96, 0.22)
    # 土台（コイルと磁石を載せる）
    asm.add(ring_sector(R_BASE_IN, R_BASE_OUT, BASE_Z0, COIL_Z0, a0, a1), name="base",
            color=cq.Color(0.10, 0.10, 0.12))
    # 床下のコイル
    phase_col = {"U": cq.Color(0.90, 0.49, 0.13), "V": cq.Color(0.95, 0.77, 0.06),
                 "W": cq.Color(0.09, 0.63, 0.52)}
    for k in range(N_COIL):
        ang = k * COIL_PITCH + COIL_PITCH / 2
        if not full and not (a0 - 4 <= ang <= a1 + 4):
            continue
        ph = "UVW"[k % 3]
        asm.add(coil_flat(ang), name=f"coil_{k:02d}_{ph}", color=phase_col[ph])
    # 浮上磁石（床、N上向き）
    for i, rr in enumerate(LEV_ROWS):
        asm.add(ring_sector(rr - LEV_W / 2, rr + LEV_W / 2, COIL_Z1 - LEV_H, COIL_Z1, a0, a1),
                name=f"lev_floor_row{i}", color=cq.Color(0.80, 0.15, 0.15))
    # 床カバー（ミラーアクリル想定。表示は濃いグレーの光沢）
    asm.add(ring_sector(R_IN_FACE, R_OUT_FACE, -COVER_T, 0, a0, a1), name="floor_cover_mirror",
            color=cq.Color(0.55, 0.58, 0.62, 0.30) if see_through else cq.Color(0.16, 0.17, 0.19))
    # 内外の透明フェンス
    asm.add(ring_sector(R_IN_FACE - WALL_T, R_IN_FACE, COIL_Z0, WALL_H_IN, a0, a1),
            name="inner_clear_fence", color=clear)
    asm.add(ring_sector(R_OUT_FACE, R_OUT_FACE + WALL_T, COIL_Z0, WALL_H_OUT, a0, a1),
            name="outer_clear_fence", color=clear)
    # 外壁を支える透明リブ（18° ごと）
    for g in range(N_GROUP):
        ang = g * GROUP_PITCH + 12.0
        if not full and not (a0 <= ang <= a1):
            continue
        asm.add(placed_box(5.0, 10.0, WALL_H_OUT - COIL_Z0, R_OUT_FACE + WALL_T + 10.0,
                           (WALL_H_OUT + COIL_Z0) / 2, ang), name=f"fence_rib_{g:02d}", color=clear)
    # ホールセンサー列（内側フェンスの根元の裏）と基板
    asm.add(ring_sector(R_HALL_OUT - HALL_D - 1.6, R_HALL_OUT - HALL_D, HALL_Z - 7, HALL_Z + 7, a0, a1),
            name="hall_pcb_strip", color=cq.Color(0.20, 0.42, 0.25))
    for g in range(N_GROUP):
        for i, lab in enumerate("ABC"):
            ang = g * GROUP_PITCH + 1.5 + i * HALL_IN_GROUP
            if not full and not (a0 <= ang <= a1):
                continue
            asm.add(placed_box(HALL_W, HALL_D, HALL_H, R_HALL_OUT - HALL_D / 2, HALL_Z, ang),
                    name=f"hall_g{g:02d}_{lab}", color=cq.Color(0.05, 0.05, 0.05))
    # LED 帯（外壁の上端の裏）。台車の付近だけ点灯して表示
    step = 2.0
    a = a0
    while a < a1 - 1e-6:
        b = min(a + step, a1)
        mid = (a + b) / 2
        lit = lit_center is not None and abs(((mid - lit_center + 180) % 360) - 180) < 16
        col = cq.Color(0.20, 0.95, 1.00) if lit else cq.Color(0.25, 0.28, 0.32)
        asm.add(ring_sector(R_OUT_FACE + WALL_T, R_OUT_FACE + WALL_T + 3, WALL_H_OUT - 6, WALL_H_OUT - 2,
                            a + 0.1, b - 0.1, 0.5), name=f"led_{a:.0f}", color=col)
        a = b


def add_cart(asm):
    c0 = CART_CENTER - POLE_SPAN / 2
    span_ch = POLE_SPAN + 2.0
    r_in_roll = R_IN_FACE + ROLLER_R + 0.3
    r_out_roll = R_OUT_FACE - ROLLER_R - 0.3
    dark, white = cq.Color(0.16, 0.17, 0.20), cq.Color(0.97, 0.97, 0.98)
    red, blue = cq.Color(0.85, 0.12, 0.12), cq.Color(0.15, 0.25, 0.70)
    glow = cq.Color(0.20, 0.95, 1.00)

    # シャーシ（円弧板。浮上磁石と駆動磁石を埋め込む）
    asm.add(ring_sector(r_in_roll + 4, r_out_roll - 4, CH_Z0, CH_Z0 + CH_T,
                        CART_CENTER - span_ch / 2, CART_CENTER + span_ch / 2, 0.5),
            name="cart_chassis", color=dark)
    # 浮上磁石（N下向き）2列×4
    for rr in LEV_ROWS:
        for j in range(4):
            ang = CART_CENTER + (j - 1.5) * (POLE_SPAN / 4)
            asm.add(placed_box(20.0, LEV_W, LEV_H, rr, CH_Z0 + LEV_H / 2, ang),
                    name=f"lev_cart_{rr:.0f}_{j}", color=red)
    # 駆動磁石（下向き、S N S N S）
    pole = {"N": red, "S": blue}
    for i, p in enumerate(CART_POLES):
        ang = c0 + TAU * (i + 0.5)
        asm.add(placed_box(DRV[0], DRV[1], DRV[2], R_C, CH_Z0 + DRV[2] / 2, ang),
                name=f"magnet_drive_{i}_{p}", color=pole[p])
    # 内側スカートとセンサー用小磁石（内向き、内側フェンス裏のホール列に向ける）
    skirt_in = R_IN_FACE + SKIRT_GAP
    asm.add(ring_sector(skirt_in + SENS_MAG[1], skirt_in + SENS_MAG[1] + 3, CH_Z0, HALL_Z + 7,
                        c0 - 0.3, c0 + POLE_SPAN + 0.3, 0.5), name="cart_skirt", color=dark)
    for i, p in enumerate(CART_POLES):
        ang = c0 + TAU * (i + 0.5)
        asm.add(placed_box(SENS_MAG[0], SENS_MAG[1], SENS_MAG[2], skirt_in + SENS_MAG[1] / 2, HALL_Z, ang),
                name=f"magnet_sensor_{i}_{p}", color=pole[p])
    # アンダーグロー（シャーシ下面の縁）
    for rr in (r_in_roll + 6, r_out_roll - 6):
        asm.add(ring_sector(rr - 1.5, rr + 1.5, CH_Z0 - 0.8, CH_Z0, CART_CENTER - span_ch / 2 + 1,
                            CART_CENTER + span_ch / 2 - 1, 0.5), name=f"underglow_{rr:.0f}", color=glow)
    # 床に落ちる光（表示用）
    asm.add(ring_sector(R_C - 52, R_C + 52, 0.0, 0.3, CART_CENTER - span_ch / 2 - 2,
                        CART_CENTER + span_ch / 2 + 2, 0.5), name="floor_glow_vis",
            color=cq.Color(0.20, 0.95, 1.00, 0.25))
    # ボディ
    shell, canopy, wing, stripe, glows = body_parts()
    asm.add(to_track(shell, R_C, CART_CENTER), name="body_shell", color=cq.Color(0.10, 0.36, 0.86))
    asm.add(to_track(canopy, R_C, CART_CENTER), name="body_canopy", color=cq.Color(0.06, 0.08, 0.12))
    asm.add(to_track(wing, R_C, CART_CENTER), name="body_wing", color=white)
    asm.add(to_track(stripe, R_C, CART_CENTER), name="body_stripe", color=white)
    for i, g in enumerate(glows):
        asm.add(to_track(g, R_C, CART_CENTER), name=f"wheelwell_glow_{i}", color=glow)
    # 前後バンパー（FRP プレート）と 2段ローラー
    for tag, ang in (("F", CART_CENTER + span_ch / 2 + 1.6), ("R", CART_CENTER - span_ch / 2 - 1.6)):
        asm.add(ring_sector(r_in_roll, r_out_roll, CH_Z0 + 1, CH_Z0 + 3, ang - 1.4, ang + 1.4, 0.3),
                name=f"frp_plate_{tag}", color=cq.Color(0.22, 0.22, 0.24))
        for side, rc in (("out", r_out_roll), ("in", r_in_roll)):
            asm.add(cyl_z(1.6, CH_Z0 + 1, ROLLER_Z[1] + ROLLER_H + 2, rc, ang),
                    name=f"roller_shaft_{tag}_{side}", color=cq.Color(0.78, 0.78, 0.80))
            for lv, zr in zip(("low", "up"), ROLLER_Z):
                asm.add(cyl_z(ROLLER_R, zr, zr + ROLLER_H, rc, ang),
                        name=f"roller_{tag}_{side}_{lv}", color=cq.Color(0.78, 0.80, 0.84))


def build(see_through=False):
    asm = cq.Assembly(name="maglev_floor_drive")
    build_fixed(asm, lit_center=CART_CENTER, see_through=see_through)
    add_cart(asm)
    return asm


def build_showcase(half=30.0):
    asm = cq.Assembly(name="showcase")
    build_fixed(asm, CART_CENTER - half, CART_CENTER + half, lit_center=CART_CENTER)
    add_cart(asm)
    return asm


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "maglev_floor_drive.step"
    build().save(out)
    print("saved", out)
    print(f"R_C={R_C:.2f} track {R_IN_FACE:.1f}-{R_OUT_FACE:.1f} (width {2*HALF_W:.0f})")
    print(f"drive magnet bottom z={CH_Z0}, coil top z={COIL_Z1} -> gap {CH_Z0 - COIL_Z1:.1f}")
