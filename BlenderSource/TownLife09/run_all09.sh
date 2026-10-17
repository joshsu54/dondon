#!/bin/sh
# Full TownLife09 pipeline: concepts first, then Blender models, checks, sheets, library registration.
# Batch spec: TL_SPEC=town10_shapes ./run_all09.sh (default town09_shapes).
set -e
cd "$(dirname "$0")"
python3 concept_render09.py "$@"
python3 build_town_assets09.py "$@"
python3 verify_town_assets09.py
python3 contact_sheets09.py
python3 register_batch09.py
