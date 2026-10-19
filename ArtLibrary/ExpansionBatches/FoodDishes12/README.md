# 料理成品 12

依清單「米、蔬菜、魚肉、料理成品」製作第一批成品菜。本批新增 **6 組可編輯 Blender 外觀原型、6 份 FBX、60 張 1024×1024 同源十視圖**、6 張建模設計圖，另有 1 張餐桌預覽圖。設計圖和預覽圖不計入 60 張。

| 模型 | 容器 | 內容 |
| --- | --- | --- |
| RiceBowl／白米飯 | 粗陶碗 | 高出碗口約 26 mm 的圓丘白飯，米粒用材質凹凸表現 |
| NoodleSoup／湯麵 | 粗陶碗放大 1.35 倍（高 1.25 倍） | 湯面、捲麵、兩片叉燒、半顆蛋、青菜、蔥花，筷子架在碗口 |
| SteamedBuns／蒸籠包子 | 竹蒸籠下層（不含上層和蓋子） | 7 顆有摺紋的包子 |
| SteamedFish／清蒸魚 | 粗陶盤拉成 384 × 252 mm 橢圓盤 | 整條魚（尾、背鰭、眼、刀紋），醬汁鋪底，上面放蔥絲和薑絲 |
| StirFryGreens／炒青菜 | 粗陶盤 | 兩層青江菜葉、菜梗、蒜末 |
| BraisedPork／紅燒肉 | 粗陶碗 | 9 塊分成瘦肉、肥肉、豬皮三層的五花肉，泡在醬汁裡，上面放蔥段 |

## 容器與食物的關係

容器不是重新建模，而是從 `Models/<容器>/v001` 附加 KitchenWare09 的原始物件，放在 `Container_<容器>` 空物件底下；需要放大或拉長時只縮放這個空物件。食物網格直接放在根物件下，可以單獨修改。之後若要改容器造型，請改 KitchenWare09 的原始素材再重建本批。

FBX 同時包含容器和食物。原點在容器底部中心，正面為 Blender −Y。

## 製作流程

1. **製圖**：`food_specs.py` 記錄容器、縮放比例和食物尺寸，`draw_food_sheets.py` 依同一份數值畫出含容器半剖面的設計圖。
2. **建模**：`build_food_dishes12.py` 附加容器、建立食物，再從同一模型渲染十視圖。全部跑完後，會把 6 道菜擺上 KitchenWare09 的方桌，輸出 `table_setting_preview.png` 和 `.blend`。
3. 共用的 `prop_kit.py` 本批做了一處修正：置中時只移動根物件的第一層子物件，避免縮放過的容器和食物錯位。這個改動不影響 StreetProps11 的結果。

## 驗證

`verify_food12.py` 逐組重新開啟 `.blend` 並檢查以下項目，結果見 `validation.json`：
- 原點位於底部中心。
- 容器縮放比例正確，蒸籠沒有帶入上層和蓋子。
- 除了架在碗口的筷子，食物都在容器輪廓內，而且底部高於容器底、頂部露出容器。
- FBX 重新匯入後網格數一致，外框誤差小於 1 mm。
- 十視圖可讀取且彼此不同，設計圖存在。

製作過程中調整過三項：
- 白飯原本太光滑，加強了材質凹凸。
- 紅燒肉的蔥段原本浮在肉上，改為貼在上層肉塊頂面。
- 餐桌預覽原本燈光過亮，調暗後重新出圖。

這些是 Blender 內的檢查。UV、貼圖烘焙、LOD 與 Unreal 匯入都尚未完成；湯汁和醬汁只是光滑材質，沒有做液體模擬。這批用 Blender 5.2.2 製作。

## 重新生成

```sh
python3 BlenderSource/draw_food_sheets.py
blender --background --factory-startup -t 4 --python BlenderSource/build_food_dishes12.py   # 需先有 KitchenWare09 的 Models
blender --background --factory-startup --python BlenderSource/verify_food12.py
python3 BlenderSource/publish_food12.py
```
