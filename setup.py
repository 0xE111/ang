import setuptools
from pathlib import Path


setuptools.setup(
    name="ang",
    version="0.0.1",
    author="Alex",
    author_email="alex@alpha.dev",
    description="",
    long_description=Path('README.md').read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/c0ntribut0r/ang",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    python_requires='>=3.7',
)
