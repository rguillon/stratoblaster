# Type stub for the browser globals. At compile time Transcrypt turns these names into the
# real JavaScript globals (`from org.transcrypt.stubs.browser import *` is a compile-time no-op).
from typing import Any

document: Any
window: Any

def __pragma__(*args: Any) -> None: ...
