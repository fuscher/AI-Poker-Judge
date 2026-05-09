"""快速开始示例"""

from aipokerjudge import ModelClient, BatchRunner, save_report
from aipokerjudge.config import MODEL_A_NAME, MODEL_A_API_KEY, MODEL_A_BASE_URL

def main():
    # 初始化模型
    model = ModelClient(MODEL_A_NAME, MODEL_A_API_KEY, MODEL_A_BASE_URL)
    
    # 让模型自己和自己对局（测试用）
    runner = BatchRunner(model, model)
    
    # 运行5局
    print("开始测试...")
    result = runner.run_batch(rounds=5, seed=42, verbose=True)
    
    # 生成报表
    save_report(result, "ModelA", "ModelA")
    print(f"完成! 比分: {result.a_wins}:{result.b_wins}")

if __name__ == "__main__":
    main()