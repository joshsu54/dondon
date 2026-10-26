# 用 Codex 把環境收邊模組包上傳到《雲境》

這個資料夾是**已經整理好、檢查過的上傳包**，只要複製進《雲境》就能開 PR，不用 Blender，也不用重新打包。

| 檔案 | 用途 |
| --- | --- |
| `EnvironmentTransitionKit/v001/` | 上傳包本體：今天全部的模型、貼圖、預覽、腳本、報告與檢查結果 |
| `PACKAGE_SHA256.json` | 上傳包每個檔案的雜湊值，安裝時用來確認檔案完整 |
| `install_into_yunjing.py` | 安裝腳本：檢查完整性 → 複製到 `art/incoming/dondon/EnvironmentTransitionKit/` → 再檢查 → 在 `art/incoming/dondon/README.md` 末尾加一節。只用 Python 內建功能，不碰 git |
| `README_append.md` | 要加到 `art/incoming/dondon/README.md` 末尾的那一節 |
| `PR_BODY.md` | PR 說明（照《雲境》的 PR 範本寫好） |

---

## 給使用者

1. 建議用**電腦上的 Codex**（Codex CLI 或 VS Code 擴充），因為它會用你電腦上的 git 登入，而你在《雲境》有寫入權限。電腦需要先裝好：Git、[Git LFS](https://git-lfs.com/)、Python 3、Node.js 22；要讓 Codex 開 PR，再加 GitHub CLI（`gh`，並先 `gh auth login`）。
2. 雲端版 Codex 是否能下載和上傳 Git LFS 大檔，我無法確認。如果用雲端版，請確認它能 `git lfs pull` 並推送 LFS 物件，否則圖片和模型只會剩下指標檔，`LFS asset integrity` 檢查會失敗。
3. 在 Codex 貼下面這段：

> 請照 `joshsu54/dondon` 分支 `claude/environment-transition-kit` 的 `Environment_Transition_Kit/Handoff/yunjing_upload/CODEX_UPLOAD.md`（https://github.com/joshsu54/dondon/blob/claude/environment-transition-kit/Environment_Transition_Kit/Handoff/yunjing_upload/CODEX_UPLOAD.md ）「給 Codex」那一節，把環境收邊模組包上傳到 z1nnz/yun-jing-rpg 並開 PR。只複製檔案，不要修改或重做任何模型。每一步的結果都要告訴我，失敗就停下來。

---

## 給 Codex

### 規定

- 遵守 `z1nnz/yun-jing-rpg` 的 `AGENTS.md` 與 `CONTRIBUTING.md`。
- 這次**只是素材交接**：只新增 `art/incoming/dondon/EnvironmentTransitionKit/`，並在 `art/incoming/dondon/README.md` 末尾加一節。不要修改、重新匯出或重新建模任何檔案。不要動其他檔案，包括 `inventory.json`、`stage_manifest.json`、其他素材、程式與設定。
- 不要碰樹伴、古樹（`elder-world-tree-*`）、山兔（`qingxi-mountain-rabbit-v003`）或任何主世界 `.blend`。
- `main` 只透過 PR 更新：不要直接推 main，不要強制推送，不要在 CI 通過前合併。
- `.blend`、`.fbx`、`.png` 必須走 Git LFS（`.gitattributes` 已設定）。推送前用 `git lfs status` 確認它們是 `(LFS: …)`，不是 `(Git: …)`。
- 安裝腳本若報錯，**停下來回報**，不要手動繞過檢查。

### 步驟 1：取得上傳包（只抓這個資料夾，約 220 MB）

```sh
git lfs install
git clone --filter=blob:none --no-checkout --branch claude/environment-transition-kit https://github.com/joshsu54/dondon.git dondon-kit
cd dondon-kit
git sparse-checkout set Environment_Transition_Kit/Handoff
git checkout claude/environment-transition-kit
git lfs pull --include="Environment_Transition_Kit/Handoff/**"
cd ..
```

### 步驟 2：在《雲境》開分支並安裝

```sh
git clone https://github.com/z1nnz/yun-jing-rpg.git   # 已經有就跳過這行，改用既有的資料夾
cd yun-jing-rpg
git config pull.ff only
git status                      # 確認沒有別人未提交的修改；有就停下來問使用者
git switch main
git pull --ff-only origin main
git switch -c assets/dondon-environment-kit-v001
python3 ../dondon-kit/Environment_Transition_Kit/Handoff/yunjing_upload/install_into_yunjing.py --repo .
```

- Windows 若沒有 `python3`，改用 `python` 或 `py`。
- 分支名稱：`assets/dondon-import` 已在 PR #3 合併過，不要重用。如果 `assets/dondon-environment-kit-v001` 在遠端已經存在，先停下來問使用者。
- 安裝成功時會印出兩行 `... files match PACKAGE_SHA256.json`（source package、installed copy），以及 `INSTALLED -> art/incoming/dondon/EnvironmentTransitionKit`。

### 步驟 3：檢查

```sh
git add art/incoming/dondon
git diff --cached --stat        # 預期約 662 個檔案：上傳包加上 README.md 一處修改
git lfs status                  # .blend／.fbx／.png 都應該是 (LFS: …)，約 508 個
npm ci
npm test                        # 這次沒有改程式，應該和 main 一樣全部通過
```

`git diff --cached` 只能出現 `art/incoming/dondon/EnvironmentTransitionKit/...` 和 `art/incoming/dondon/README.md`。多了別的檔案就停下來。

### 步驟 4：提交、推送、開 PR

```sh
git commit -m "assets: add dondon Environment Transition Kit v001 under art/incoming/dondon"
git push -u origin assets/dondon-environment-kit-v001
```

開 PR 前，先在 `PR_BODY.md` 填兩處：

- 「驗證結果」中 `npm test` 那一格，勾選並寫上結果；
- 「測試摘要」中 `npm test` 那一行，同樣填上結果；
- 「合併前確認」中「已同步最新 main」那一格，勾選並寫上目前 main 的提交編號。

其他內容不要改，也不要把沒做過的檢查勾成已完成。

```sh
gh pr create --base main --head assets/dondon-environment-kit-v001 \
  --title "assets: add dondon Environment Transition Kit v001 under art/incoming/dondon" \
  --body-file ../dondon-kit/Environment_Transition_Kit/Handoff/yunjing_upload/PR_BODY.md
gh pr checks --watch
```

沒有 `gh` 的話，就把網址 `https://github.com/z1nnz/yun-jing-rpg/compare/main...assets/dondon-environment-kit-v001` 和 `PR_BODY.md` 的內容交給使用者，由使用者在網頁上開 PR。

- 兩個檢查（`API and persistence tests`、`LFS asset integrity`）都要通過。
- `LFS asset integrity` 失敗，通常是 LFS 物件沒上傳：執行 `git lfs push --all origin assets/dondon-environment-kit-v001` 後再看；不要刪檔或關掉檢查。
- 合併由使用者決定。CONTRIBUTING 寫明 joshsu54 可在檢查通過後 squash merge。

---

## 這個包已經做過的檢查（Claude，2026-10-26）

- **Blender 5.2.3 實際重開與回匯**（結果在 `EnvironmentTransitionKit/v001/handoff_check.json`）：
  - 13 個 `.blend` 缺貼圖 0、缺連結檔 0；
  - 34 個 FBX 回匯，尺寸誤差小於 0.001 mm，29 件物件名稱一致。
- **來源端 QA**（`validation.json`）：
  - 接頭、串接、配對誤差 ≤ 0.0005 mm；
  - FBX 回匯 29/29；
  - 預覽沒有被裁切；
  - 受保護資產未變更。
- **同一包在《雲境》main `40adb20` 的試裝：** 安裝與 `npm test`（55/55）都通過。該次提交因為 Claude 沒有《雲境》的推送權限（403）而沒有推送。
- **沒做的：**
  - Unity／URP 匯入與材質重建；
  - 手機效能；
  - 引擎內碰撞與行走；
  - GLB 匯出；
  - AI 三視圖（建模前參考是腳本畫的工程三視圖，PR 裡照實寫明）。
