import io
from setuptools import setup
from facebook_sdk import __version__

with io.open('README.rst', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

tests_require = [
    'coveralls',
    'pytest >= 4.1; python_version > "3.5"',
    'pytest-cov',
]

setup(
    name='facebook-py-sdk',
    version=__version__,
    description='Facebook Python SDK',
    long_description=readme,
    license="MIT",
    author='Zeta Hernandez',
    author_email='zetahernandez@gmail.com',
    url='https://github.com/eventbrite/facebook-py-sdk',
    packages=['facebook_sdk'],
    package_data={'facebook_sdk': ['py.typed']},
    install_requires=[
        'requests >=0.8',
        'six',
        'typing;python_version<"3.5"'
    ],
    tests_require=tests_require,
    extras_require={
        'testing': tests_require,
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
