#!/usr/bin/env python


from glob import glob
from os.path import splitext, basename
from setuptools import find_packages, setup


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


with open('README.md') as readme_file:
    readme = readme_file.read()


requirements = [
    'numpy',
    'pandas',
    'opyenxes',
    'ciso8601',
    'lxml',
    'pygraphviz'
]


test_requirements = [
    'pytest'
]


setup_requirements = [
    'pytest-runner'
]


setup(
    name='podspy',
    version='0.1.2',
    description='A SciKit for process oriented data science',
    long_description_content_type='text/markdown',
    long_description=readme,
    author='Wai Lam Jonathan Lee',
    author_email='walee@uc.cl',
    install_requires=requirements,
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    entry_points={'pytest11': ['podspy = podspy']},
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')]
)
