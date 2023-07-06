
from pathlib import Path
from setuptools import find_namespace_packages, setup

# Load packages from requirements.txt
BASE_DIR = Path(__file__).parent
with open(Path(BASE_DIR, 'requirements.txt'), 'r') as file:
    required_packages = [ln.strip() for ln in file.readlines()]

test_packages = [
    'pytest~=7.1.2',
    'pytest-env~=0.6.2',
]

# Define our package
setup(
    name='timelines',
    version=0.1,
    description='Get the big picture of the news',
    author='Kelvin Ou',
    author_email='kelvin.ou.jin.bin@gmail.com',
    url='https://readtimelines.com/',
    python_requires=">=3.9",
    packages=find_namespace_packages(),
    install_requires=[required_packages],
    extras_require={
        'dev': test_packages,
        'test': test_packages
    }
)
