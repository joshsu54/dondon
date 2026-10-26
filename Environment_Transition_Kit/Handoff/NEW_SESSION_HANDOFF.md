# 新對話交接：環境收邊模組包 → 《雲境》任務 B

日期：2026-10-26。這份文件是給**下一個 Claude 對話**看的，裡面寫了今天做了什麼、檔案在哪、接下來要做什麼，以及必須遵守的規定。

---

## 0. 給使用者：怎麼開新對話

1. **先讓新對話能動《雲境》儲存庫。**《雲境》屬於 z1nnz 的帳號，所以要由 z1nnz（或該儲存庫的管理者）在 GitHub 把 Claude 應用程式安裝到 `z1nnz/yun-jing-rpg`：<https://github.com/apps/claude/installations/select_target>。你自己的 Claude 設定目前只授權了 `joshsu54/dondon`，這就是今天上傳不了的原因。
2. 開新的 Claude Code 雲端對話，儲存庫**兩個都選**：`z1nnz/yun-jing-rpg` 和 `joshsu54/dondon`。
3. 第一句貼這段：

> 請先讀 `joshsu54/dondon` 分支 `claude/environment-transition-kit` 裡的 `Environment_Transition_Kit/Handoff/NEW_SESSION_HANDOFF.md`，照第 3 節把環境收邊模組包放進《雲境》開 PR，再依第 4 節問我任務 B 要做哪一版。

如果 z1nnz 沒辦法安裝應用程式，也可以在你自己的電腦上執行第 3 節的指令並推送；你在《雲境》有 Write 權限。

---

## 1. 今天做了什麼（全部在 dondon，已推送）

儲存庫 `joshsu54/dondon`，分支 **`claude/environment-transition-kit`**，資料夾 `Environment_Transition_Kit/`。今天的提交：

| 提交 | 內容 |
| --- | --- |
| e3d7b94 | 規格、設計工程三視圖（階段 0–1） |
| 6a7f51e | 29 件白模與接頭檢查 |
| 167b376 | 29 件完成：細節、UV、烘焙貼圖、LOD、碰撞、FBX、QA |
| 179c764 | B07 護岸石重做、展示場景溪水 |
| f5de445 | D01 獨木橋、河岸重建、第一批預覽 |
| a8ffd52 | D02 木造梁橋、最終預覽、展示場景與報告 |
| ea4bf86 | 交接工具 `make_incoming_package.py`、`check_incoming.py` 與這份文件 |

成果：

- **A 道路收邊 11 件**（A01–A11）：左右直線、15°／30° 彎道、土石／草地過渡、斜坡、端點、破損。路面 3 m，兩側各 0.75 m 收邊帶，直段 4 m。
- **B 河岸收邊 10 件**（B01–B10）：直線兩款、內外轉角、緩坡、陡坡、亂石護岸（B07，使用者特別要求重做成大小不一、帶圓角的自然石）、多草、沖蝕、端點。陸地在行進方向左側，坡腳 -1.00 m，測試水位 -0.80 m。
- **C 橋頭收邊 8 件**（C01–C08）：石基、側邊、角石、道路／河岸過渡、緩坡修正、水邊。2 m 緩坡升到橋面 +0.15 m，寬 3 m。
- **D02 木造梁橋**（使用者要的「用木頭搭的橋樑」）：10 m 跨、4 根縱梁、48 片橋板、中央木排架橋墩、兩側欄杆（0.97 m），可行走淨寬 2.69 m，直接擱在兩岸 C05 橋頭石基上。
- **D01 獨木橋**：先做的，使用者說「不是獨木橋」後保留為可選件，不要當成主要的橋。
- 每件 LOD0／LOD1／LOD2、`_COL` 碰撞代理、世界尺度 UV（2 m 一個 UV 單位）、頂點色混合遮罩（R 濕、G 草、B 碎石、A 苔）。
- 共用貼圖 1024² 可無縫平鋪：乾土、濕土、草、苔、岩、碎石、樹皮、木材、年輪、橋木、水面法線、草片、混合雜訊。
- 預覽：每件 10 張正交視圖加 1 張 45° 透視（1024 px），附 `views.json`、`model_info.json`、`validation.json`；總表 Sheet A–D；展示場景（兩岸橋頭、清澈有深淺漸層的溪水、河床石、焦散）與接縫特寫；瀏覽器圖庫 `04_Previews/index.html`。
- 報告：`06_Reports/QA_Report.md`、`ASSET_MANIFEST.md/.csv`、`CONNECTOR_SPEC.json`、`ASSUMPTIONS.md`（44 條）、`README_Integration.md`（引擎匯入說明）、`PHASE6_ProtectedAssetRecheck.json`。

實際通過的檢查（來源端，Blender 5.2.3）：

- 接頭、7 條串接、16 組配對：誤差 ≤ 0.0005 mm（目標 1 mm）。
- 細節不越過接頭平面。
- 29 件 FBX 在 Blender 回匯一致。
- 預覽沒有被裁切。
- 受保護資產複查：未變更。

**沒做的：** Unity／Unreal 匯入、URP 材質、手機效能、引擎內碰撞與行走、GLB 匯出、AI 三視圖。

---

## 2. 不能違反的規定

### 原任務書（使用者最初的要求，仍然有效）

- **絕對不要修改「樹伴古樹」「山兔」「主世界 .blend」及其相關資料**（.blend、模型、貼圖、備份、輸出、場景、Collection 等）。不讀寫、不 Link/Append、不另存、不搬移、不清理。「備份不構成修改許可。」
- 不要把新模組合併進主世界；不要對整個專案做批次 cleanup、轉檔或遞迴刪除。
- Blender 不要用會清空目前場景的操作（未確認就 New/Open、`read_factory_settings`），也不要 `save_as_mainfile` 到受保護路徑。
- 做不出來的東西不要放假檔；報告要分清楚「已生成且驗證／已生成未驗證／待人工處理」。

### 《雲境》（`z1nnz/yun-jing-rpg` 的 AGENTS.md、CONTRIBUTING.md）

- 此儲存庫獨立於樹伴；**不得讀寫樹伴正式資料**。受保護素材：`qingxi-mountain-rabbit-v003`（山兔）、`elder-world-tree-*`（古樹）。
- **自己做新模型前，必須先用 AI 生成該物品的三視圖，檢視並保存後才建模**（使用者 2026-10-24 指定，不能跳過）。今天的套件沒有 AI 三視圖（當時沒有生圖工具），只有腳本畫的工程三視圖。這點已寫在套件 README，交接時要照實說明。新對話若也沒有生圖工具，**先告訴使用者，不要直接建模**。
- `main` 只能透過 PR，一個 PR 一件工作。合併前要過 `API and persistence tests` 和 `LFS asset integrity`。joshsu54 有 Write，可在檢查通過後 squash merge。
- 分支 `feature/短名稱`。PR 寫明完成內容、驗證方式、未完成項目；模型附預覽、來源、三視圖、尺寸、面數、LOD、碰撞、動畫清單。
- `.blend`、`.fbx`、`.glb`、`.png` 走 Git LFS（看 `.gitattributes`），推送前確認 `git lfs status`，不能只推指標檔。
- 不主動開其他對話或子代理；保留使用者的修改；每項變更跑相關測試；不提交快取、產物、憑證、私鑰。
- 不要同時改同一個 `.blend`。不要動 v12 道路母稿（`art/source/qingxi-road-props-v12.blend`）、既有 v8–v10 場景、既有蘆葦／花叢／苔石／木路燈、A 組的 API 與 C 組的審圖頁。

### dondon（`CLAUDE.md`）

- 繁體中文。不覆寫既有版本（新版本號或新批次）；不重設分支、不強制推送。圖庫與報告只寫實際通過的檢查。
- 套件的所有腳本都只寫進 `Environment_Transition_Kit/`，而且遇到已存在的檔案會停下來（不覆寫）。

---

## 3. 第一件事：把今天的套件放進《雲境》

### 3.1 準備

```sh
# 《雲境》
cd /home/user/yun-jing-rpg          # 或新對話實際的路徑
git lfs install && git config pull.ff only
git fetch origin && git switch main && git pull --ff-only origin main
git lfs pull                          # 今天這個對話被拒絕過（儲存庫沒授權）；新對話要確認成功
npm ci && npm test                    # 今天在 770ae09 是 55/55 通過

# dondon（套件來源；只需要這個資料夾）
cd /home/user/dondon
git fetch origin claude/environment-transition-kit
git switch claude/environment-transition-kit
git lfs pull --include="Environment_Transition_Kit/**"
```

Blender：今天用的是 `/opt/blender/blender-5.2.3-linux-x64/blender`（背景模式）。新環境如果沒有，需要裝 Blender 5.2.x。打包只需要 Python 3＋Pillow。

### 3.2 打包與檢查

`assets/dondon-import` 已經在 PR #3 合併過，**不要再用它**，從最新 main 開新分支：

```sh
cd /home/user/yun-jing-rpg
git switch -c assets/dondon-environment-kit-v001
python3 /home/user/dondon/Environment_Transition_Kit/05_Scripts/make_incoming_package.py \
    --dest art/incoming/dondon/EnvironmentTransitionKit/v001
blender -b --python-exit-code 1 \
    --python art/incoming/dondon/EnvironmentTransitionKit/v001/05_Scripts/check_incoming.py \
    -- --pkg art/incoming/dondon/EnvironmentTransitionKit/v001
```

- `make_incoming_package.py` 複製 00–06 資料夾與 README，會拒絕寫進已存在的資料夾，也會拒絕只有 LFS 指標的來源檔。單件預覽縮成 512 px（約 220 MB；加 `--full-previews` 保留 1024 px，約 430 MB）。它還會寫下：
  - `SOURCE.json`：來源提交，以及每個檔案的 SHA-256；
  - 根目錄 `model_info.json`、`validation.json`：31 件總表與來源端檢查彙整；
  - 中文 `README.md`：原本的套件說明改名為 `README_kit.md`。
- 套件**保留原資料夾結構**，因為 `.blend` 用相對路徑 `//../03_Textures/` 找貼圖（素材交接清單允許，README 已說明）。
- `check_incoming.py` 在接收端位置做三件事，結果寫進 `handoff_check.json`，**不存檔**：
  - 重開每個 `.blend`，確認貼圖與連結的檔案都找得到；
  - 回匯 34 個 FBX；
  - 比對尺寸與物件名稱。
- 今天在暫存位置實測的結果：
  - 13 個 `.blend`（9 個模組檔，加上連結模組檔的拼裝測試與展示場景）全部能打開，缺貼圖 0、缺連結檔 0；
  - 34 個 FBX 尺寸誤差最大 3.6×10⁻⁷ m，29 件名稱全對；
  - 656 個檔案，約 217 MB。

### 3.3 提交與 PR

```sh
git add art/incoming/dondon/EnvironmentTransitionKit
git diff --cached --stat && git lfs status
git commit -m "assets: add dondon Environment Transition Kit v001 under art/incoming/dondon"
git push -u origin assets/dondon-environment-kit-v001
```

- 可以考慮在 `art/incoming/dondon/README.md` 最後加一小節連到新套件。那份 README 是 dondon2.0 批次的紀錄，不要改它既有的表格；`inventory.json`、`stage_manifest.json` 也屬於 dondon2.0 批次，不要動。
- PR 說明照 CONTRIBUTING 的格式：
  - **完成內容：** 31 件、檔案位置；
  - **驗證：** `handoff_check.json` 與來源端 QA；
  - **未完成：** Unity、URP、手機效能、引擎碰撞與行走、GLB、AI 三視圖；
  - **三視圖：** 說明是工程圖，不是 AI 圖；
  - **規格：** 尺寸與面數（`ASSET_MANIFEST.md`）、LOD、碰撞；動畫：無；
  - **授權：** 由 joshsu54 與 z1nnz 確認。
- 等兩個 CI 檢查（尤其 `LFS asset integrity`）通過。這是素材交接 PR，**和任務 B 分開**。

---

## 4. 第二件事：任務 B（先問使用者做哪一版）

《雲境》有兩份 B 任務，**開工前先問使用者**：

### 4.1 使用者今天貼給我的版本（`docs/execution/2026-10-26/07-daily-14h-work-package.md`）

> **B｜自然道路與水岸拼件，14 小時**
> 輸入：道路三視圖、既有河岸與古樹樣片、`art/source/qingxi-detail-props-v2.blend`。不要重做既有蘆葦、花叢、苔石、木路燈初版。新幾何的三視圖先保存；母稿另存 `art/source/qingxi-road-bank-v2.blend`。
>
> | 預算 | 任務與可檢查產物 |
> |---:|---|
> | 2 小時 | 量定玩家通行淨寬、直段／左右彎接縫與橋頭標高；對照道路三視圖標註土、草、碎石及裸岩分布。缺少新物件參考時先產三視圖。 |
> | 4 小時 | 建三個可接的土路段，路緣用不規則輪廓與高度起伏；接縫不露底、不產生突兀直角或長方形貼片。 |
> | 3 小時 | 製作大小層次不同的石塊、碎石散佈與稀疏／密集植被變體；用實例調整尺度、旋轉與密度，近景不露重複規律。 |
> | 2 小時 | 完成接木橋、接河岸石階的兩個收邊件；地面可走表面連續，河岸和水面不相互穿透。 |
> | 3 小時 | 匯出 GLB、回匯及幾何 QA；交頂／側／斜視預覽、尺寸面數表與 180 × 140 m 青溪場景擺位建議，開 PR。 |
>
> 驗收：三段路能交換順序仍接得上、橋與河岸過渡自然；圖像比較能看出與三視圖的差距縮小。流動水本日只需**保留**核心組既有 Blender 樣片，不由 B 新建正式水系統。

### 4.2 目前生效的版本（`docs/execution/2026-10-26/10-qingxi-three-collaborators-42h.md`，寫著「此單取代 09 舊工作包」）

**B｜不規則道路＋採集路線（14 小時）**，分支 `feature/qingxi-road-and-trail-v1`。

- 專責範圍：
  - `art/references/qingxi-road-trail-v1/` 與同名的 source／exports／previews；
  - `tools/world-preview/` 的試走路線。
- 參考：道路三視圖、河岸三視圖。新石、花、橋件也要先做 AI 三視圖。
- 工作內容：
  1. 量 v12 道路與村口接口，標出「村口 → 藥草點 → 石材點 → 回村」路線，淨寬 ≥ 2.4 m。
  2. 兩段能相接的 S 型土路、一段橋頭過渡、四種半埋岩石、三種草花組；路緣是土石與草的自然過渡，沒有方形貼片。交 GLB 與 1.7 m 眼高預覽。
  3. 在 `tools/world-preview/` 做可重走的採集路線：顯示目前目標、已去過的地點、重置入口。真正的採集獎勵必須呼叫服務端既有的採集動作，不能用瀏覽器本機狀態改背包。
  4. 桌面鍵盤與手機觸控各完整走一次，修通路、碰撞、深水阻擋與提示。
  5. Blender QA、GLB 回匯、預覽截圖，報告與概念圖還差的材質或植被細節。
- 不要同時重做完整河流、水材質或大橋。

### 4.3 今天的套件可以怎麼用在 B

- 可以直接沿用的是**做法與工具**：
  - 接頭系統：`kit_spec.py`，兩端截面一致，所以順序可以互換；
  - 不規則路緣與高度起伏、頂點色混合、可平鋪貼圖烘焙；
  - 自然石生成器：`kit_blender.py` 的 `chunk`／`rock`；
  - 細節不越界檢查、接縫特寫、預覽、FBX 回匯檢查。
- 要另外做的：
  - **先做 AI 三視圖**；
  - 量《雲境》的 v12 道路與村口尺寸：今天的套件是 3 m 路面，B 要求淨寬 ≥ 2.4 m，要對齊雲境實際數值；
  - GLB 匯出（今天只有 FBX）；
  - 照《雲境》的路徑另存母稿，不寫進 dondon 套件資料夾；
  - 180 × 140 m 擺位建議；
  - （10 版）`tools/world-preview/` 的路線程式與測試。
- 今天在《雲境》只讀過文件。因為 LFS 被擋，`art/source/qingxi-*.blend`（detail-props-v2、riverbank-v2、timber-bridge-v1、winding-road-v1、road-props-v12）都**沒有實際打開過**，新對話要自己 `git lfs pull` 後檢查。

---

## 5. 使用者的偏好（今天學到的）

- **語言：** 白話繁體中文，少用術語。使用者會說「我全都要」，希望東西看起來是完成品，不是灰模或示意。
- **石頭：** 要自然，大小不一、帶圓角，不要像方糖、地磚或一塊一塊的方塊（「岸邊上一塊一塊的石頭是三小」）。苔蘚不要像綠色紙片。
- **邊緣：** 路緣與過渡帶要參差不齊，不能有直角、長方形貼片或整齊的排列。
- **水：** 要清澈到看得見水底，有由淺到深的漸層（「我想要那種清澈到能看到水下的那種溪水然後有漸層」）。
- **橋：** 要用木頭搭的橋樑，有梁、橋板、欄杆、橋墩，不是一根原木。
- **出圖：** 每次出圖後**自己打開圖片檢查**有沒有黑面、穿插、Z-fighting、白色亮斑、被裁切。
- **回報：** QA 照實寫，沒驗證就寫沒驗證。

---

## 6. 工具清單（`Environment_Transition_Kit/05_Scripts/`）

| 腳本 | 用途 |
| --- | --- |
| `kit_spec.py` | 所有尺寸、接頭截面、三角面預算的唯一來源 |
| `kit_blender.py` | 共用建模：路緣網格、自然石 `chunk`、岩石 `rock`、切石 `dressed_stone`、LOD 減面、材質、`KB.new_output`（不覆寫）、`KB.kit_path`（限制只寫套件內） |
| `bake_textures.py` | 4D 環面雜訊烘焙可無縫平鋪 PBR 貼圖 |
| `generate_modules.py` | 生成 29 件（含 Guard：細節越過接頭就移除並記錄） |
| `generate_timber_bridge.py`／`generate_log_bridge.py` | D02 木橋／D01 獨木橋（含驗證、回匯、預覽） |
| `validate_connectors.py` | 接頭、串接、配對、細節越界檢查 |
| `export_fbx.py` | FBX 匯出與回匯驗證 |
| `render_previews.py` | 每件 10 正交＋45° 透視 |
| `render_showcase.py`／`annotate_showcase.py` | 展示場景、溪水、接縫特寫與中文標註 |
| `write_final_reports.py` | 總表、裁切檢查、所有報告與圖庫頁 |
| `build_all.sh` | 依序跑完整流程 |
| `make_incoming_package.py`／`check_incoming.py` | 打包到《雲境》交接資料夾、接收端檢查 |

執行方式：

```sh
/opt/blender/blender-5.2.3-linux-x64/blender -b --python-exit-code 1 --python <絕對路徑> -- <參數>
```

## 7. 今天踩過的坑

- **Cycles 出圖慢：** 正交視圖 12 samples、透視 32 samples 就夠。
- **水面白色亮斑：** 補光被水面反射造成，補光要設 `visible_glossy=False`。
- **黑三角面：** 內核方塊要內縮，不要和外殼共面。
- **斜撐黑菱形：** 斜撐交叉要錯開。
- **icosphere 細分：** 細分 1 只有 20 面，自然石至少用細分 2。
- **`pkill`：** 會殺到自己的 shell，改用 PID 結束程序。
- **LFS checkout 失敗：** 留下空 index 時，用 `GIT_LFS_SKIP_SMUDGE=1 git reset -q` 修復。
- **連不到 z1nnz/yun-jing-rpg：** 是儲存庫授權問題（Claude 應用程式沒裝在 z1nnz/yun-jing-rpg），不要用別的方法繞過，請使用者處理。
