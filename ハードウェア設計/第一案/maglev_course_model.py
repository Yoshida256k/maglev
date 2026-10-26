"""浮上式リニアモーターカー コースモデル v0.2（浮いてるミニ四駆）

単位 mm。角度は +X 軸から反時計回り（FWD = 反時計回り）。
- 床：同極（N上向き）の浮上用磁石を2列で1周敷き詰め
- 台車：車輪なし。底面に同極（N下向き）の浮上磁石。左右の透明壁を2段ローラーでなぞる
- 外側：曲げた透明シート（内面がローラーの走行面）。その外にコイル枠（コイル60個・ホール列）
- 内側：曲げた透明板（内側ローラーの走行面）
"""
import math
import cadquery as cq

# ---------- コイル・磁極（仕様書 v0.2 と同じ） ----------
CIRC = 3000.0
R_C = CIRC / (2 * math.pi)            # コイル中心半径 ≈ 477.46
N_COIL = 60
COIL_PITCH = 6.0
TAU = 4.5
N_SEC = 10
COIL_OD, COIL_ID, COIL_T = 50.0, 20.0, 8.0
COIL_Z = 42.0
R_COIL_IN = R_C - COIL_T / 2          # ≈ 473.46
R_COIL_OUT = R_C + COIL_T / 2

# ---------- 外側：透明シート ----------
SHEET_T = 1.0                          # PC/PET 1mm（曲げて使う）
R_SHEET_OUT = R_COIL_IN                # コイル面にシートを密着
R_SHEET_IN = R_SHEET_OUT - SHEET_T     # ローラー走行面
SHEET_H = 110.0
GAP_ROLL = 4.0                         # 磁石面〜シート内面
R_MAG_OUT = R_SHEET_IN - GAP_ROLL      # 磁石〜コイル面 = 4 + 1 = 5mm

# ---------- 内側：透明板 ----------
TRACK_W = 110.0                        # 走行路の幅（内壁面〜外シート面）
R_INWALL_OUT = R_SHEET_IN - TRACK_W    # 内側ローラー走行面
INWALL_T, INWALL_H = 2.0, 100.0

# ---------- コイル枠（シートの外側） ----------
FRAME_BACK_T = 4.0
R_FRAME_IN = R_COIL_OUT
R_FRAME_OUT = R_FRAME_IN + FRAME_BACK_T
FRAME_H = SHEET_H

# ---------- ホールセンサー列（コイル上端から17mm上） ----------
HALL_Z = 84.0
HALL_W, HALL_D, HALL_H = 4.0, 3.0, 4.5
N_GROUP, GROUP_PITCH, HALL_IN_GROUP = 20, 18.0, 3.0

# ---------- 床と浮上磁石 ----------
BASE_T = 8.0
R_BASE_IN, R_BASE_OUT = R_INWALL_OUT - 25.0, R_FRAME_OUT + 15.0
LEV_ROWS = (R_INWALL_OUT + 30.0, R_SHEET_IN - 40.0)   # 浮上磁石列の中心半径
LEV_W, LEV_H = 12.0, 5.0               # 床磁石列の幅・厚さ（20×12×5 程度のブロックを並べる想定）
FLY_GAP = 6.0                          # 浮上高さ（床磁石上面〜台車磁石下面）

# ---------- 台車 ----------
CART_POLES = "SNSNS"
CART_CENTER = 90.0
POLE_SPAN = TAU * len(CART_POLES)      # 22.5°
MAG_T, MAG_H, MAG_W = 10.0, 40.0, 32.0
R_MAG_IN = R_MAG_OUT - MAG_T
SENS_MAG = (10.0, 5.0, 10.0)
CHASSIS_Z0 = LEV_H + FLY_GAP           # 台車の浮上磁石下面
LIFT_MAG = (20.0, 12.0, 5.0)           # 台車側の浮上磁石 W×D×H
CHASSIS_T = 3.0
ROLLER_R, ROLLER_H = 6.5, 6.0          # ミニ四駆の13mmローラー相当
ROLLER_Z = (22.0, 66.0)                # 下段・上段


def ring_sector(r_in, r_out, z0, z1, a0, a1, step=1.0):
    span = a1 - a0
    if span >= 359.999:
        return (cq.Workplane("XY").workplane(offset=z0)
                .circle(r_out).circle(r_in).extrude(z1 - z0))
    n = max(8, int(abs(span) / step))
    pts = [(r_out * math.cos(math.radians(a0 + span * i / n)),
            r_out * math.sin(math.radians(a0 + span * i / n))) for i in range(n + 1)]
    pts += [(r_in * math.cos(math.radians(a0 + span * i / n)),
             r_in * math.sin(math.radians(a0 + span * i / n))) for i in range(n, -1, -1)]
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def placed_box(w_tan, d_rad, h, r_center, z_center, ang):
    b = cq.Workplane("XY").box(d_rad, w_tan, h).translate((r_center, 0, z_center))
    return b.rotate((0, 0, 0), (0, 0, 1), ang)


def at_angle(wp, ang):
    return wp.rotate((0, 0, 0), (0, 0, 1), ang)


def coil(ang):
    c = (cq.Workplane("YZ").circle(COIL_OD / 2).circle(COIL_ID / 2)
         .extrude(COIL_T).translate((R_COIL_IN, 0, COIL_Z)))
    return at_angle(c, ang)


def cylinder_z(r, z0, z1, rc, ang):
    c = cq.Workplane("XY").workplane(offset=z0).circle(r).extrude(z1 - z0).translate((rc, 0, 0))
    return at_angle(c, ang)


# ---------- ミニ四駆風ボディ（ローカル座標：x=進行方向、y=外向き、z=上） ----------
def body_shell():
    L = 196.0
    y0, y1 = -46.0, 30.0       # 外側は駆動磁石の板を避ける
    zb = CHASSIS_Z0 + LIFT_MAG[2] + CHASSIS_T
    prof = [(-L/2, zb), (L/2, zb), (L/2, zb + 4), (L/2 - 45, zb + 16),
            (L/2 - 85, zb + 20), (-L/2 + 30, zb + 22), (-L/2 + 6, zb + 21), (-L/2, zb + 12)]
    shell = (cq.Workplane("XZ").polyline(prof).close().extrude(-(y1 - y0)).translate((0, y0, 0)))
    for sel, r in (("|Z", 14.0), ("|Y", 3.0)):
        try:
            shell = shell.edges(sel).fillet(r)
        except Exception:
            pass
    # キャノピー
    canopy = (cq.Workplane("XY").workplane(offset=zb + 17).center(-10, -8)
              .ellipse(32, 15).extrude(12))
    try:
        canopy = canopy.faces(">Z").edges().fillet(6.0)
    except Exception:
        pass
    # リアウイング
    wing = cq.Workplane("XY").box(22, y1 - y0 + 6, 3).translate((-L/2 + 6, (y0 + y1) / 2, zb + 38))
    posts = (cq.Workplane("XY").pushPoints([(-L/2 + 8, y0 + 14), (-L/2 + 8, y1 - 14)])
             .rect(4, 3).extrude(18).translate((0, 0, zb + 19)))
    # フロントバンパー（ローラーステーへつながる）
    bumper = cq.Workplane("XY").box(10, y1 - y0 + 4, 8).translate((L/2 - 2, (y0 + y1) / 2, zb + 3))
    return shell, canopy, wing.union(posts), bumper


def to_track(wp, rc, ang):
    """ローカル座標の形状を、中心半径 rc・中心角 ang に配置（x→接線、y→外向き）"""
    w = wp.rotate((0, 0, 0), (0, 0, 1), -90).translate((rc, 0, 0))   # x軸→+Y(接線), y軸→+X(半径)
    return at_angle(w, ang)


def build_showcase(half_span=26.0):
    asm = cq.Assembly(name="showcase")
    a0, a1 = CART_CENTER - half_span, CART_CENTER + half_span
    asm.add(ring_sector(R_BASE_IN, R_SHEET_OUT, -BASE_T, 0, a0, a1), name="base", color=cq.Color(0.15, 0.15, 0.17))
    for i, rr in enumerate(LEV_ROWS):
        asm.add(ring_sector(rr - LEV_W / 2, rr + LEV_W / 2, 0, LEV_H, a0, a1),
                name=f"lev_floor_row{i}", color=cq.Color(0.80, 0.15, 0.15))
    asm.add(ring_sector(R_SHEET_IN, R_SHEET_OUT, 0, SHEET_H, a0, a1), name="outer_clear_sheet",
            color=cq.Color(0.70, 0.85, 0.95, 0.25))
    add_cart(asm)
    return asm


def build(include_cart=True, cart_only=False):
    asm = cq.Assembly(name="maglev_course")
    clear = cq.Color(0.70, 0.85, 0.95, 0.25)

    if not cart_only:
        asm.add(ring_sector(R_BASE_IN, R_BASE_OUT, -BASE_T, 0, 0, 360),
                name="base", color=cq.Color(0.15, 0.15, 0.17))
        # 浮上用の床磁石（N上向き、2列）
        for i, rr in enumerate(LEV_ROWS):
            asm.add(ring_sector(rr - LEV_W / 2, rr + LEV_W / 2, 0, LEV_H, 0, 360),
                    name=f"lev_floor_row{i}", color=cq.Color(0.80, 0.15, 0.15))
        # 内側の透明板
        asm.add(ring_sector(R_INWALL_OUT - INWALL_T, R_INWALL_OUT, 0, INWALL_H, 0, 360),
                name="inner_clear_wall", color=clear)
        # 外側の透明シート
        asm.add(ring_sector(R_SHEET_IN, R_SHEET_OUT, 0, SHEET_H, 0, 360),
                name="outer_clear_sheet", color=clear)
        # コイル枠（10区間）
        for s in range(N_SEC):
            a0, a1 = s * 36.0 + 0.15, (s + 1) * 36.0 - 0.15
            # コイル枠も透明：背板＝曲げたPC板、上下の縁＝レーザーカットのアクリル平リング
            back = ring_sector(R_FRAME_IN, R_FRAME_OUT, 0, FRAME_H, a0, a1)
            rim_b = ring_sector(R_SHEET_OUT, R_FRAME_IN, 0, 10, a0, a1)
            rim_t = ring_sector(R_SHEET_OUT, R_FRAME_IN, FRAME_H - 8, FRAME_H, a0, a1)
            rail = ring_sector(R_SHEET_OUT + HALL_D, R_FRAME_IN, HALL_Z - 10, HALL_Z + 10, a0, a1)
            asm.add(back, name=f"coil_frame_back_sec{s+1:02d}", color=clear)
            asm.add(rim_b.union(rim_t), name=f"coil_frame_rims_sec{s+1:02d}", color=clear)
            asm.add(rail, name=f"sensor_rail_sec{s+1:02d}", color=cq.Color(0.30, 0.52, 0.32))
        phase_col = {"U": cq.Color(0.90, 0.49, 0.13), "V": cq.Color(0.95, 0.77, 0.06),
                     "W": cq.Color(0.09, 0.63, 0.52)}
        for k in range(N_COIL):
            ph = "UVW"[k % 3]
            asm.add(coil(k * COIL_PITCH + COIL_PITCH / 2), name=f"coil_{k:02d}_{ph}", color=phase_col[ph])
        for g in range(N_GROUP):
            for i, lab in enumerate("ABC"):
                ang = g * GROUP_PITCH + 1.5 + i * HALL_IN_GROUP
                asm.add(placed_box(HALL_W, HALL_D, HALL_H, R_SHEET_OUT + HALL_D / 2, HALL_Z, ang),
                        name=f"hall_g{g:02d}_{lab}", color=cq.Color(0.05, 0.05, 0.05))

    if include_cart:
        add_cart(asm)
    return asm


def add_cart(asm):
    c0 = CART_CENTER - POLE_SPAN / 2
    rm = (R_INWALL_OUT + R_SHEET_IN) / 2           # 走行路の中心半径
    blue, white, red = cq.Color(0.10, 0.32, 0.80), cq.Color(0.97, 0.97, 0.98), cq.Color(0.85, 0.12, 0.12)
    dark = cq.Color(0.18, 0.19, 0.22)

    # シャーシ（円弧板）
    zc0 = CHASSIS_Z0 + LIFT_MAG[2]
    span_ch = POLE_SPAN + 5.0
    asm.add(ring_sector(R_INWALL_OUT + 14, R_MAG_IN, zc0, zc0 + CHASSIS_T,
                        CART_CENTER - span_ch / 2, CART_CENTER + span_ch / 2, 0.5),
            name="cart_chassis", color=dark)
    # 浮上磁石（台車側、N下向き）2列×4
    for rr in LEV_ROWS:
        for j in range(4):
            ang = CART_CENTER + (j - 1.5) * (POLE_SPAN / 4)
            asm.add(placed_box(LIFT_MAG[0], LIFT_MAG[1], LIFT_MAG[2], rr, CHASSIS_Z0 + LIFT_MAG[2] / 2, ang),
                    name=f"lev_cart_{rr:.0f}_{j}", color=red)
    # 駆動磁石キャリア（外側の“サイドポッド”）
    asm.add(ring_sector(R_MAG_IN - 5, R_MAG_IN, zc0, HALL_Z + 8, c0 - 0.5, c0 + POLE_SPAN + 0.5, 0.5),
            name="cart_magnet_pod", color=cq.Color(0.20, 0.30, 0.55, 0.45))
    pole_col = {"N": red, "S": cq.Color(0.15, 0.25, 0.70)}
    for i, p in enumerate(CART_POLES):
        ang = c0 + TAU * (i + 0.5)
        asm.add(placed_box(MAG_W, MAG_T, MAG_H, (R_MAG_IN + R_MAG_OUT) / 2, COIL_Z, ang),
                name=f"magnet_drive_{i}_{p}", color=pole_col[p])
        sw, st, sh = SENS_MAG
        asm.add(placed_box(sw, st, sh, R_MAG_OUT - st / 2, HALL_Z, ang),
                name=f"magnet_sensor_{i}_{p}", color=pole_col[p])

    # ボディ
    shell, canopy, wing, bumper = body_shell()
    asm.add(to_track(shell, rm, CART_CENTER), name="body_shell", color=blue)
    asm.add(to_track(canopy, rm, CART_CENTER), name="body_canopy", color=cq.Color(0.08, 0.10, 0.14))
    asm.add(to_track(wing, rm, CART_CENTER), name="body_wing", color=white)
    asm.add(to_track(bumper, rm, CART_CENTER), name="body_bumper", color=white)

    # 2段ローラー：前後 × 内外 × 上下 = 8個、ステー付き
    a_front = CART_CENTER + span_ch / 2 + 1.2
    a_rear = CART_CENTER - span_ch / 2 - 1.2
    r_out_roll = R_SHEET_IN - ROLLER_R - 0.3
    r_in_roll = R_INWALL_OUT + ROLLER_R + 0.3
    for tag, ang in (("F", a_front), ("R", a_rear)):
        stay = ring_sector(r_in_roll, r_out_roll, zc0, zc0 + 3, ang - 1.1, ang + 1.1, 0.3)
        asm.add(stay, name=f"roller_stay_{tag}", color=cq.Color(0.22, 0.22, 0.24))
        for side, rc in (("out", r_out_roll), ("in", r_in_roll)):
            pin = cylinder_z(1.6, zc0, ROLLER_Z[1] + ROLLER_H + 2, rc, ang)
            asm.add(pin, name=f"roller_shaft_{tag}_{side}", color=cq.Color(0.75, 0.75, 0.78))
            for lv, zr in zip(("low", "up"), ROLLER_Z):
                asm.add(cylinder_z(ROLLER_R, zr, zr + ROLLER_H, rc, ang),
                        name=f"roller_{tag}_{side}_{lv}", color=cq.Color(0.95, 0.85, 0.20))


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "maglev_course.step"
    build().save(out)
    print("saved", out)
    print(f"sheet in R={R_SHEET_IN:.2f}, inner wall R={R_INWALL_OUT:.2f}, magnet R={R_MAG_IN:.2f}-{R_MAG_OUT:.2f}")
    print(f"magnet->coil gap = {R_COIL_IN - R_MAG_OUT:.2f}, fly gap = {FLY_GAP}")
