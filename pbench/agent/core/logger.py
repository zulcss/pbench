import os
import logging

import colorlog

logger_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(message)s",
    log_colors=dict(
        DEBUG="blue",
        INFO="green",
        WARNING="yellow",
        ERROR="red",
        CRITICAL="bold_red,bg_white",
    ),
)
LOGGER_NAME = "pbench-agent"
DEFAULT_LOG_LEVEL = logging.WARN
if os.environ.get("IR_DEBUG"):
    DEFAULT_LOG_LEVEL = logging.DEBUG

LOG = logging.getLogger(LOGGER_NAME)
LOG.setLevel(DEFAULT_LOG_LEVEL)

# Create stream handler with debug level
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)

# Add the logger_formatter to sh
sh.setFormatter(logger_formatter)

# Create logger and add handler to it
LOG.addHandler(sh)
