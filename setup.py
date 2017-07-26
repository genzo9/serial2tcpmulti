from setuptools import setup, find_packages

setup(
    name='serial2tcpmulti',
    version='1.0',
    url='https://github.com/genzo9/serial2tcpmulti',
    license='Public Domain',
    packages=find_packages(),
    scripts=['serial2tcpmulti.py'],
    install_requires = ['pyserial-asyncio'],
)
