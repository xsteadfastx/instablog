# pylint: disable=missing-docstring
from setuptools import setup

setup(
    name="instablog",
    version="0.0.0",
    packages=["instablog"],
    package_dir={"": "src"},
    package_data={"instablog": ["data/blogentry.md.j2"]},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        instablog=instablog.cli:main
    """,
)
