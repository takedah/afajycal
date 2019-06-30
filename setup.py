from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='aoscjycal',
    version='0.1.0',
    description='Calendar of AOSC Junior Youth soccer match schedules',
    long_description=readme,
    author='Hiroki Takeda',
    author_email='takedahiroki@gmail.com',
    install_requires=['requests', 'BeautifulSoup4', 'flask'],
    url='https://github.com/takedah/aoscjycal',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
