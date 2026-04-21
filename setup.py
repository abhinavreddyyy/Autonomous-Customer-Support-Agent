from setuptools import setup, find_packages

setup(
    name="autonomous-support-agent",
    version="1.0.0",
    description="Autonomous Customer Support Agent using LangChain and OpenAI",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.14",
    install_requires=[
        "langchain>=0.3.0",
        "langchain-openai>=0.3.0",
        "langchain-community>=0.3.0",
        "openai>=1.50.0",
        "faiss-cpu>=1.8.0",
        "sentence-transformers>=3.0.0",
        "pandas>=2.2.0",
        "numpy>=2.1.0",
        "python-dotenv>=1.1.0",
        "pydantic>=2.10.0",
        "requests>=2.32.0",
    ],
    entry_points={
        "console_scripts": [
            "support-agent=main:main",
        ],
    },
)