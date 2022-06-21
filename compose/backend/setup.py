from setuptools import find_packages, setup

setup(
    name="backend",
    version="0.0.1",
    description="Sample backend application",
    install_requires=[
        "flask==2.1.2",
        "psycopg2-binary==2.9.3",
        "Flask==2.1.2",
        "dataclasses==0.6",
        "numpy==1.22.4",
        "pandas==1.4.2",

    ],
    packages=find_packages(),
)
