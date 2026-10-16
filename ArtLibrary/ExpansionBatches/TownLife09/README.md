# 小鎮生活 09

小鎮待辦的第一批：八件生活道具與一棟食肆客棧，共 9 組。**每件都先產生 10 張不同角度的概念圖，再進 Blender 建模**。

| 模型 | 規格 |
| --- | --- |
| 小鎮水井／TownWell | Approx. 2.5 x 2.1 x 3.2 m; stone ring 1.8 m across, rim 0.9 m high. |
| 小鎮公告板／NoticeBoard | Approx. 2.9 x 1.0 x 2.9 m; board face 2.2 x 1.2 m. |
| 竹簍／BambooBasket | Approx. 0.6 x 0.6 x 0.67 m. |
| 木箱／WoodenCrate | Approx. 0.72 x 0.76 x 0.74 m. |
| 陶罐／ClayJar | Approx. 0.6 x 0.6 x 0.74 m. |
| 柴堆／FirewoodStack | Approx. 2.0 x 0.8 x 1.1 m. |
| 竹籬笆段／BambooFence | 2.1 x 0.2 x 1.3 m; posts at x = +/-1.0 m for tiling. |
| 籬笆院門／FenceGate | Approx. 2.9 x 0.9 x 2.8 m; clear opening 1.9 m wide, 2.1 m high. |
| 食肆客棧／TownInn | Approx. 13.8 x 13 x 9.6 m; floor-to-floor 3.4 m; stair 17 risers of 0.2 m. |

## 製作流程

1. 每件素材先寫提示詞（含 10 個角度的描述）與設計規格：`BlenderSource/TownLife09/town09_shapes.py`。
2. **建模前**先依規格繪製十個角度的墨線上色概念圖，存放在 `ArtReferences/<素材>_10Views/`，提示詞記錄在同資料夾的 `prompts.json`。
   雲端環境沒有 AI 生圖模型，這些是程式繪製的概念草圖（不是 AI 繪圖、也不是模型渲染），提示詞可在之後交給生圖工具重新產生。
3. Blender 開新檔，把十張概念圖放進 `80_Concept_References` 集合當參考圖（不渲染、不匯出），再完整建模：倒角、材質、瓦壟、編織帶、格柵等細節零件都在這一步加入。
4. 匯出 FBX，並從同一模型渲染 10 張 1024 × 1024 固定角度圖到 `ArtLibrary/Turnarounds/<素材>_v001/`。
5. 重新開檔、FBX 回匯核對尺寸與物件數；結果記錄在 `validation.json`。

總覽：`concepts/*_concept_10views.jpg` 是建模前概念圖，`*_10views.jpg` 是建模後的同模型十視圖。模型在專案 `Models/<素材>/v001/`，不另複製到本資料夾。

## 客棧內容

一樓前半部是食堂（五張方桌、十張長凳），右後方是櫃台與酒架，左後方是 17 級直跑樓梯（每級高 0.2 m），通往二樓開口。二樓有前方走廊、陽台，以及後方三間客房（兩間單床、一間小床）。後方加建單坡廚房，內有雙灶爐、兩口鐵鍋、煙囪、砧板桌與水缸。招牌為空白牌匾，不含文字。

## 尚未完成

UV／貼圖烘焙、碰撞、LOD 與 Unreal 匯入驗證都還沒做。客棧門窗不能開合，水井轆轤、院門門扇也沒有動畫；食肆的鍋碗、食材等料理道具仍待下一批。
