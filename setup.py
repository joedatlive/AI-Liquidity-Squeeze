from setuptools import setup, find_packages

setup(
    name="ai_liquidity_squeeze",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'numpy'
    ],
)