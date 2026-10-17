# 小鎮道路庭院 11

小鎮待辦的第三批：道路接頭、坡路、石拱橋、欄杆、荷花池，以及原本只在組合場景裡的出生石台與小鎮牌樓，共 10 組。**每件都先產生 10 張不同角度的概念圖，再進 Blender 建模**。

| 模型 | 規格 |
| --- | --- |
| 青石路 T 字路口／TownRoadTJunction | 6 x 6 x 0.2 m; open edges at west, east and north. |
| 青石路十字路口／TownRoadCrossroad | 6 x 6 x 0.2 m; open edges on all four sides. |
| 青石路彎道／TownRoadCurve | 6 x 6 x 0.2 m; open edges at south and east. |
| 青石坡路／TownRoadSlope | 3.5 x 6 x 0.8 m; south edge at 0.2 m, north edge at 0.8 m. |
| 石拱橋／StoneArchBridge | Approx. 9.6 x 2.8 x 2.6 m; deck crown 1.45 m above the ends. |
| 木欄杆段／TimberRailing | 2.1 x 0.2 x 1.23 m; posts at x = +/-1.0 m for tiling. |
| 石欄杆段／StoneRailing | 2.2 x 0.3 x 1.3 m; posts at x = +/-1.0 m for tiling. |
| 荷花池／PondEdge | Approx. 5.2 x 3.8 m; water surface 0.22 m above the bed. |
| 出生石台／SpawnAltar | Approx. 3.5 x 4.3 x 1.9 m. |
| 小鎮牌樓／TownPaifang | Approx. 8.2 x 1.8 x 5.9 m; centre opening 2.3 m wide. |

## 製作流程

1. 每件素材先寫提示詞（含 10 個角度的描述）與設計規格：`BlenderSource/TownLife09/town11_shapes.py`。
2. **建模前**先依規格在暫存場景排出草模，以接近 Codex image_gen 概念圖的柔光棚拍風格（淺灰背景、暖色主光、接地陰影、透視鏡頭）渲染十個角度，存放在 `ArtReferences/<素材>_10Views/`，提示詞記錄在同資料夾的 `prompts.json`。
   雲端環境沒有 AI 生圖模型，這些不是 AI 繪圖；提示詞可在之後交給生圖工具重新產生。
3. Blender 開新檔，把十張概念圖放進 `80_Concept_References` 集合當參考圖（不渲染、不匯出），再完整建模：倒角、材質與細節零件都在這一步加入。
4. 匯出 FBX，並從同一模型渲染 10 張 1024 × 1024 固定角度圖到 `ArtLibrary/Turnarounds/<素材>_v001/`。
5. 重新開檔、FBX 回匯核對尺寸與物件數；結果記錄在 `validation.json`。

總覽：`concepts/*_concept_10views.jpg` 是建模前概念圖，`*_10views.jpg` 是建模後的同模型十視圖。模型在專案 `Models/<素材>/v001/`，不另複製到本資料夾。重跑：`TL_SPEC=town11_shapes BlenderSource/TownLife09/run_all09.sh`。

## 道路接頭規格

道路方塊為 6 × 6 m，路面寬 3 m、路緣石寬 0.25 m，路面高 0.2 m，與 MountainStonePath 同寬。每件的 `model_info.json` 記錄 `connectors`（開口邊中點、路面高度，以底部中心原點為準），方塊可邊對邊拼接；彎道從南邊轉到東邊，坡路往北升高 0.6 m。

## 其他

- 石拱橋跨距 8 m，橋面頂比兩端高約 1.45 m；兩端接口在 (±4, 0, 0.28) m。
- 木欄杆、石欄杆都是 2 m 一段，柱心在 x = ±1.0 m，可連續排列。
- 出生石台與小鎮牌樓是新建的獨立版本，造型和 SpawnTown 組合場景內的原件不同，可替換使用。

## 尚未完成

UV／貼圖烘焙、碰撞、LOD、導航網格與 Unreal 匯入驗證都還沒做；荷花池水面沒有動態，出生石台靈石沒有發光與浮動特效。
