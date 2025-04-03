from setuptools import setup

setup(
    name='imgdescgenlib',
    version='1.0',
    packages=['imgdescgenlib', 'imgdescgenlib/chatbot'],
    install_requires=[
        'pyexiftool>=0.5.6', 'requests>=2.32.3', 'pillow>=11.1.0', 'pytest>=8.3.5'
    ],
)