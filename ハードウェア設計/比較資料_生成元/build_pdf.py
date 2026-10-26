import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Spacer, Table,
                                TableStyle, Image, PageBreak, KeepTogether)

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "浮いてるミニ四駆_第一案第二案比較.pdf")

pdfmetrics.registerFont(TTFont("JP", "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"))
pdfmetrics.registerFont(TTFont("JPM", "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"))
from reportlab.lib.fonts import addMapping
for b in (0, 1):
    for i in (0, 1):
        addMapping("JP", b, i, "JP")
import reportlab.platypus as _rp
_Para = _rp.Paragraph
class Paragraph(_Para):
    """太字のない日本語フォントなので、<b> は濃い青の強調色で表す"""
    def __init__(self, text, style, *a, **k):
        text = text.replace("<b>", '<font color="#0b3fb3">').replace("</b>", "</font>")
        super().__init__(text, style, *a, **k)

NAVY = colors.HexColor("#14213d")
BLUE = colors.HexColor("#1a5ce0")
CYAN = colors.HexColor("#14a9c4")
ORANGE = colors.HexColor("#e67e22")
GRAY = colors.HexColor("#5f6670")
LIGHT = colors.HexColor("#eef2f8")
P1C = colors.HexColor("#6b7a90")     # 第一案の色
P2C = colors.HexColor("#1a5ce0")     # 第二案の色

def st(name, size, lead=None, color=NAVY, align=0, space_after=0, font="JP"):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=lead or size * 1.45,
                          textColor=color, alignment=align, spaceAfter=space_after, wordWrap="CJK")

S_TITLE = st("title", 28, 38, NAVY)
S_SUB = st("sub", 14, 22, GRAY)
S_H1 = st("h1", 19, 26, NAVY, space_after=2)
S_H2 = st("h2", 12.5, 18, BLUE, space_after=2)
S_BODY = st("body", 10.5, 16.5, colors.HexColor("#22262b"))
S_SMALL = st("small", 9, 13.5, GRAY)
S_CELL = st("cell", 9.2, 13.2, colors.HexColor("#22262b"))
S_CELLB = st("cellb", 9.2, 13.2, NAVY)
S_HEAD = st("head", 9.6, 13.5, colors.white)
S_BOX = st("box", 11, 17, NAVY)

PW, PH = landscape(A4)
M = 14 * mm
CW = PW - 2 * M


def on_page(canv, doc):
    canv.saveState()
    if doc.page > 1:
        canv.setFillColor(NAVY)
        canv.rect(0, PH - 9 * mm, PW, 9 * mm, stroke=0, fill=1)
        canv.setFillColor(colors.white)
        canv.setFont("JP", 9.5)
        canv.drawString(M, PH - 6 * mm, "浮いてるミニ四駆　卓上リニアモーターカー　第一案・第二案の比較")
    canv.setFillColor(GRAY)
    canv.setFont("JP", 8.5)
    canv.drawRightString(PW - M, 7 * mm, f"{doc.page}")
    canv.drawString(M, 7 * mm, "2026-10-25　検討資料（数値は計算・設計値。試作で確認が必要なものを含む）")
    canv.restoreState()


def img(name, width):
    p = os.path.join(HERE, name)
    from PIL import Image as PI
    w, h = PI.open(p).size
    return Image(p, width=width, height=width * h / w)


def bullets(items, style=S_BODY):
    return [Paragraph("・" + t, style) for t in items]


def table(rows, col_w, head=True, zebra=True, first_col_style=S_CELLB, style_extra=()):
    data = []
    for i, r in enumerate(rows):
        if i == 0 and head:
            data.append([Paragraph(c, S_HEAD) for c in r])
        else:
            data.append([Paragraph(c, first_col_style if j == 0 else S_CELL) for j, c in enumerate(r)])
    t = Table(data, colWidths=col_w, repeatRows=1 if head else 0)
    cmds = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d0da")),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 3.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2)]
    if head:
        cmds.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        for i in range(1 if head else 0, len(rows)):
            if i % 2 == 0:
                cmds.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    cmds += list(style_extra)
    t.setStyle(TableStyle(cmds))
    return t


def callout(text, color=BLUE, bg=colors.HexColor("#eaf1ff"), width=None):
    t = Table([[Paragraph(text, S_BOX)]], colWidths=[width or CW])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg),
                           ("LINEBEFORE", (0, 0), (0, -1), 4, color),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def two_col(left, right, wl, wr, gap=6 * mm):
    t = Table([[left, "", right]], colWidths=[wl, gap, wr])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return t


S_KN = st("kn", 20, 24, NAVY, align=1)
S_KL = st("kl", 9, 12, GRAY, align=1)


def kpis(items, color):
    cells = [[Paragraph(v, S_KN) for _, v in items], [Paragraph(k, S_KL) for k, _ in items]]
    w = CW / len(items)
    t = Table(cells, colWidths=[w] * len(items))
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f6fa")),
                           ("LINEABOVE", (0, 0), (-1, 0), 3, color),
                           ("LINEAFTER", (0, 0), (-2, -1), 0.6, colors.white),
                           ("TOPPADDING", (0, 0), (-1, 0), 8), ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return t


def caption(text):
    return Paragraph(text, S_SMALL)


story = []

# ---------------- 1. 表紙 ----------------
story += [Spacer(1, 6 * mm),
          Paragraph("浮いてるミニ四駆", S_TITLE),
          Paragraph("卓上リニアモーターカー　第一案・第二案の比較とスペック", S_SUB),
          Spacer(1, 4 * mm),
          img("f_eye_level.png", CW),
          caption("第二案（床下駆動）の完成イメージ。外側の透明フェンス越しに、床から約6mm浮いた台車と、光るホイールハウス・アンダーグローが見える"),
          Spacer(1, 5 * mm),
          callout("コンセプト：車輪のないミニ四駆が、永久磁石の反発で床から浮き、リニアモーターで透明なコースを周回する。"
                  "左右の透明壁はミニ四駆と同じ2段ローラーでなぞる。"),
          PageBreak()]

# ---------------- 2. 共通の仕組み ----------------
left = [Paragraph("どうやって動くか（両案共通）", S_H2)] + bullets([
    "<b>浮く</b>：床の磁石（N極が上）と台車の底の磁石（N極が下）が反発して、約6mm浮く。浮くのに電力は使わない",
    "<b>進む</b>：コースに並べたコイルに3相の交流を流し、台車の駆動磁石（S N S N S の5極）を引っ張る。リニア同期モーター（LSM）",
    "<b>ぶつからない</b>：磁石の反発だけでは横方向に必ず不安定になる（アーンショーの定理）。そのため左右の透明壁を2段ローラーで常になぞって走る",
    "<b>位置がわかる</b>：ホールセンサー60個を全部読み、磁石のパターンから台車の位置を求める。電源を入れた直後から絶対位置がわかるので、好きな場所に止められる",
    "<b>電気を節約</b>：コースを10区間に分け、台車がいる区間と次の区間だけリレーで通電する",
]) + [Spacer(1, 3 * mm), Paragraph("2つの案の違い", S_H2)] + bullets([
    "<b>第一案（側面駆動）</b>：コイルを外壁に縦に並べ、台車の外側に立てた板の駆動磁石を横から押す",
    "<b>第二案（床下駆動）</b>：コイルを床下に寝かせて並べ、台車の底の駆動磁石を下から押す",
])
common = table([
    ["項目", "共通スペック"],
    ["コース", "円周 3.0 m の周回コース（コイル60個、10区間）"],
    ["駆動方式", "地上一次式リニア同期モーター（3相、空芯コイル）"],
    ["コイル配置", "3：4（コイル3個に磁極4個）。コイル間隔6°、磁極ピッチ4.5°（約37.5mm）"],
    ["コイル", "UEW 0.9mm × 80回、手巻き（線は合計約600m）"],
    ["インバーター", "IGBT 3相、ゲートドライバー IR2104、DC 24V、キャリア 20kHz"],
    ["区間切替", "2極リレー × 10（台車の先を読んでON/OFF）"],
    ["浮上", "永久磁石の反発、浮上高さ 約6mm（試作で確認）"],
    ["案内", "φ13 の2段ローラー（ベアリング入り）× 8"],
    ["位置検出", "ホールIC（OH44E / A3144）60個、74HC165で個別読み出し"],
    ["最高速度", "設計 30 km/h（1周 0.36秒）。展示は 10〜15 km/h を推奨"],
    ["消費電力", "走行中のコイル発熱 約13.5W（3区間ON時）"],
    ["保護", "ハードウェア過電流保護、非常停止、絶縁電源、防護囲い"],
], [30 * mm, 98 * mm])
story += [Paragraph("共通の仕組みとスペック", S_H1), Spacer(1, 2 * mm),
          two_col(left, common, CW - 134 * mm, 128 * mm), PageBreak()]

# ---------------- 3. 第一案 ----------------
story += [Paragraph('<font color="#6b7a90">第一案</font>　側面駆動：コイルを外壁に並べる', S_H1), Spacer(1, 2 * mm),
          two_col([img("m_overall.png", CW / 2 - 3 * mm), caption("コース全体。外壁は透明シート＋透明なコイル枠で、コイルが外から見える")],
                  [img("m_cart_only.png", CW / 2 - 3 * mm), caption("台車。外側の半透明ポッドに駆動磁石5極（赤=N、青=S）とセンサー用磁石")],
                  CW / 2 - 3 * mm, CW / 2 - 3 * mm),
          Spacer(1, 3 * mm)]
story += bullets([
    "コイル60個（外径50mm）を外壁に縦向きに並べ、1mmの透明シート越しに台車の駆動磁石と向き合う。磁石とコイルの隙間は5mm",
    "ホールセンサーはコイル列の17mm上（高さ84mm）。そのため駆動ポッドが高くなり、<b>台車の高さは約92mm</b>",
    "遠心力（30km/hで約73N）は「ローラー → 透明シート → コイル → 背板」と伝わる。背板がたわむと磁石とコイルの隙間が広がる",
    "コイルが外壁に並んで見えるので「メカ感」は強いが、ミニ四駆らしさは弱い",
])
story += [Spacer(1, 4 * mm), kpis([("台車の高さ", "約 92 mm"), ("磁石〜コイルの隙間", "5 mm"),
                                     ("推力の目安（200AT）", "約 3 N"), ("コースの外径", "約 1.0 m"),
                                     ("床の浮上磁石", "約 260 個")], P1C)]
story.append(PageBreak())

# ---------------- 4. 第二案 ----------------
story += [Paragraph('<font color="#1a5ce0">第二案</font>　床下駆動：コイルを床下に寝かせる', S_H1), Spacer(1, 2 * mm),
          two_col([img("f_overall.png", CW / 2 - 3 * mm), caption("コース全体（展示状態）。床はミラーまたは黒のカバーで仕組みを隠す。台車付近のLED帯が点灯")],
                  [img("f_cart_3q.png", CW / 2 - 3 * mm), caption("台車。高さ約40mm。タイヤ位置は空で中が光る。底に駆動磁石5極と浮上磁石8個")],
                  CW / 2 - 3 * mm, CW / 2 - 3 * mm),
          Spacer(1, 3 * mm)]
story += bullets([
    "コイル60個（外径48mm）を床下に寝かせて並べ、その左右に浮上磁石を2列。床は1mmのカバーで覆う。磁石とコイルの隙間は7mm",
    "駆動磁石は台車の底に下向き。外側に高い板が不要になり、<b>台車の高さは約40mm</b>（本物のミニ四駆とほぼ同じ）",
    "壁は内外とも純粋なガイド用の透明フェンス。遠心力はローラーとフェンスだけで受け、<b>コイルの隙間には影響しない</b>",
    "ホールセンサーは内側フェンスの根元の裏。外側（観客側）から見たときに浮上の隙間を隠さない",
    "演出：空のホイールハウスが光る、台車の底のアンダーグロー、台車の通過に合わせて光るLED帯",
])
story += [Spacer(1, 4 * mm), kpis([("台車の高さ", "約 40 mm"), ("磁石〜コイルの隙間", "7 mm"),
                                     ("推力の目安（200AT）", "約 2.6 N"), ("コースの外径", "約 1.14 m"),
                                     ("床の浮上磁石", "約 300 個")], P2C)]
story.append(PageBreak())

# ---------------- 5. 断面図の比較 ----------------
story += [Paragraph("断面図の比較（台車の位置で切った図、単位 mm）", S_H1), Spacer(1, 2 * mm),
          two_col([Paragraph("第一案（側面駆動）", S_H2), img("m_section.png", CW * 0.44)],
                  [Paragraph("第二案（床下駆動）", S_H2), img("f_section.png", CW * 0.53),
                   Spacer(1, 4 * mm),
                   callout("<b>一番の違いは台車の高さ</b>：第一案 約92mm → 第二案 約40mm。<br/>"
                           "代わりに、第二案は磁石とコイルの隙間が 5mm → 7mm に広がり、推力が約15%下がる見込み。",
                           P2C, width=CW * 0.53)],
                  CW * 0.44, CW * 0.53, gap=CW * 0.03),
          PageBreak()]

# ---------------- 6. スペック比較表 ----------------
cmp_rows = [
    ["項目", "第一案　側面駆動", "第二案　床下駆動"],
    ["コイルの位置", "外壁に縦向き（透明シートの外側、透明なコイル枠）", "床下に寝かせる（床カバーで隠す）"],
    ["コイル", "60個、外径 50mm", "60個、外径 48mm（平らに並べると隣と接触するため）"],
    ["駆動磁石の位置", "台車の外側面（外向き）", "台車の底面（下向き）"],
    ["磁石〜コイルの隙間", "5 mm（すき間4 ＋ シート1）", "7 mm（浮上6 ＋ 床カバー1）"],
    ["推力の目安（200AT時）", "約 3 N", "約 2.6 N（約15%減）"],
    ["台車の高さ", "約 92 mm", "<b>約 40 mm</b>"],
    ["台車の大きさ（ローラー除く）", "長さ 約196 × 幅 約76 mm（＋外側ポッド）", "長さ 約172 × 幅 約92 mm"],
    ["走行路の幅", "110 mm", "124 mm"],
    ["コースの外径", "約 1.0 m", "約 1.14 m"],
    ["壁", "内：透明板／外：透明シート＋透明コイル枠", "内外とも透明フェンス（外側は透明リブで補強）"],
    ["ホールセンサーの位置", "外壁、コイルの上（高さ84mm）", "内側フェンスの根元の裏（高さ15mm）"],
    ["遠心力（30km/h、約73N）の受け方", "ローラー → シート → コイル → 背板。背板のたわみで隙間が変わる", "ローラー → フェンスのみ。コイルの隙間は変わらない"],
    ["浮上の見え方", "見えるが、高い駆動ポッドが目立つ", "真横から隙間とアンダーグローがよく見える"],
    ["ミニ四駆らしさ", "低い", "<b>高い</b>"],
    ["見えるメカ", "外壁にコイルが並ぶ（メカ感が強い）", "床はミラー/黒で、仕組みが見えない"],
    ["床の浮上磁石", "約 260 個（半径 392.5 / 432.5 mm の2列）", "約 300 個（半径 432.5 / 522.5 mm の2列）"],
    ["磁石の費用（全体）", "約 1.5万〜2.7万円", "約 1.6万〜2.9万円"],
    ["加工のしやすさ", "曲げた透明シートにコイルを固定し、透明背板を補強する必要あり", "平らな土台にコイルと磁石を埋めるので加工しやすい"],
]
hl = [("BACKGROUND", (2, 6), (2, 6), colors.HexColor("#dfe9ff")),
      ("BACKGROUND", (2, 14), (2, 14), colors.HexColor("#dfe9ff")),
      ("BACKGROUND", (2, 5), (2, 5), colors.HexColor("#fff1e0")),
      ("BACKGROUND", (2, 4), (2, 4), colors.HexColor("#fff1e0"))]
story += [Paragraph("スペック比較", S_H1), Spacer(1, 2 * mm),
          table(cmp_rows, [52 * mm, (CW - 52 * mm) / 2, (CW - 52 * mm) / 2], style_extra=hl),
          Spacer(1, 2 * mm),
          caption("青の網掛け：第二案が有利な主な点。オレンジの網掛け：第二案が不利な主な点。推力・浮上高さ・磁石の単価は見積もりで、試作で確認する"),
          PageBreak()]

# ---------------- 7. 評価とおすすめ ----------------
pc = table([
    ["", "第一案　側面駆動", "第二案　床下駆動"],
    ["よい点", "・磁石とコイルの隙間が小さく、推力が出しやすい<br/>・浮上高さが変わっても駆動の隙間は変わらない<br/>・コイルが見えて仕組みが伝わりやすい",
     "・台車が低く、本物のミニ四駆に近い<br/>・浮いている隙間が真横からよく見える<br/>・遠心力がコイルにかからない<br/>・土台が平らで加工しやすい"],
    ["悪い点・リスク", "・駆動ポッドが高く、ミニ四駆に見えにくい<br/>・背板がたわむと隙間が変わり推力が落ちる<br/>・ホールセンサーがコイルに比較的近い",
     "・推力が約15%下がる<br/>・浮上高さの変化（荷重・駆動の上下の力）がそのまま推力の変化になる<br/>・床の浮上磁石の磁界がホールセンサーに影響する可能性<br/>・コースが少し大きくなる"],
], [30 * mm, (CW - 30 * mm) / 2, (CW - 30 * mm) / 2])
story += [Paragraph("評価とおすすめ", S_H1), Spacer(1, 2 * mm), pc, Spacer(1, 5 * mm),
          callout("<b>おすすめ：第二案（床下駆動）</b><br/>"
                  "「浮いてるミニ四駆」というコンセプトを一番伝えられるのは、台車が低く、浮いている隙間が真横から見える第二案。"
                  "推力の低下は、床カバーを0.5mmにする・巻数を見直すことで補える見込み。<br/>"
                  "ただし、<b>浮上試験と推力（逆起電力）の試作で問題がないことを確認してから決定</b>する。"
                  "試作で推力や浮上の安定が足りなければ第一案に戻す。", P2C),
          Spacer(1, 5 * mm),
          Paragraph("グループで決めたいこと", S_H2)]
story += bullets([
    "第一案と第二案のどちらで進めるか（試作の結果を待って最終決定するか）",
    "床の仕上げ：ミラーアクリル（映り込みで浮いているのが目立つ）か、黒アクリル（落ち着いた見た目）か",
    "台車のボディ：市販のミニ四駆のボディを流用するか、自作するか",
    "展示の速度：最高速チャレンジ（30km/h）を見せるか、10〜15km/hに抑えるか",
])
story.append(PageBreak())

# ---------------- 8. 試作と展示の見せ方 ----------------
tests = table([
    ["順番", "試作・確認すること", "合格の目安", "対象"],
    ["1", "浮上試験：床磁石を20cm分（約20個）並べ、台車の底板＋おもりを載せる", "約6mm浮き、ローラーで横を押さえれば安定する", "両案"],
    ["2", "コイル試作：2〜3個巻いて R・L と逆起電力を測る", "30km/h換算で1個あたり約7Vピーク（ずれたら巻数を調整）", "両案"],
    ["3", "ホールセンサーの選別：全数を磁石で確認、コイルに電流を流して誤動作がないか", "S極でON・離すとOFF、コイルだけでは反応しない", "両案"],
    ["4", "駆動電流を流した状態で浮上高さを測る", "変化が1〜2mm以内、床に接触しない", "第二案"],
    ["5", "浮上磁石の近くでホールセンサーが正しく反応するか", "台車のセンサー用磁石で確実にON/OFF", "第二案"],
], [16 * mm, 112 * mm, 100 * mm, CW - 228 * mm])
show = table([
    ["場面", "見せ方"],
    ["① ゆっくり登場して止まる", "観客の正面に台車を運んで止める（位置決め機能）。浮いていること・タイヤがないことを見てもらう"],
    ["② 浮いている証拠", "止まったまま台車を上下にふわふわ揺らす（第二案で実現できる可能性あり、要試作）"],
    ["③ 加速して周回", "10〜15km/hで周回。LED帯が台車を追いかけ、アンダーグローが光の筋になる"],
    ["④ 最高速チャレンジ", "30km/h（1周0.36秒）。速すぎて浮いているのは見えないので、締めの演出として1回だけ"],
], [48 * mm, CW - 48 * mm])
cost = table([
    ["磁石", "用途", "第一案", "第二案", "単価の目安"],
    ["20×10×5 mm", "床と台車の浮上磁石", "約 290 個", "約 320 個", "40〜70 円"],
    ["30×20×10 mm", "駆動磁石（1極2個×5極）", "12 個", "12 個", "200〜500 円"],
    ["10×10×5 mm", "センサー用小磁石", "10 個", "10 個", "15〜30 円"],
    ["合計", "", "約 1.5万〜2.7万円", "約 1.6万〜2.9万円", "AliExpress・N35、1ドル150円換算"],
], [30 * mm, 52 * mm, 34 * mm, 34 * mm, CW - 150 * mm])
story += [Paragraph("次の試作と展示の見せ方", S_H1), Spacer(1, 1 * mm),
          Paragraph("試作の順番（磁石は最初に20個程度だけ買い、浮上を確認してから残りを買う）", S_H2), tests,
          Spacer(1, 3 * mm), Paragraph("展示の流れ（案）", S_H2), show,
          Spacer(1, 3 * mm), Paragraph("磁石の費用", S_H2), cost]

doc = BaseDocTemplate(OUT, pagesize=landscape(A4), leftMargin=M, rightMargin=M,
                      topMargin=13 * mm, bottomMargin=12 * mm,
                      title="浮いてるミニ四駆 第一案・第二案の比較", author="", subject="卓上リニアモーターカー 検討資料")
frame = Frame(M, 12 * mm, CW, PH - 25 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=on_page)])
doc.build(story)
print("wrote", OUT)
