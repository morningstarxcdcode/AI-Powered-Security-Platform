import os

from setuptools import find_packages, setup


def get_requirements():
    """Read requirements from requirements.txt"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            requirements = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove comments and version specifiers for basic compatibility
                    req = line.split('#')[0].strip()
                    if req:
                        requirements.append(req)
            return requirements
    return ['click >= 8.0.0']


def get_long_description():
    """Read long description from README.md"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Advanced Security Reconnaissance CLI Tool"


setup(
    name="scout-cli",
    version="1.0.0",
    description="Advanced Security Reconnaissance CLI Tool",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Scout Team",
    author_email="scout@example.com",
    url="https://github.com/scout-cli/scout",
    packages=find_packages(),
    install_requires=get_requirements(),
    extras_require={
        'dev': [
            'pytest >= 7.0.0',
            'pytest - cov >= 4.0.0',
            'black >= 23.0.0',
            'flake8 >= 6.0.0',
            'mypy >= 1.0.0',
            'bandit >= 1.7.0',
            'safety >= 2.0.0',
        ],
        'test': [
            'pytest >= 7.0.0',
            'pytest - cov >= 4.0.0',
            'pytest - benchmark >= 4.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'scout = scout.cli:cli',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production / Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    keywords="security reconnaissance vulnerability assessment compliance",
    project_urls={
        "Bug Reports": "https://github.com / scout - cli / scout / issues",
        "Source": "https://github.com / scout - cli / scout",
        "Documentation": "https://scout - cli.github.io / scout/",
    },
)
