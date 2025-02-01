from setuptools import setup

setup(
    name='imgdescgenlib',
    version='1.0',
    packages=['imgdescgenlib', 'imgdescgenlib/chatbot'],
    install_requires=[
        'pyexiftool', 'requests', 'pillow'
    ],
)