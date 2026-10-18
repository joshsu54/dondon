# 食肆用具 09

依 `BlenderSource/Planning/下一批素材與缺口_2026-10-15.md` 的「優先製作：食肆用具」補齊廚房與用餐區道具。本批新增 **8 組可編輯 Blender 外觀原型、8 份 FBX、80 張 1024×1024 同源十視圖**，另有 7 張內部／底面／開蓋細節圖和 8 張建模設計圖；細節圖與設計圖不計入 80 張。

| 模型 | 尺寸／分件 |
| --- | --- |
| CookingHearth／柴火爐灶 | 1.2 × 0.8 × 0.8 m；石台座、灰泥爐身、深色石板爐面、Ø500 mm 鍋口與鑄鐵承圈、拱形火口、柴薪與炭火、背面排煙口、備料木板 |
| IronWok／雙耳鐵鍋 | 口徑 550 mm、深 160 mm；球冠鍋身含 6 mm 內外壁、捲邊、雙環耳。可擱在爐灶承圈上 |
| BambooSteamer／竹蒸籠 | 直徑 400 mm；兩層籠身（各 90 mm）與編織籠蓋分件，籠底竹條與托梁 |
| PrepBoard／料理砧板 | 450 × 300 × 40 mm；30 mm 圓角、掛孔、刀痕與兩條墊腳 |
| CeramicBowl／粗陶碗 | 口徑 160 mm；內外壁與圈足，內側青釉。空碗，作為料理變體基底 |
| CeramicPlate／粗陶盤 | 直徑 240 mm；盤心與圈足，內側青釉 |
| DiningTable／食肆方桌 | 1.0 × 1.0 × 0.75 m；四片桌板、穿帶、桌腳、牙板與橫撐 |
| RoundStool／木圓凳 | 高 450 mm、座面 Ø320 mm；四支外撇凳腳、圓環橫撐 |

## 製作流程

1. **製圖**：`BlenderSource/kitchen_specs.py` 記錄所有尺寸；`draw_design_sheets.py` 依同一份數值畫出正視、側視、俯視設計圖（`DesignSheets/`）。碗、盤、鍋使用半剖面表示壁厚。這些是尺寸設計圖，並非 AI 概念繪圖。
2. **建模**：`build_kitchen_assets09.py` 讀取同一份尺寸，以 Blender 背景模式產生可編輯網格，匯出 `.blend`、`.fbx` 與 `model_info.json`，再從同一模型渲染 10 個固定角度。
3. **細節圖**：鐵鍋、碗、盤加出內部與底面圖；蒸籠加出開蓋與底面圖。檔名從 `11_` 起，記錄在 `views.json` 的 `extra_views`。

十視圖：前、右、後、左、右前、右後、左後、左前、正上方、高位正前方。正交投影，正面為 Blender −Y，單位公尺，原點在底部中心。

## 驗證

`verify_kitchen09.py` 逐組重新開啟 `.blend`，檢查非空網格、有限座標、底部中心原點、外框是否符合設計尺寸，並將 FBX 重新匯入比對網格數與外框（誤差 < 1 mm、不含攝影棚物件）。另檢查蒸籠兩層與籠蓋為獨立物件、鐵鍋口徑大於爐灶承圈。每張圖須為可解碼的 1024×1024 PNG，同組圖片內容互不相同。結果見 `validation.json`。

這些是 Blender 內的幾何檢查。UV／貼圖烘焙、碰撞、LOD 與 Unreal 匯入均尚未完成；程序凹凸與炭火自發光材質不等於遊戲貼圖。

## 重新生成

```sh
blender --background --factory-startup -t 4 --python BlenderSource/build_kitchen_assets09.py   # 可在 -- 後指定素材 ID
blender --background --factory-startup --python BlenderSource/verify_kitchen09.py
python3 BlenderSource/draw_design_sheets.py
python3 BlenderSource/publish_kitchen09.py   # 合併到專案 Models／素材庫並更新索引
```

已有 `views.json` 的素材會跳過；要重建請先刪除該素材的 Turnarounds 資料夾。

## 後續

- 食肆／客棧建築：一樓門面、廚房與用餐區，使用本批爐灶與桌凳配置。
- 料理成品：米飯、湯麵、蒸點、魚肉，以粗陶碗盤與蒸籠為容器。
- 竹簍、柴堆、水缸、碗櫃等廚房周邊道具。
