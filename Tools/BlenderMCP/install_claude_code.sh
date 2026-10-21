#!/bin/sh
# One-step Blender MCP setup for Claude Code on this computer (macOS or Linux).
#   1. Python venv in Tools/BlenderMCP/.venv with the pinned mcp-for-blender (requirements.lock.txt)
#   2. Install + enable the bundled Blender add-on (existing add-on file and userpref.blend are backed up first)
#   3. Register the "blender" MCP server with Claude Code (local scope: this project, this computer only)
# Usage:  sh Tools/BlenderMCP/install_claude_code.sh [path/to/Blender]
#         BLENDER=/path/to/Blender sh Tools/BlenderMCP/install_claude_code.sh
#         NO_CLAUDE=1 ...   skip step 3
set -eu
TOOL_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO=$(CDPATH= cd -- "$TOOL_DIR/../.." && pwd)
say() { printf '\n== %s\n' "$*"; }

# ---- 1. Python environment
say "Python environment"
if [ ! -x "$TOOL_DIR/.venv/bin/mcp-for-blender" ]; then
  if command -v uv >/dev/null 2>&1; then
    uv venv --python '>=3.10' "$TOOL_DIR/.venv"
    uv pip install --python "$TOOL_DIR/.venv/bin/python" -r "$TOOL_DIR/requirements.lock.txt"
  else
    PY=${PYTHON:-python3}
    "$PY" -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
    "$PY" -m venv "$TOOL_DIR/.venv"
    "$TOOL_DIR/.venv/bin/python" -m pip install --quiet --upgrade pip
    "$TOOL_DIR/.venv/bin/python" -m pip install --quiet -r "$TOOL_DIR/requirements.lock.txt"
  fi
fi
"$TOOL_DIR/.venv/bin/python" -c 'import blender_mcp, mcp; print("mcp-for-blender ready")'

# ---- 2. Blender add-on
say "Blender add-on"
BL=${1:-${BLENDER:-}}
if [ -z "$BL" ]; then
  for c in "/Applications/Blender.app/Contents/MacOS/Blender" "/Applications/Blender 2.app/Contents/MacOS/Blender" "$(command -v blender 2>/dev/null || true)"; do
    [ -n "$c" ] && [ -x "$c" ] && BL=$c && break
  done
fi
[ -n "$BL" ] && [ -x "$BL" ] || { echo "Blender not found. Pass its path: sh $0 /Applications/Blender.app/Contents/MacOS/Blender"; exit 1; }
"$BL" --version | head -1
"$BL" --background --factory-startup --python "$TOOL_DIR/install_blender_addon.py" 2>&1 | grep -E 'BLENDER_MCP_INSTALLED|Error|Traceback' || { echo "Add-on install failed"; exit 1; }

# ---- 3. Claude Code registration
say "Claude Code"
if [ "${NO_CLAUDE:-}" = 1 ]; then
  echo "Skipped (NO_CLAUDE=1)."
elif command -v claude >/dev/null 2>&1; then
  cd "$REPO"
  claude mcp remove blender --scope local >/dev/null 2>&1 || true
  claude mcp add blender --scope local -- "$TOOL_DIR/start-mcp"
  claude mcp list 2>/dev/null | grep -i blender || true
else
  echo "claude CLI not found. Install Claude Code, then run in $REPO:"
  echo "  claude mcp add blender --scope local -- \"$TOOL_DIR/start-mcp\""
fi

say "Done"
echo "Next: open Blender (the add-on starts its server on 127.0.0.1:9876; if not, press N in the 3D view > MCP tab > Start),"
echo "then run 'claude' in $REPO and type /mcp to check that 'blender' is connected. Keep only one Blender instance open."
