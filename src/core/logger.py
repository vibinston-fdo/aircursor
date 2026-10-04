"""
AirCursor Pro — Application Logger
Centralised logging with INFO / WARNING / ERROR levels.
Logs to console + optional rotating file.
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from src.core import config

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOG_FILE = os.path.join(_ROOT, "aircursor.log")

_logger: logging.Logger | None = None


def get_logger(name: str = "AirCursor") -> logging.Logger:
    global _logger
    if _logger is not None:
        return logging.getLogger(name)

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S"
    )

    root = logging.getLogger("AirCursor")
    root.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # File handler (5 MB × 3 backups)
    try:
        fh = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3,
                                 encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        root.addHandler(fh)
    except OSError:
        pass  # read-only filesystem — log only to console

    _logger = root
    root.info(f"AirCursor Pro {config.APP_VERSION} — Logger initialised")
    return logging.getLogger(name)
