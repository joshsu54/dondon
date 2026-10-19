# 街道道具 11

依規劃「小鎮生活與場景整合」補齊街道生活道具。本批新增 **6 組可編輯 Blender 外觀原型、6 份 FBX、60 張 1024×1024 同源十視圖**，另有 5 張細節圖和 6 張建模設計圖；細節圖與設計圖不計入 60 張。6 件道具已擺上 TownLayout v004 的西街。

| 模型 | 尺寸／分件 |
| --- | --- |
| StoneWell／石井 | 井欄外徑 1.2 m、高 0.75 m，石塊逐顆分件；石台座 Ø1.8 m；轆轤、右側搖把、繩圈、吊桶；兩坡小瓦頂，總高 2.5 m |
| WellBucket／木水桶 | 口徑 0.32 m、高 0.30 m；14 片桶板、兩道鐵箍、繩提把；與石井吊桶同一造型 |
| NoticeBoard／公告板 | 寬 2.0 m、高 2.55 m；石墩、雙柱、六片木板拼成的板面與框、4 張空白告示、小瓦頂 |
| WoodenCrate／木箱 | 0.6 × 0.45 × 0.5 m；三層側板、角柱、箱底，箱蓋為獨立物件，可疊放 |
| BambooBasket／竹簍 | 口徑 0.42 m、高 0.56 m；18 根竹骨、編圈、木底框、背面兩條背帶 |
| FirewoodStack／柴堆 | 1.8 × 0.8 × 1.3 m；7 層交錯劈柴（含木紋端面）、立柱、底軌、前低後高遮雨板 |

## 製作流程

1. **製圖**：`BlenderSource/street_specs.py` 記錄尺寸，`draw_street_sheets.py` 依同一份數值畫出正視、側視、俯視設計圖（`DesignSheets/`）。
2. **建模**：`build_street_props11.py` 讀取同一份尺寸建模，再從同一模型渲染 10 個固定角度。
3. **細節圖**：石井加井內俯視；水桶加內部與底面；竹簍加內部與背帶。檔名從 `11_` 起，記錄在 `views.json` 的 `extra_views`。

這批起把共用程式抽成兩個模組，之後的道具批次可以直接沿用：`prop_kit.py` 負責 Blender 建模基本形、FBX 匯出和十視圖渲染，`sheet_kit.py` 負責畫設計圖。

## 驗證

`verify_street11.py` 逐組重新開啟 `.blend` 並檢查以下各項，結果見 `validation.json`：
- 網格完整、原點在底部中心，外框符合設計尺寸。
- 石井井欄高度在 0.75～0.9 m 之間，吊桶高於井欄。
- 木箱的箱蓋是獨立物件，公告板有 4 張空白告示。
- FBX 重新匯入後網格數一致、外框誤差小於 1 mm。
- 十視圖與細節圖都可正常讀取，內容互不重複。

這些是 Blender 內的幾何檢查，UV／貼圖烘焙、碰撞、LOD 與 Unreal 匯入尚未完成。這批用 Blender 5.2.2 製作。

## 放進小鎮（TownLayout v004）

`BlenderSource/SpawnTown/build_town_layout_v004.py` 以 v003 為底，擺放位置寫在 `town_v004_specs.py`：
- 西巷南側新鋪井台，放石井和一個備用水桶。
- 巷口北側新鋪石坪，放公告板，面朝西街。
- 藥草攤旁放三個木箱（其中一個疊放）和一個竹簍。
- 食肆簷廊放一個竹簍。
- 食肆後門南側靠牆放柴堆。

建置時用 36 個射線點確認西巷與西街仍然暢通；每件道具底下都有支撐面（以 5 個射線點取樣），而且彼此不重疊。`verify_town_layout_v004.py` 會在存檔上重跑這些檢查，並比對 FBX 匯回結果（4614 個網格）。

## 重新生成

```sh
python3 BlenderSource/draw_street_sheets.py
blender --background --factory-startup -t 4 --python BlenderSource/build_street_props11.py
blender --background --factory-startup --python BlenderSource/verify_street11.py
python3 BlenderSource/publish_street11.py
```
