#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="dollarslice",
    version="1.0.0",
    description="A library for solving problems with LLMs and function calls",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "httpx",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "dollarslice=dollarslice.__main__:main",
        ],
    },
)
