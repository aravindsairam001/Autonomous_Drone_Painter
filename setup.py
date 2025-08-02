#!/usr/bin/env python3
"""
Setup script for PX4 Autonomous Wall Spray Painting System
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read requirements from requirements.txt
def read_requirements():
    requirements = []
    with open("requirements.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-r"):
                requirements.append(line)
    return requirements

setup(
    name="px4-autonomous-wall-painter",
    version="1.0.0",
    author="aravindsairam001",
    author_email="",
    description="A comprehensive autonomous drone spray painting system for PX4 Autopilot using MAVSDK Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aravindsairam001/Autonomous_Drone_Painter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "isort>=5.9.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "viz": [
            "matplotlib>=3.3.0",
            "numpy>=1.20.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "sphinx-autodoc-typehints>=1.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wall-generator=interactive_wall_generator:main",
            "drone-spawn-updater=update_drone_spawn_pose:main",
            "wall-painter=wall_spray_painting_advanced:main",
        ],
    },
    keywords="px4 drone autonomous painting mavsdk gazebo simulation",
    project_urls={
        "Bug Reports": "https://github.com/aravindsairam001/Autonomous_Drone_Painter/issues",
        "Source": "https://github.com/aravindsairam001/Autonomous_Drone_Painter",
        "Documentation": "https://docs.px4.io/",
        "PX4 Autopilot": "https://github.com/PX4/PX4-Autopilot",
        "MAVSDK Python": "https://github.com/mavlink/MAVSDK-Python",
    },
)
