from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="devlog",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI tool for tracking developer work sessions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/devlog",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "devlog=devlog.cli:cli",
        ],
    },
)
