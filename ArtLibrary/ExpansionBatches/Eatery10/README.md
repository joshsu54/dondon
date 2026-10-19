# 食肆客棧 10

依規劃「後續順序 1：食肆／客棧建築」製作。本批新增 **1 組兩層建築（Eatery／食肆客棧）**，包含 `.blend`、FBX、10 張 1024×1024 同源十視圖、4 張配置剖視圖和 2 張建模設計圖。剖視圖與設計圖不計入十視圖。

## 製作流程

這次沒有 AI 概念圖，流程是先畫設計圖，再建模：

1. **製圖**：`BlenderSource/eatery_specs.py` 記錄所有尺寸與配置；`draw_eatery_sheets.py` 依同一份數值畫出正立面、右側立面、一樓平面、二樓平面（`DesignSheets/`）。
2. **建模**：`build_eatery10.py` 讀取同一份數值建出可編輯網格，並從 KitchenWare09 的 `.blend` 附加家具複本擺進一樓。

另有 `ArtReferences/Eatery_10Views/prompts.json` 的生圖提示詞，可日後補 AI 概念圖對照。

## 內容

| 部分 | 規格 |
| --- | --- |
| 量體 | 主體 10 × 7 m，前簷廊／陽台深 1.5 m；石台 0.45 m；一樓樓高 3.4 m；二樓牆高 2.8 m；雙坡曲面瓦頂，屋脊約 8.9 m |
| 一樓 | 正面兩開間摺門全開（淨高 2.6 m）、兩側格窗；用餐區 4 張方桌 16 張圓凳；櫃台與酒架；東北角廚房（隔間、送菜窗口、後門） |
| 廚房 | KitchenWare09 柴火爐灶靠煙囪擺放，鐵鍋坐在承圈上，蒸籠放在備料板上；磚砌煙囪穿出屋頂 |
| 樓梯 | 西牆直跑，17 級 × 0.20 m，踏面 0.22 m，寬 1.0 m；樓梯開口確保下方最小淨高 2.0 m；開口側有扶手 |
| 二樓 | 三間朝南客房（各有床鋪）、北側走廊；中間客房有格子門通往陽台 |
| 外觀 | 前簷廊立柱與斜撐、陽台欄杆、空白招牌、兩盞紅燈籠、山牆木構與屋脊翹角 |

物件分在 `01_Editable_Asset` 下的群組：Foundation、Frame／Frame_Upper、Walls_Ground／Walls_Upper、Floor_Upper、Stair、Counter、Kitchen、Doors、Veranda、Balcony、Signage、Roof。剖視圖靠隱藏 Roof、Walls_Upper 等群組產生。

**FBX 只含建築本體**。家具在 `.blend` 的 `30_Furnishing_KitchenWare09`，是 KitchenWare09 的複本，用來看配置；原始道具仍在各自的 `Models/<道具>/v001`。

原點在石台（含簷廊）底部中心，正面為 Blender −Y，單位公尺。屋簷與前台階超出石台範圍。

## 驗證

`verify_eatery10.py` 會重新開啟 `.blend` 並逐項檢查：

- 原點位於石台底部中心。
- 樓梯為 17 級 0.20 m，最上一級與二樓地面齊平。
- 樓梯每一級上方淨高至少 2.0 m（樓板與梁）。
- 正面開口淨高 2.6 m，煙囪高出屋面。
- 家具數量正確，鐵鍋坐在爐灶承圈上。
- FBX 重新匯入後網格數一致、外框誤差小於 1 mm，且不含相機與燈光。
- 十視圖與剖視圖都是 1024×1024，內容互不相同。

結果見 `validation.json`。

製作中，這項檢查抓到第一版樓梯下方淨高只有 1.6 m，已加大樓梯開口並移動二樓走廊牆修正。

以上是 Blender 內的幾何檢查，不等於角色控制器或 Unreal 通行測試。UV／貼圖烘焙、碰撞、LOD、導航網格、門窗開合與室內燈光都尚未完成。

## 重新生成

```sh
python3 BlenderSource/draw_eatery_sheets.py
blender --background --factory-startup -t 4 --python BlenderSource/build_eatery10.py   # 需先有 KitchenWare09 的 Models
blender --background --factory-startup --python BlenderSource/verify_eatery10.py
python3 BlenderSource/publish_eatery10.py
```
