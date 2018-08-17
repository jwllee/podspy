#!/usr/bin/env python


from glob import glob
from os.path import splitext, basename
from setuptools import find_packages, setup


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


setup(
    name='podspy',
    version='0.1.0',
    description='A SciKit for process oriented data science',
    author='Wai Lam Jonathan Lee',
    author_email='walee@uc.cl',
    install_requires=['numpy', 'pandas', 'opyenxes', 'sortedcontainers'],
    tests_require=['pytest'],
    entry_points={'pytest11': ['podspy = podspy']},
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')]
)
