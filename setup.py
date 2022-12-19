# -*- coding: utf-8 -*-
from io import open
from os import path
#from setuptools import setup, find_packages, find_namespace_packages
from setuptools import find_namespace_packages
#from setuptools.extension import Extension
import numpy as np
from distutils.core import setup, Extension
# import pyximport
# pyximport.install()
from Cython.Build import cythonize
from Cython.Compiler.Options import get_directive_defaults
directive_defaults = get_directive_defaults()
directive_defaults['linetrace'] = True
directive_defaults['binding'] = True

here = path.abspath(path.dirname(__file__))
main_util_rel_path = path.join(here,'emccd_detect', 'arcticpy', 'main_utils.pyx')
main_util_rel_path = path.relpath(main_util_rel_path, here)
trap_managers_util_rel_path = path.join(here,'emccd_detect', 'arcticpy', 'trap_managers_utils.pyx')
trap_managers_util_rel_path = path.relpath(trap_managers_util_rel_path, here)
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

link_args = ["-std=c99"]
ext_modules = [
    Extension("emccd_detect.arcticpy.trap_managers_utils", [trap_managers_util_rel_path],#["emccd_detect/arcticpy/trap_managers_utils.pyx"], #[path(here,'emccd_detect', 'arcticpy', 'trap_managers_utils.pyx')],#["arcticpy/trap_managers_utils.pyx"],
            extra_compile_args=link_args,
            extra_link_args=link_args,
            include_dirs=[np.get_include()],
            define_macros=[('CYTHON_TRACE', '1')],
            language='c'),
    Extension("emccd_detect.arcticpy.main_utils", [main_util_rel_path],#["emccd_detect/arcticpy/main_utils.pyx"], #[path(here,'emccd_detect', 'arcticpy', 'main_utils.pyx')],#["arcticpy/main_utils.pyx"],
            extra_compile_args=link_args,
            extra_link_args=link_args,
            include_dirs=[np.get_include()],
            define_macros=[('CYTHON_TRACE', '1')],
            language='c'),
]
ext_modules = cythonize(
    ext_modules, compiler_directives={'language_level': 3})

setup(
    name='emccd_detect',
    version='2.2.5',
    description='EMCCD detector image simulation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.jpl.nasa.gov/WFIRST-CGI/emccd_detect',
    author='Bijan Nemati, Sam Miller, Kevin Ludwick',
    author_email='bijan.nemati@uah.edu, sam.miller@uah.edu, kevin.ludwick@uah.edu',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    #packages=find_namespace_packages('arcticpy.src', 'arcticpy.include'),
    #packages=find_packages(),
    packages=find_namespace_packages(),
    #packages=['arcticpy'],
    package_data={'': ['metadata.yaml']},
    include_package_data=True,
    python_requires= '>=3.6',
    install_requires=[
        #'arcticpy',
        #'arcticpy @ git+https://github.com/jkeger/arctic.git',
        'Cython',
        'astropy',
        'matplotlib',
        'numpy',
        'scipy',
        'pynufft==2020.0.0',
        'pyyaml',
        'autoarray==0.13.4',
        'autoconf==0.6.1',
        'colorcet>=2.0.2',
        #'arcticpy @ git+https://github.com/jkeger/arcticpy.git'
    ],
    ext_modules=ext_modules,

)
