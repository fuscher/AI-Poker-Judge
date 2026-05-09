"""安装脚本"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="aipokerjudge",
    version="0.1.0",
    author="AIPokerJudge Contributors",
    description="AI vs AI 斗地主对决平台 - 测试LLM决策能力、规则遵循度与性能表现",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AI-Poker-Judge",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "aipokerjudge=aipokerjudge.cli:main",
        ],
    },
)