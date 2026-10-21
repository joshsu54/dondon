# 生鮮食材 13

依清單「米、蔬菜、魚肉」補齊食材，可放進廚房、攤位與街道。本批新增 **6 組可編輯 Blender 外觀原型、6 份 FBX、60 張 1024×1024 同源十視圖**，以及 6 張建模設計圖。

| 模型 | 容器 | 內容 |
| --- | --- | --- |
| RiceSack／米袋 | 無（新建） | 麻布米袋，袋身有隨機皺褶與縫線；袋口反折，露出米面；插一支木米勺 |
| CuredMeatRack／臘肉吊架 | 無（新建） | 0.9 m 寬的 A 字木架；4 條分皮、肥、瘦三層的臘肉，3 串臘腸 |
| RadishCrate／蘿蔔木箱 | 街道道具 11 木箱（去掉箱蓋） | 10 根白蘿蔔分兩排從箱壁斜靠向中間，葉子露出箱口；另有 3 根紅蘿蔔 |
| VegetableBasket／蔬菜籃 | 竹簍壓低成淺籃（0.4 倍高），去掉背帶 | 2 顆大白菜、4 根紅蘿蔔、一束綁好的青蔥 |
| EggBasket／蛋籃 | 竹簍縮小成小淺籃 | 籃底鋪乾草，放 14 顆深淺兩色的蛋 |
| FishTub／鮮魚木盆 | 木水桶放寬 1.7 倍、壓低成淺盆，去掉提把 | 盆中有水面，3 條鯉魚半浮在水中 |

## 製作流程與共用工具

1. **製圖**：`fresh_specs.py` 記錄尺寸、容器與縮放比例，`draw_fresh_sheets.py` 依同一份數值畫出設計圖。
2. **建模**：`build_fresh13.py` 讀取同一份數值建模，並從同一模型渲染十視圖。

這批把附加容器、圓頂、葉片、管狀物、橢球等工具函式移進共用的 `prop_kit.py`，之後的批次可以直接沿用。

**不等比縮放的處理**：容器若做了不等比縮放（例如竹簍壓低成淺籃），會把縮放直接套進網格資料，原本的比例記在容器空物件的 `baked_scale` 屬性。原因是竹骨等物件本身有旋轉，疊上不等比縮放後會產生 FBX 無法表示的斜切變形，第一次驗證時 FBX 外框差了 12 mm。

## 驗證

`verify_fresh13.py` 逐組重新開啟 `.blend` 並檢查，結果見 `validation.json`：
- 原點位於底部中心。
- 米袋與吊架的外框符合設計尺寸。
- 有容器的 4 件：容器比例正確，蔬果都在容器範圍內，並高於容器底；向外散開的葉子與青蔥不在此限。
- FBX 重新匯入後網格數一致，外框誤差小於 1 mm。
- 十視圖可讀取且彼此不同，設計圖存在。

製作中修正了兩件：
- 蘿蔔原本傾斜方向寫錯，根部穿出箱子側面。
- 蔬菜籃的紅蘿蔔原本有一端伸出籃外。

UV、貼圖烘焙、LOD 與 Unreal 匯入都尚未完成。這批用 Blender 5.2.2 製作。

## 重新生成

```sh
python3 BlenderSource/draw_fresh_sheets.py
blender --background --factory-startup -t 4 --python BlenderSource/build_fresh13.py   # 需先有 StreetProps11 的 Models
blender --background --factory-startup --python BlenderSource/verify_fresh13.py
python3 BlenderSource/publish_fresh13.py
```
