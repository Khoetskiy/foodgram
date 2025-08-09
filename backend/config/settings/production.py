# ruff: noqa
import os

from .base import *

if DEBUG:
    raise RuntimeError(
        'ПРЕДУПРЕЖДЕНИЕ О БЕЗОПАСНОСТИ: не запускайте с включенной отладкой в производственной среде!'
    )
