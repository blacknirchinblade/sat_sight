from setuptools import setup, find_packages

setup(
    name="sat_sight",
    version="1.0.0",
    description="Advanced Satellite Image Analysis with AI Agents",
    author="Sat-Sight Team",
    packages=find_packages(),
    python_requires=">=3.12",
    install_requires=[
        "langchain>=0.3.17",
        "langchain-groq>=0.2.1",
        "langchain-community>=0.3.16",
        "langgraph>=0.2.59",
        "langchain-chroma>=0.1.4",
        "chromadb>=0.5.23",
        "faiss-cpu>=1.9.0.post1",
        "sentence-transformers>=3.3.1",
        "torch>=2.5.1",
        "transformers>=4.47.1",
        "pillow>=11.0.0",
        "numpy>=1.26.0",
        "streamlit>=1.41.1",
        "python-dotenv>=1.0.1",
        "requests>=2.32.3",
        "wikipedia>=1.4.0",
        "duckduckgo-search>=7.1.0",
        "tavily-python>=0.5.0",
        "mcp>=1.3.1",
        "llama-cpp-python>=0.3.2",
        "gputil>=1.4.0"
    ],
    extras_require={
        'dev': [
            'pytest',
            'black',
            'flake8'
        ]
    },
    entry_points={
        'console_scripts': [
            'sat-sight-ui=ui.app:main',
        ],
    },
)
