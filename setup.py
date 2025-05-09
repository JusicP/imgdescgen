from setuptools import setup, find_packages

setup(
    name='imgdescgenlib',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'pyexiftool>=0.5.6', 'requests>=2.32.3', 'pillow>=11.1.0', 'pytest>=8.3.5', 'pydantic-settings>=2.8.1',
    ],
)