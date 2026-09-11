import logging
import sys
import os
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

LOG_DIR - os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok = True)

logger = logging.getLogger('ats_resume_scorer')
logger.setLevel(logging.INFO)

