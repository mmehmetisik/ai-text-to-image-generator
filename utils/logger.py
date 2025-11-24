# ============================================
# LOGGING SYSTEM (logger.py)
# Logs all operations and errors.
# Writes to both console and file.
# ============================================

import logging
import os
from datetime import datetime

# Create log folder
LOG_FOLDER = "logs"
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

# Log file name (new file each day)
log_file = os.path.join(LOG_FOLDER, f"app_{datetime.now().strftime('%Y%m%d')}.log")

# Configure logger
logger = logging.getLogger("AIImageGenerator")
logger.setLevel(logging.DEBUG)  # Capture all levels

# Console handler (writes to terminal)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# File handler (writes to file)
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# Log format
log_format = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

console_handler.setFormatter(log_format)
file_handler.setFormatter(log_format)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Functions for ease of use
def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)

def log_warning(message):
    logger.warning(message)

def log_debug(message):
    logger.debug(message)