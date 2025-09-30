from setuptools import setup, find_packages

setup(
    name="author-parser",
    version="0.1.0",
    description="Package for extracting author information from source code",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "llama-index",
        "llama-index-llms-ollama",
        "llama-index-embeddings-ollama",
        "pydantic",
        "comment-parser",
        "plac",
        "loguru",
    ],
    entry_points={
        "console_scripts": [
            "package-author-parser=author_parser.package_author_parser:main",
        ],
    },
)