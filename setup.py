#!/usr/bin/env python


from glob import glob
from os.path import splitext, basename
from setuptools import find_packages, setup


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


with open('README.md') as readme_file:
    readme = readme_file.read()


requirements = [
    'numpy>=1.15.4',
    'pandas>=0.23.4',
    'opyenxes>=0.3.0',
    'ciso8601>=2.1.1',
    'lxml>=4.2.5',
    'pygraphviz>=1.5'
]


test_requirements = [
    'pytest>=4.0.2'
]


setup_requirements = [
    'pytest-runner>=4.2'
]


setup(
    name='podspy',
    version='0.1.5',
    description='A SciKit for process oriented data science',
    long_description_content_type='text/markdown',
    long_description=readme,
    author='Wai Lam Jonathan Lee',
    author_email='walee@uc.cl',
    include_package_data=True,
    install_requires=requirements,
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    zip_safe=False,
    test_suite='tests',
    entry_points={'pytest11': ['podspy = podspy']},
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')]
)
