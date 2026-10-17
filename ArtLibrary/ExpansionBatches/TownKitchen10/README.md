# 小鎮廚房 10

小鎮待辦的第二批：食肆用的料理道具、碗盤、米糧與食材，加上籬笆轉角段，共 9 組。**每件都先產生 10 張不同角度的概念圖，再進 Blender 建模**。

| 模型 | 規格 |
| --- | --- |
| 鐵鍋／CookingWok | Wok 0.72 m across; set approx. 0.9 x 1.0 x 0.45 m. |
| 蒸籠／BambooSteamer | Steamer 0.43 m across, 0.37 m tall; set approx. 0.6 x 0.45 m. |
| 雙灶爐台／BrickStove | 1.7 x 0.95 m body, 0.86 m working height, chimney to 2.2 m. |
| 砧板台／ChoppingBlock | 0.52 m across, 0.8 m working height. |
| 碗盤茶具組／TablewareSet | Tray 0.62 x 0.42 m; teapot 0.14 m tall. |
| 米糧麻袋／GrainSacks | Approx. 1.0 x 0.9 x 0.65 m; each sack 0.8 m long. |
| 竹籬笆轉角段／BambooFenceCorner | 1.1 x 1.1 x 1.35 m; arm ends at (-1, 0) and (0, +1) m for tiling with BambooFence. |
| 料理成品拼盤／FoodPlatter | Tray 0.76 m across; tallest item 0.13 m. |
| 食材木箱／IngredientCrate | 0.9 x 0.6 x 0.28 m crate; approx. 0.35 m tall with produce. |

## 製作流程

1. 每件素材先寫提示詞（含 10 個角度的描述）與設計規格：`BlenderSource/TownLife09/town10_shapes.py`。
2. **建模前**先依規格在暫存場景排出草模，以接近 Codex image_gen 概念圖的柔光棚拍風格（淺灰背景、暖色主光、接地陰影、透視鏡頭）渲染十個角度，存放在 `ArtReferences/<素材>_10Views/`，提示詞記錄在同資料夾的 `prompts.json`。
   雲端環境沒有 AI 生圖模型，這些不是 AI 繪圖；提示詞可在之後交給生圖工具重新產生。
3. Blender 開新檔，把十張概念圖放進 `80_Concept_References` 集合當參考圖（不渲染、不匯出），再完整建模：倒角、材質與細節零件都在這一步加入。
4. 匯出 FBX，並從同一模型渲染 10 張 1024 × 1024 固定角度圖到 `ArtLibrary/Turnarounds/<素材>_v001/`。
5. 重新開檔、FBX 回匯核對尺寸與物件數；結果記錄在 `validation.json`。

總覽：`concepts/*_concept_10views.jpg` 是建模前概念圖，`*_10views.jpg` 是建模後的同模型十視圖。模型在專案 `Models/<素材>/v001/`，不另複製到本資料夾。重跑：`TL_SPEC=town10_shapes BlenderSource/TownLife09/run_all09.sh`。

## 內容

- 料理道具：鐵鍋（含鍋架、鍋鏟、木鍋蓋）、三層蒸籠、雙灶爐台、砧板台、碗盤茶具組。
- 料理成品：清蒸魚、白飯、饅頭、青菜、湯，放在同一個漆盤上；可拆成單品使用。
- 食材：米糧麻袋（開口袋裝米）、食材木箱（白菜、白蘿蔔、紅蘿蔔、整條魚）。
- 竹籬笆轉角段可接 TownLife09 的 BambooFence：兩臂端點在 (-1, 0) 與 (0, +1) m。

## 尚未完成

UV／貼圖烘焙、碰撞、LOD 與 Unreal 匯入驗證都還沒做。爐火、蒸氣、湯面熱氣等特效未製作；食物是外觀模型，沒有烹飪狀態變化。
