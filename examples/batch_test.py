"""批量测试示例 - 演示如何通过代码进行批量测试"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aipokerjudge import ModelClient, BatchRunner, save_report
from aipokerjudge.config import (
    MODEL_A_NAME, MODEL_A_API_KEY, MODEL_A_BASE_URL,
    MODEL_B_NAME, MODEL_B_API_KEY, MODEL_B_BASE_URL
)


def main():
    """批量测试示例"""
    print("=" * 60)
    print("批量测试示例")
    print("=" * 60)
    
    # 1. 初始化模型客户端
    print("\n1. 初始化模型...")
    model_a = ModelClient(MODEL_A_NAME, MODEL_A_API_KEY, MODEL_A_BASE_URL)
    model_b = ModelClient(MODEL_B_NAME, MODEL_B_API_KEY or MODEL_A_API_KEY, MODEL_B_BASE_URL)
    print(f"   模型A: {MODEL_A_NAME}")
    print(f"   模型B: {MODEL_B_NAME}")
    
    # 2. 创建运行器
    print("\n2. 创建批量运行器...")
    runner = BatchRunner(model_a, model_b)
    
    # 3. 运行批量测试
    print("\n3. 开始批量测试...")
    rounds = 10  # 测试10局
    seed = 42    # 固定种子，保证可复现
    
    result = runner.run_batch(rounds=rounds, seed=seed, verbose=False)
    
    # 4. 输出结果
    print("\n4. 测试结果:")
    print(f"   总局数: {result.total_rounds}")
    print(f"   比分: {result.a_wins} : {result.b_wins}")
    print(f"   胜率: A:{result.a_wins/rounds*100:.1f}% B:{result.b_wins/rounds*100:.1f}%")
    print(f"   违规: A:{result.a_violations} B:{result.b_violations}")
    print(f"   超时: A:{result.a_timeouts} B:{result.b_timeouts}")
    print(f"   平均响应: A:{result.a_avg_response_ms:.0f}ms B:{result.b_avg_response_ms:.0f}ms")
    
    # 5. 保存报表
    print("\n5. 保存报表...")
    save_report(result, MODEL_A_NAME, MODEL_B_NAME)
    
    print("\n✅ 批量测试完成!")


if __name__ == "__main__":
    main()