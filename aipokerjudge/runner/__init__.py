"""对局运行器模块"""

from .batch_runner import BatchRunner, GameRecord, BatchResult
from .visual_runner import run_visual_mode
from .blackbox_runner import run_blackbox_mode

__all__ = ["BatchRunner", "GameRecord", "BatchResult", "run_visual_mode", "run_blackbox_mode"]