from setuptools import setup
from facebook_sdk import __VERSION__

readme = open('README.rst').read()
history = open('CHANGELOG.md').read()

setup(
    name='facebook-sdk-python',
    version=__VERSION__,
    description='Facebook Python SDK',
    long_description=readme + '\n\n' + history,
    license="MIT",
    author='Zeta Hernandez',
    author_email='zetahernandez@gmail.com',
    url='http://github.com/zetahernandez/facebook-python-sdk',
    packages=['facebook_sdk'],
    install_requires=['requests >=0.8', 'six >= 1.6'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
)