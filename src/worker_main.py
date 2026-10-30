"""Entry point of the ground worker (P13-R03). Transcrypt compiles this file, and the Makefile
bundles it to `dist/js/ground_worker.js`, the script that `render/scenery/background_loader.py`
starts. Importing the worker module installs its message handler on the worker's global scope.
"""

import render.scenery.ground_worker  # noqa: F401
