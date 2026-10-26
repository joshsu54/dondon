# Environment Transition Kit v01｜半寫實仙俠環境收邊模組包

不規則道路收邊（A，11 件）、河岸收邊（B，10 件）、橋頭與地形交接收邊（C，8 件），共 29 件可重複拼接的獨立模組。依《Claude 專用完整任務書｜半寫實仙俠環境收邊模組包》執行。

**受保護資產：未修改。** 樹伴古樹、山兔、主世界 `.blend` 不在本環境中，本專案也不讀取、連結或改動它們；所有檔案只寫在本資料夾內。

## 目前進度

| 階段 | 狀態 |
| --- | --- |
| PHASE 0 安全檢查 | 完成：`06_Reports/PHASE0_Safety.md` |
| PHASE 1 規格、清單、三視圖 | 完成：29 張設計三視圖與 REF_A–E；REF_F 材質板待建模階段 |
| PHASE 2 之後（建模、貼圖、QA、匯出） | **暫停，等使用者看過三視圖後決定** |

審閱重點見 `06_Reports/PHASE1_ThreeViews_Review.md`。

## 資料夾

```
00_References/   三視圖（ThreeViews/）、REF_A–E 總表與工程圖、生圖提示詞
05_Scripts/      kit_spec.py（唯一數值來源）、draw_three_views.py、write_reports.py、
                 phase0_safety_check.py、kit_blender.py（建模共用工具，尚未執行）
06_Reports/      PHASE0_Safety、ASSUMPTIONS、ASSET_MANIFEST（.md／.csv）、PHASE1 審閱清單
01_Blender/ 02_Exports/ 03_Textures/ 04_Previews/   建模階段才會產生內容
```

## 重新產生

只需要 Python 3 與 Pillow，不需要 Blender：

```sh
python3 Environment_Transition_Kit/05_Scripts/kit_spec.py                 # 規格自我檢查
python3 Environment_Transition_Kit/05_Scripts/draw_three_views.py --out _work/v02   # 輸出到新資料夾
python3 Environment_Transition_Kit/05_Scripts/write_reports.py --manifest
```

腳本不會覆寫已存在的檔案；要重出請指定新的輸出資料夾或先移走舊版。

## 規格摘要

- 公尺、Z 向上、模組前進 +X、+Y 為行進方向左側、地面 Z = 0。
- 道路：路面 3.00 m＋兩側 0.75 m 收邊帶；直線 4 m；彎道中心線弧長 4 m（15°、30°）。
- 河岸：陸地 1 m、岸線、往水側 2 m 到坡腳 -1.00 m；示意水位 -0.80 m；陸地在行進方向左側。
- 橋頭：2 m 緩坡升到測試橋面 +0.15 m（寬 3 m）；不製作橋樑本體。
- 接頭誤差目標 ≤ 1 mm；接頭頂點由同一組斷面函數產生。詳見 `06_Reports/ASSUMPTIONS.md`。
