from setuptools import setup, find_packages

setup(
    name="lrbt",
    version="0.1",
    packages=find_packages(),
    description="Private factors and extensions built on top of the RBT framework.",
    author="Chang Liu",
    author_email="",
    url="",
    install_requires=[
        "rbt",
        "pandas",
        "numpy",
        "cvxpy",
    ],
    entry_points={},
)
