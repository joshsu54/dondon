# Claude Code 交接｜2026-10-17

## 專案與下載

- GitHub：<https://github.com/joshsu54/dondon>
- 最新分支：`solid-clouds-karst-peaks`。交接前素材提交為 `44cb796`；本次交接文件另有提交，Release tag 鎖定完整交接快照。
- 複製版本庫：安裝 Git LFS，執行 `git clone --branch solid-clouds-karst-peaks https://github.com/joshsu54/dondon.git`，進入目錄後 `git lfs pull`、`git lfs fsck`。
- 也可下載 Release 全部分卷、`handoff-manifest.json`、`restore_handoff.py`，依 `DOWNLOAD.md` 還原。這種方式含實際二進位檔，但不含 .git 歷史；需要後續推送時優先使用 Git clone。

## 已完成內容

素材索引共 **66 組獨立素材、660 張基本角度圖、3 個配置場景**，另有多個歷史版本、額外預覽與風動影片。這是外觀原型素材庫，不是已可遊玩的完整開放世界專案。

| 內容 | 路徑／版本 | 狀態 |
| --- | --- | --- |
| 最新山景總場景 | Models/MountainSanctuary/v004 | 已替換實體雲、喀斯特山峰；四張場景預覽與靜態 FBX |
| 原登山步道 | Models/MountainSanctuary/v002 | 33 個路線模組、升高 48 m；歷史版本保留 |
| 凌雲孤峰、連綿山脊 | Models/CloudpiercerPeak/v002、Models/MountainRidge/v002 | 新版石柱型山峰；v001 保留 |
| 風動與實體雲 | Effects/WindFog/v002 | Blender 96 幀循環，4 秒／12fps 影片；非流體模擬 |
| 水景批次 09 | ArtLibrary/ExpansionBatches/MountainWaters09 | 瀑布、彎曲山溪、靈泉：3 組／30 圖；水為靜態幾何 |
| 山路設施 10 | ArtLibrary/ExpansionBatches/MountainWayside10 | 六角休憩亭、拱形石橋、獨立欄杆：3 組／30 圖，另有亭內預覽 |
| 宗門、商鋪、道具等 | ArtLibrary/asset_catalog.json | 其餘登錄素材與圖庫入口 |
| 故事 | Story/ | 序章、第一章大綱與 Word 劇本，尚未據此完成整套角色／動畫 |

## 重要版本差異與限制

1. 圖庫索引及部分歷史 README 仍指向 MountainSanctuary v002、山峰 v001、WindFog v001；不能把「索引目前選用」與「目錄內最新版本」視為相同。先核對 v004／v002 的內容及已有 validation，再決定是否切換索引，保留舊版連結。
2. `build_peaks_v002.py` 已修正山頂環高度遞增、`build_solid_clouds_v002.py` 已修正匯入時還原 sys.argv。這些修正已提交，但現有二進位是否由修正後腳本重建未另行證明，不能宣稱完全可重現；應在新版本或隔離輸出目錄重建比較。
3. 新增水景與山路設施尚未放入山景總場景。石橋長 9 m、淨寬 2.98 m、最高橋面 2.1 m；最大坡度約 35°，加入角色前需調整坡度或加階梯並驗證通行。
4. FBX 只保留靜態幾何與基本材質色；程序材質、雲漂移、植被形態鍵動畫並非已完成 Unreal 移植。
5. UV／貼圖烘焙、碰撞、LOD、導航及 Unreal 實際匯入尚未完成。石欄杆重複排列需整理端柱與接縫。
6. 批次 09／10 的本機安裝腳本在忽略的 work 內，不在交接來源中；已有成品、建模與驗證腳本均已交付。接下來新增批次應把安裝／圖庫更新流程寫成版本化工具。

## 目錄

- `ArtLibrary/index.html`：本機圖庫；`完整建模清單.md`：需求與尚缺項目。
- `ArtLibrary/ExpansionBatches/<batch>/BlenderSource/`：各批次 Blender 生成／驗證腳本。
- `Models/<asset>/vNNN/`：可編輯原檔、FBX、模型資料。
- `ArtLibrary/Turnarounds/<asset>_vNNN/`：十視圖與相機紀錄。
- `BlenderSource/`：較早期模型與動畫腳本。
- `Effects/`：風動雲霧；`ArtReferences/`：概念圖，不能當作同模型十視圖。
- `Deliverables/`：歷史完整批次 ZIP；交接 Release 也保留這些檔案。
- `Assets/`：Unity 歷史原型，不是目前 Unreal 專案。
- `Tools/BlenderMCP/`：既有 MCP 安裝記錄及鎖定需求；本機 .venv 與帳號設定不包含在包內。

## 環境與驗證

原機使用 macOS arm64、Blender 5.3.0 Beta（建置 98f8f23151d3），Python 腳本主要依賴 Blender 內建 bpy。尚未驗證其他 Blender 版本。`Tools/bin/blender` 是原機絕對路徑捷徑，在別台機器請改用實際的 `blender` 執行檔。讀圖／製作總覽時可使用 Pillow，但唯讀交接檢查僅需 Python 3.9+ 標準函式庫。

```sh
# 唯讀：索引、實際檔案、十視圖、LFS 指標與本地網頁連結
python3 Tools/Handoff/verify_project.py

# 重新開檔及 FBX 回匯驗證（會寫回批次 validation.json）
blender --background --python-exit-code 1 --python ArtLibrary/ExpansionBatches/MountainWaters09/BlenderSource/verify_waters09.py
blender --background --python-exit-code 1 --python ArtLibrary/ExpansionBatches/MountainWayside10/BlenderSource/verify_wayside10.py
```

批次 09／10 建模腳本遇到 views.json 會跳過該資產；不要為了強制重建而直接刪除正式成果。新建 v002 或改到獨立輸出路徑，再驗證、渲染、回匯與安裝。CLI 使用 `--python-exit-code 1`，避免 Blender Python 失敗但程序回傳 0。

## 建議接續順序

1. 跑唯讀盤點、閱讀最近 validation，回報實際現況與版本差異。
2. 優先整理新版山峰／實體雲的圖庫索引，先核對原檔及十視圖，不要直接改計數。
3. 在新的山景版本配置水景、休憩亭、石橋與欄杆；處理橋坡、岸線、入口高度與接縫。
4. 再依完整建模清單補竹林／灌木、秘境入口、小鎮水井／公告板等缺件；每件至少十視圖。
5. 美術原型確認後，另做 UV、材質烘焙、碰撞、LOD 與 Unreal 驗收。

## 可直接交給 Claude Code 的開場指令

> 請接手這個修仙 Blender 美術專案。先讀 CLAUDE.md、HANDOFF.md 與 ArtLibrary/完整建模清單.md，執行 python3 Tools/Handoff/verify_project.py，核對 git status。用繁體中文說明盤點結果，再從新版山峰／實體雲索引差異與山景設施整合接續工作。保留既有版本；每個獨立新素材必須有可編輯 Blender、FBX 和至少十個不同角度的同模型渲染圖。不要把外觀原型標成已通過 Unreal 驗證。
