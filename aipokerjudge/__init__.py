"""
AI-Poker-Judge - 人工智能扑克荷官
AI vs AI 斗地主对决平台
"""

__version__ = "0.1.0"
__author__ = "AIPokerJudge Contributors"

from .game.engine import DouDiZhuEngine
from .game.models import GameState, GameStatus, TurnRecord
from .model.client import ModelClient
from .runner.batch_runner import BatchRunner
from .report.generator import generate_report, save_report

__all__ = [
    "DouDiZhuEngine",
    "GameState",
    "GameStatus",
    "TurnRecord",
    "ModelClient",
    "BatchRunner",
    "generate_report",
    "save_report",
]