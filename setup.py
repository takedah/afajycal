from setuptools import setup, find_packages


with open("README.rst") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="afajycal",
    version="0.1.1",
    description="Calendar of AFA Junior Youth soccer match schedules",
    long_description=readme,
    author="Hiroki Takeda",
    author_email="takedahiroki@gmail.com",
    install_requires=[
        "BeautifulSoup4",
        "flask",
        "gunicorn",
        "numpy",
        "pandas",
        "psycopg2",
        "requests",
        "xlrd",
    ],
    url="https://github.com/takedah/afajycal",
    license=license,
    packages=find_packages(exclude=("tests", "docs")),
)
