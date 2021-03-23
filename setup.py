import setuptools
from setuptools import setup

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()
with open("requirements.txt", "r") as f:
    REQUIREMENTS = f.read().splitlines()

DESCRIPTION = "This is a plotter of Arduino."

setup(
    name="TLTester",
    version="0.1.0",
    author="5yutan5",
    author_email="4yutan4@gmail.com",
    description=DESCRIPTION,
    longdescription=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/5yutan5/ArduinoPlotter",
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    dependency_links=["git@git+https://github.com/pyqtgraph/pyqtgraph"],
    entry_points={"gui_scripts": ["ArduinoPlotter = main:main"]},
    python_requires=">=3.9",
)
