"""Selects the batch design spec. TL_SPEC=town10_shapes ./run_all09.sh ... (default town09_shapes)."""
import importlib
import os

S = importlib.import_module(os.environ.get('TL_SPEC', 'town09_shapes'))
