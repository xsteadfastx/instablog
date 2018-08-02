# pylint: disable=missing-docstring
from setuptools import setup

setup(
    name="instablog",
    version="0.0.0",
    py_modules=["instablog"],
    package_dir={"": "src"},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        instablog=instablog:cli
    """
)
