# Blender 工具安裝紀錄

## Claude Code 一鍵安裝（2026-10-21）

在專案根目錄執行：

```sh
sh Tools/BlenderMCP/install_claude_code.sh
# 若找不到 Blender：sh Tools/BlenderMCP/install_claude_code.sh "/Applications/Blender.app/Contents/MacOS/Blender"
```

腳本依序完成三件事：
1. 在 `Tools/BlenderMCP/.venv` 建立 Python 環境，並依 `requirements.lock.txt` 安裝鎖定版本的 `mcp-for-blender==2.1.9`（有 `uv` 用 `uv`，否則用 `python3 -m venv`）。已存在的環境會直接沿用。
2. 用 Blender 背景模式執行 `install_blender_addon.py`，安裝並啟用外掛。原有的外掛檔與 `userpref.blend` 會先備份成 `.bak`，並維持遙測關閉。
3. 以 `claude mcp add blender --scope local` 向 Claude Code 註冊。設定只存在這台電腦的這個專案，不會寫進版本庫。

完成後開啟 Blender，在專案資料夾執行 `claude`，輸入 `/mcp` 確認 `blender` 已連線。

腳本已在雲端 Linux 容器（Blender 5.2.2）實測步驟 1、2，MCP 伺服器也能正常回應初始化請求。步驟 3 只檢查了指令格式。實際連到開著的 Blender 視窗必須在你的電腦上進行。`install_blender_addon.py` 現在會自動尋找任何 Python 3 版本的外掛檔，不再寫死 3.14。


2026-10-15 完成。

- Computer Use：沿用已安裝的工具，已成功開啟 Blender 5.3 並擷取視窗。
- Blender MCP：PyPI `mcp-for-blender==2.1.9`，安裝在本資料夾 `.venv`，相依版本見 `requirements.lock.txt`。
- 外掛：已在 Blender 5.3 和 5.4 的使用者外掛資料夾安裝並啟用。既有偏好設定如存在，已先建立帶時間戳記的 `.bak`。
- Codex：全域 MCP 名稱 `blender`，啟動器為本資料夾 `start-mcp`。已透過實際 MCP 工具讀取 Blender 5.3 的預設場景，協定版本 13 相符。
- Blender CLI：沿用 `/Applications/Blender 2.app/Contents/MacOS/Blender`，專案捷徑為 `Tools/bin/blender`，已驗證背景 Python 執行。

## 使用

開啟 Blender 2.app，外掛會自動啟動本機連線。若手動停止過，可在 3D 視窗按 N，從 MCP 面板重新啟動。避免同時開啟兩個 Blender 搶用同一連接埠。

在專案根目錄執行 CLI：

```sh
./Tools/bin/blender --background --python BlenderSource/MaterialShop/build_material_shop.py
```

這會執行建模腳本；請先查看該腳本的輸出位置。CLI 捷徑未修改系統 PATH。

MCP 啟動器連到 `127.0.0.1:9876`，設定 `DISABLE_TELEMETRY=true`；Blender 外掛的遙測同意維持關閉。素材服務與付費生成服務未啟用。

獨立環境與 Codex 設定使用絕對路徑；若移動專案資料夾，需重建環境並更新連線路徑。

來源：[MCP for Blender](https://github.com/ahujasid/mcp-for-blender)（社群專案）、[Codex MCP 文件](https://developers.openai.com/codex/mcp)。
