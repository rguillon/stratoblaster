# Copyright (c) 2026 Renaud Guillon
"""Entry point of the ground worker (PERF-14).

Transcrypt compiles this file (ENG-150), and the Makefile bundles it to `dist/js/ground_worker.js`,
the script that `render/scenery/background_loader.py` starts. It installs the worker module's
message handler on the worker's global scope.
"""

from render.scenery.ground_worker import install_message_handler

install_message_handler()
