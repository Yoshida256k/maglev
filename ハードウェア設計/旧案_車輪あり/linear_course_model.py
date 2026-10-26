"""卓上リニアモーターカー コース全体モデル（v0.1 概念モデル）

単位：mm。角度は +X 軸から反時計回り（台車の FWD 方向 = 反時計回り）。
仕様書 v0.2 の寸法に、2.4節の「台車5極・個別読み出し」案を反映。
未決定の寸法（壁高さ、ガイド形状、台車本体など）は仮置き。
"""
import math
import cadquery as cq

# ---------------- 基本寸法 ----------------
CIRC = 3000.0
R_C = CIRC / (2 * math.pi)          # コイル中心（コイル厚さ方向の中央）の半径 ≈ 477.46
N_COIL = 60
COIL_PITCH = 360.0 / N_COIL         # 6°
TAU = COIL_PITCH * 3 / 4            # 4.5°
N_SEC = 10

COIL_OD, COIL_ID, COIL_T = 50.0, 20.0, 8.0
COIL_Z = 45.0                       # コイル中心の高さ（床面 z=0）
R_COIL_IN = R_C - COIL_T / 2        # コイル内面（台車側）≈ 473.46
R_COIL_OUT = R_C + COIL_T / 2

GAP = 5.0                           # 磁石〜コイル面の隙間
MAG_T = 10.0                        # 主磁石の厚さ（半径方向）
MAG_H = 40.0                        # 主磁石の高さ
MAG_W = 32.0                        # 主磁石の幅（周方向）
R_MAG_OUT = R_COIL_IN - GAP
R_MAG_IN = R_MAG_OUT - MAG_T

WALL_T, WALL_H = 12.0, 120.0
R_WALL_IN = R_COIL_OUT
R_WALL_OUT = R_WALL_IN + WALL_T

FLOOR_R_IN, FLOOR_R_OUT, FLOOR_T = 300.0, R_WALL_OUT + 10.0, 10.0

# ホールセンサー列（コイル列の上にずらす）
HALL_Z = 90.0
HALL_W, HALL_D, HALL_H = 4.0, 3.0, 4.5      # TO-92 相当
SENSOR_RAIL_R_IN = R_COIL_IN + HALL_D       # センサー台の内面
SENSOR_RAIL_Z = (78.0, 102.0)
SENS_MAG = (10.0, 5.0, 10.0)                # センサー用小磁石 W×T×H
N_GROUP = 20
GROUP_PITCH = 360.0 / N_GROUP               # 18°
HALL_IN_GROUP = 2 * TAU / 3                 # 3°

# ガイドレール（壁上端から内側に張り出す）
RAIL_R_IN = R_COIL_IN - GAP                 # ローラーが当たる面（= 磁石外面と同じ半径）
RAIL_Z = (112.0, 120.0)
ROLLER_R = 8.0

# 台車
CART_POLES = "SNSNS"
CART_SPAN = TAU * len(CART_POLES)           # 22.5°
CART_CENTER = 90.0                          # 台車の中心角（図の見やすい位置）


# ---------------- 形状ヘルパー ----------------
def ring_sector(r_in, r_out, z0, z1, a0, a1):
    """半径 r_in〜r_out、高さ z0〜z1、角度 a0〜a1[deg] の円弧ブロック"""
    span = a1 - a0
    if span >= 359.999:
        return (cq.Workplane("XY").workplane(offset=z0)
                .circle(r_out).circle(r_in).extrude(z1 - z0))
    pts = []
    n = max(8, int(span / 1.0))
    for i in range(n + 1):
        a = math.radians(a0 + span * i / n)
        pts.append((r_out * math.cos(a), r_out * math.sin(a)))
    for i in range(n, -1, -1):
        a = math.radians(a0 + span * i / n)
        pts.append((r_in * math.cos(a), r_in * math.sin(a)))
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def placed_box(w_tan, d_rad, h, r_center, z_center, ang):
    """周方向 w_tan、半径方向 d_rad、高さ h の直方体を、半径 r_center・角度 ang に置く"""
    b = cq.Workplane("XY").box(d_rad, w_tan, h).translate((r_center, 0, z_center))
    return b.rotate((0, 0, 0), (0, 0, 1), ang)


def coil(ang):
    """コイル：軸が半径方向の円環（ボビン省略）"""
    c = (cq.Workplane("YZ").circle(COIL_OD / 2).circle(COIL_ID / 2)
         .extrude(COIL_T).translate((R_COIL_IN, 0, COIL_Z)))
    return c.rotate((0, 0, 0), (0, 0, 1), ang)


# ---------------- 部品の生成 ----------------
def build():
    asm = cq.Assembly(name="linear_course")

    # 床
    asm.add(ring_sector(FLOOR_R_IN, FLOOR_R_OUT, -FLOOR_T, 0, 0, 360),
            name="floor", color=cq.Color(0.82, 0.80, 0.76))

    # 外壁（10区間に分割。区間ごとに色を交互に）
    for s in range(N_SEC):
        a0, a1 = s * 36.0 + 0.15, (s + 1) * 36.0 - 0.15
        col = cq.Color(0.90, 0.90, 0.92) if s % 2 == 0 else cq.Color(0.78, 0.80, 0.86)
        asm.add(ring_sector(R_WALL_IN, R_WALL_OUT, 0, WALL_H, a0, a1),
                name=f"wall_sec{s+1:02d}", color=col)
        # センサー台（壁に沿った棚）
        asm.add(ring_sector(SENSOR_RAIL_R_IN, R_WALL_IN, *SENSOR_RAIL_Z, a0, a1),
                name=f"sensor_rail_sec{s+1:02d}", color=cq.Color(0.35, 0.55, 0.35))
        # ガイドレール（壁上端の内向きフランジ）
        asm.add(ring_sector(RAIL_R_IN, R_WALL_IN, *RAIL_Z, a0, a1),
                name=f"guide_rail_sec{s+1:02d}", color=cq.Color(0.60, 0.62, 0.66))

    # コイル 60個（U V W の順、全部同じ向きに巻く）
    phase_col = {"U": cq.Color(0.90, 0.49, 0.13),
                 "V": cq.Color(0.95, 0.77, 0.06),
                 "W": cq.Color(0.09, 0.63, 0.52)}
    for k in range(N_COIL):
        ph = "UVW"[k % 3]
        ang = k * COIL_PITCH + COIL_PITCH / 2
        asm.add(coil(ang), name=f"coil_{k:02d}_{ph}", color=phase_col[ph])

    # ホールセンサー 20組×3（A・B・C）
    for g in range(N_GROUP):
        for i, lab in enumerate("ABC"):
            ang = g * GROUP_PITCH + 1.5 + i * HALL_IN_GROUP
            asm.add(placed_box(HALL_W, HALL_D, HALL_H, R_COIL_IN + HALL_D / 2, HALL_Z, ang),
                    name=f"hall_g{g:02d}_{lab}", color=cq.Color(0.08, 0.08, 0.08))
    # 原点センサー（床面、台車底の目印磁石を検出）
    asm.add(placed_box(HALL_W, HALL_H, HALL_D, 430.0, HALL_D / 2, 359.0),
            name="hall_index", color=cq.Color(0.85, 0.1, 0.1))

    # ---------- 台車 ----------
    c0 = CART_CENTER - CART_SPAN / 2
    # 磁石キャリア（円弧板）
    carrier_r_out = R_MAG_IN
    carrier_r_in = carrier_r_out - 6.0
    asm.add(ring_sector(carrier_r_in, carrier_r_out, 20.0, 100.0, c0 - 0.5, c0 + CART_SPAN + 0.5),
            name="cart_magnet_carrier", color=cq.Color(0.25, 0.27, 0.30))
    # 台車本体
    asm.add(ring_sector(380.0, carrier_r_in, 22.0, 60.0, c0 + 0.5, c0 + CART_SPAN - 0.5),
            name="cart_body", color=cq.Color(0.95, 0.95, 0.97))
    # 主磁石（S N S N S）とセンサー用小磁石
    pole_col = {"N": cq.Color(0.80, 0.15, 0.15), "S": cq.Color(0.15, 0.25, 0.70)}
    for i, p in enumerate(CART_POLES):
        ang = c0 + TAU * (i + 0.5)
        r_mid_main = (R_MAG_IN + R_MAG_OUT) / 2
        asm.add(placed_box(MAG_W, MAG_T, MAG_H, r_mid_main, COIL_Z, ang),
                name=f"magnet_main_{i}_{p}", color=pole_col[p])
        sw, st, sh = SENS_MAG
        r_mid_s = R_COIL_IN - GAP - st / 2
        asm.add(placed_box(sw, st, sh, r_mid_s, HALL_Z, ang),
                name=f"magnet_sensor_{i}_{p}", color=pole_col[p])
    # 原点用の目印磁石（台車底）
    asm.add(placed_box(8.0, 8.0, 3.0, 430.0, 18.5, c0 + TAU / 2),
            name="magnet_index_marker", color=cq.Color(0.8, 0.1, 0.1))
    # 車輪 4個（床を転がる）
    for ang in (c0 + 2.5, c0 + CART_SPAN - 2.5):
        for r in (395.0, 440.0):
            w = (cq.Workplane("XZ").circle(10.0).extrude(4.0, both=True)
                 .rotate((0, 0, 0), (0, 0, 1), 90)          # 軸を半径方向に
                 .translate((r, 0, 10.0))
                 .rotate((0, 0, 0), (0, 0, 1), ang))
            asm.add(w, name=f"wheel_{ang:.1f}_{r:.0f}", color=cq.Color(0.1, 0.1, 0.1))
    # ガイドローラー 2個（ガイドレール内面に当たり、遠心力を受ける）
    for ang in (c0 + 2.0, c0 + CART_SPAN - 2.0):
        rc = RAIL_R_IN - ROLLER_R
        roller = (cq.Workplane("XY").workplane(offset=RAIL_Z[0]).circle(ROLLER_R)
                  .extrude(RAIL_Z[1] - RAIL_Z[0]).translate((rc, 0, 0))
                  .rotate((0, 0, 0), (0, 0, 1), ang))
        post = (cq.Workplane("XY").workplane(offset=100.0).circle(3.0)
                .extrude(RAIL_Z[0] - 100.0).translate((rc, 0, 0))
                .rotate((0, 0, 0), (0, 0, 1), ang))
        asm.add(roller, name=f"guide_roller_{ang:.1f}", color=cq.Color(0.2, 0.2, 0.2))
        asm.add(post, name=f"roller_post_{ang:.1f}", color=cq.Color(0.5, 0.5, 0.5))
    return asm


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "linear_course.step"
    a = build()
    a.save(out)
    print("saved", out)
    print(f"R_C={R_C:.2f}  coil face R={R_COIL_IN:.2f}  magnet R={R_MAG_IN:.2f}-{R_MAG_OUT:.2f}")
    print(f"coil pitch at R_C = {R_C*math.radians(COIL_PITCH):.2f} mm, tau = {R_C*math.radians(TAU):.2f} mm")
