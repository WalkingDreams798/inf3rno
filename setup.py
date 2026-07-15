"""Setup script for Inf3rno."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="inf3rno",
    version="2.1.0",
    author="WalkingDreams798",
    author_email="anon@anon.com",
    description="Multi-Protocol Brute-Force Tool for Penetration Testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WalkingDreams798/inf3rno",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "paramiko>=3.0",
        "requests>=2.31",
        "rich>=13.0",
        "colorama>=0.4",
        "tqdm>=4.65",
        "urllib3>=2.0",
        "pymysql>=1.1",
        "pysocks>=1.7",
        "psycopg2-binary>=2.9",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pydantic>=2.0",
    ],
    entry_points={
        "console_scripts": [
            "inf3rno=inf3rno:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["wordlists/*.txt"],
    },
    keywords="bruteforce penetration-testing security ssh ftp http mysql",
    license="MIT",
)
