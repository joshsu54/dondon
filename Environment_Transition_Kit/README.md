# Environment Transition Kit v01｜半寫實仙俠環境收邊模組包

這是 29 件可以重複拼接的獨立收邊模組：道路不規則收邊（A 類，11 件）、河岸自然收邊（B 類，10 件）、橋頭與地形交接收邊（C 類，8 件）。依《Claude 專用完整任務書｜半寫實仙俠環境收邊模組包》製作。

**受保護資產：未修改。** 本環境中沒有樹伴古樹、山兔或主世界的 `.blend`，本專案也不讀取、連結或改動它們。所有檔案只寫在本資料夾內（交付前已用唯讀方式複查，見 `06_Reports/PHASE6_ProtectedAssetRecheck.json`）。

## 先看這些

| 想看什麼 | 檔案 |
| --- | --- |
| 拼起來的樣子（有中文標註） | `04_Previews/Showcase/showcase_v01_hero_labels.png`、`_bridgehead_labels.png`、`_river_labels.png` |
| 接縫有沒有裂縫（近距離特寫） | `04_Previews/Showcase/showcase_v01_seam_*_labels.png` |
| 29 件一覽 | `04_Previews/Sheets/Sheet_A_RoadEdge.png`、`Sheet_B_Riverbank.png`、`Sheet_C_Bridgehead.png` |
| 每件 11 個角度 | `04_Previews/Individual/<編號>_<ID>/`，或用瀏覽器開 `04_Previews/index.html` |
| 檢查結果（白話＋數字） | `06_Reports/QA_Report.md` |
| 引擎匯入 | `06_Reports/README_Integration.md` |

## 交付內容

```
00_References/   REF_A–F（模組總表、正交工程圖、接頭工程圖、材質）、29 張設計三視圖
01_Blender/      road_edge_modules_v01.blend、riverbank_modules_v01.blend、bridgehead_modules_v01.blend
                 （每件一個 Collection；含 LOD0/1/2、細節、碰撞代理、測試物件 COL_TEST_Only）
02_Exports/      RoadEdge/ 11、Riverbank/ 10、Bridgehead/ 8 個 FBX；_TestHelpers/ 尺度與拼接測試用
03_Textures/     共用 PBR 貼圖（1024²，可無縫平鋪）、草片、混合雜訊、水面波紋法線
04_Previews/     Individual（每件 10 正交＋1 透視、views/model_info/validation.json）、Sheets、
                 AssemblyTests（自動檢查用拼裝）、Showcase（展示場景與接縫特寫）、Materials、index.html
05_Scripts/      全部生成、檢查、匯出、出圖腳本（build_all.sh 依序執行）
06_Reports/      ASSET_MANIFEST、CONNECTOR_SPEC.json、QA_Report、ASSUMPTIONS、README_Integration、
                 PHASE0／PHASE6 安全檢查、qa/（所有檢查的原始 JSON）、history/（設計階段舊版清單）
```

## 規格摘要

- 公尺、Z 向上、模組行進方向 +X、+Y 為行進方向左側、地面 Z = 0。
- 道路：路面 3.00 m＋兩側 0.75 m 收邊帶；直線 4 m；彎道中心線弧長 4 m（15°、30°）。
- 河岸：陸地 1 m、岸線、往水側 2 m 到坡腳 -1.00 m；測試水位 -0.80 m；陸地在行進方向左側。
- 橋頭：2 m 緩坡升到測試橋面 +0.15 m（寬 3 m）；不製作橋梁本體。
- 接頭誤差目標 ≤ 1 mm（實測見 QA 報告）。所有數值的唯一來源是 `05_Scripts/kit_spec.py`；其他假設見 `06_Reports/ASSUMPTIONS.md`。

## 重新產生

需要 Blender 5.2（背景模式）與 Python 3＋Pillow。所有腳本都不覆寫既有檔案；重出前請先把舊成果移走或改用新版本號。

```sh
BLENDER=/path/to/blender Environment_Transition_Kit/05_Scripts/build_all.sh      # 貼圖→建模→檢查→FBX→出圖
python3 Environment_Transition_Kit/05_Scripts/write_final_reports.py --reports    # 看過總表後產生報告
```

## 還沒做的

Unity／Unreal 實際匯入與材質重建、引擎內碰撞與行走測試、手機效能實測、登錄到專案 ArtLibrary（任務書限制只寫本資料夾）。詳見 `06_Reports/QA_Report.md` 第 5 節。
