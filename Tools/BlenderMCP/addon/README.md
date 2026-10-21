# Blender MCP 外掛（手動安裝用）

`blender_mcp.py` 是 `mcp-for-blender==2.1.9`（MIT 授權，見 `LICENSE`，作者 Siddharth Ahuja）內附的 Blender 外掛原檔，未修改。版本要和 `requirements.lock.txt` 的伺服器一致。

手動安裝：
1. Blender → Edit → Preferences → Add-ons。
2. 右上角選單 → Install from Disk，選這個 `blender_mcp.py`。
3. 勾選啟用 "Blender MCP"。
4. 在 3D 視窗按 N，打開 MCP 分頁，按 Start／Connect。伺服器會監聽 127.0.0.1:9876。
