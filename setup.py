from setuptools import setup, find_packages

try:
    with open("requirements.txt") as f:
        install_reqs = f.read().splitlines()
except:
    install_reqs = []

setup(
    name="PyPPLCompiler",
    version="0.",
    packages=find_packages(),
    url="https://github.com/Tobias-Kohn/PyPPLCompiler",
    license="GPL-3.0",
    install_requires=install_reqs,
)