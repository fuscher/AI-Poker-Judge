"""Configuration file - users need to modify settings here
配置文件 - 用户需要修改这里的设置"""

import os

# ============ Model A Configuration ============
# ============ 模型A配置 ============
MODEL_A_NAME = os.getenv("MODEL_A_NAME", "deepseek-chat")
MODEL_A_API_KEY = os.getenv("MODEL_A_API_KEY", os.getenv("OPENAI_API_KEY", ""))
MODEL_A_BASE_URL = os.getenv("MODEL_A_BASE_URL", os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com"))

# ============ Model B Configuration ============
# ============ 模型B配置 ============
MODEL_B_NAME = os.getenv("MODEL_B_NAME", "deepseek-chat")
MODEL_B_API_KEY = os.getenv("MODEL_B_API_KEY", os.getenv("OPENAI_API_KEY", ""))
MODEL_B_BASE_URL = os.getenv("MODEL_B_BASE_URL", os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com"))

# ============ Game Configuration ============
# ============ 游戏配置 ============
# Model response timeout (seconds)
TIMEOUT_SECONDS = 60           # 模型响应超时时间（秒）
# Maximum turns per game to prevent infinite loops
MAX_TURNS_PER_GAME = 100       # 单局最大回合数，防止无限循环
# Default number of rounds (recommend even number for position swapping)
DEFAULT_ROUNDS = 50            # 默认对局轮次（建议偶数，配合位置轮换）
# Default random seed (None for truly random)
DEFAULT_SEED = 42              # 默认随机种子（None表示真随机）
# Enable position swapping (swap model positions on even rounds)
POSITION_SWAP = True            # 是否启用位置轮换（偶数局交换模型位置）
# Enable deal normalization (adjacent rounds share same hand with swapped positions)
DEAL_NORMALIZATION = True       # 是否启用发牌归一化（相邻两局用同一手牌交换位置）

# ============ Report Configuration ============
# ============ 报表配置 ============
# Report output directory
REPORT_OUTPUT_DIR = "reports"  # 报表输出目录
# Whether to save detailed logs (JSON format)
SAVE_DETAIL_LOGS = True        # 是否保存详细日志（JSON格式）
# Number of parallel threads for blackbox mode
BLACKBOX_WORKERS = 3            # 黑盒模式并行线程数

# ============ Card Type Configuration ============
# ============ 牌型配置 ============
CARD_RANKS = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
CARD_RANK_VALUE = {rank: i for i, rank in enumerate(CARD_RANKS)}

# Card type priority (for comparison)
# 牌型优先级（用于比较）
PLAY_TYPE_PRIORITY = {
    'single': 1,
    'pair': 2,
    'triplet': 3,
    'triplet_with_one': 4,
    'straight': 5,
    'bomb': 10,
}