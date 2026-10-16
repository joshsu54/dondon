# dondon 專案規則

## 建模流程（必須遵守）

**每次用 Blender 建模之前，先產生 10 張不同角度的概念參考圖。**

1. 先為素材寫提示詞與設計規格（造型、尺寸、材質、10 個角度的描述）。
2. 產生 10 張建模前概念圖，存到 `ArtReferences/<素材>_10Views/`，角度依序為：
   `01_front`、`02_right`、`03_rear`、`04_left`、`05_front_right`、`06_rear_right`、`07_rear_left`、`08_front_left`、`09_top`、`10_high_front`；
   同資料夾附 `prompts.json`（每張圖的提示詞）與 `README.md`。有 AI 生圖工具時用提示詞生圖；沒有時（例如雲端環境）用 `BlenderSource/TownLife09/concept_sketch09.py` 的方式依規格繪製，並在 README 註明。
3. 建模時把這 10 張圖載入 .blend 的 `80_Concept_References` 集合當參考（不渲染、不匯出）。
4. 建模完成後再從同一模型渲染 10 張 1024 × 1024 十視圖到 `ArtLibrary/Turnarounds/<素材>_vNNN/`，並重新開檔、FBX 回匯驗證。

範例批次：`BlenderSource/TownLife09/`（說明見 `ArtLibrary/ExpansionBatches/TownLife09/README.md`）。

## 慣例

- 單位公尺、Z 向上、正面為 Blender -Y、原點在底部中心。
- `.blend`、`.fbx`、圖片走 Git LFS（見 `.gitattributes`）。
- 雲端環境可用 `pip install bpy==5.2.2` 取得 Blender（Python 3.13）；本機 Mac 用 `Tools/bin/blender`。
- 所有原型都尚未經 Unreal 匯入驗證，不要標成「遊戲可用」。
