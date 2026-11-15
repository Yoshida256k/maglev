# インバータ回路図（circuitikz 版）

`ハードウェア設計/インバータの回路図.jpg`（手書き）を circuitikz で描き直したものです。

| ファイル | 内容 |
|---|---|
| `inverter_circuit.tex` | 回路図のソース（LuaLaTeX + circuitikz） |
| `inverter_circuit.pdf` | ビルド済み PDF |
| `inverter_circuit.png` | プレビュー（200 dpi） |

## 環境構築

日本語を含むため LuaLaTeX を使います。circuitikz と luatexja が必要です。

**Ubuntu / Debian（動作確認: Ubuntu 24.04）**

```
sudo apt-get install -y texlive-pictures texlive-latex-extra texlive-lang-japanese \
  texlive-luatex fonts-noto-cjk
```

- `texlive-pictures` に circuitikz が入っています。
- `texlive-lang-japanese` に luatexja が入っています。

**Windows / macOS**

TeX Live（または MacTeX）を入れたうえで、次を実行します。

```
tlmgr install circuitikz luatexja
```

## ビルド

```
cd "ハードウェア設計/インバータ回路図"
lualatex inverter_circuit.tex
```

## 原図からの修正点

| # | 原図の内容 | 修正後 |
|---|---|---|
| 1 | 上側 IGBT の共通コレクタ母線（P 側）に U・V・W と書かれていた | 母線は `P (+)` とし、出力端子 U・V・W は各相の上下 IGBT の中点に付けた |
| 2 | 直列抵抗の両端に電圧計（V） | 電流検出用シャント `R_sh` として表記し、`V_sh` は両端電圧（I = V / R_sh） |
| 3 | 可変変圧器の上端に、どこにも接続されない端子（o）があった | 削除。電源は巻線の両端に接続し、ワイパー出力を F → 整流器へ |
| 4 | 「ツェナ」（TVS） | 双方向ツェナー 2 個を逆直列にした TVS と表記 |
| 5 | 「スナバ」 | R と C の直列による RC スナバと表記 |
| 6 | 配線の交差に接続点の印がなく、接続か交差か判別しにくい | 交差は接続しない（点なし）、接続点は黒丸で明示 |
| 7 | IGBT のゲート信号が描かれていなかった | `G_UH`〜`G_WL` を追記し、絶縁ドライバ経由と注記 |
| 8 | 分数が `1.5 / n` の形になっていなかった | `P = P_total × 1.5 / n`（n：分割数）として分数表記 |
| 9 | 中央下の回路が「VOM1271 か ゲートドライバ」と書かれていた | 「双方向スイッチ（VOM1271 等）」の 1 個分として描き、TVS と RC スナバを接点の両端に並列 |

## 未確認事項（原図で判読できなかったもの）

- 左上の注記（「…の長さが図面の半分」）と、左下の薄い注記（「…に 7.5…」）は判読できなかったため転記していません。
- モータのコイル区間数（原図では 2 群のみ描き、残りは「⋯」）。仕様書の「コイル 60 個・10 区間」と対応しているかは確認が必要です。
- VOM1271 を使う場合は、データシートで耐圧・電流定格がコイルの電圧・電流に足りるか確認してください。
