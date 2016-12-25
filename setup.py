from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name='coxeter',
    version='0.1',
    py_modules=["coxeter", "coxeter.scripts.save"],
    ext_modules = cythonize("coxeter/coxeter.pyx"),
    install_requires=[
        'click',
        'pillow',
        'tqdm',
    ],
    entry_points='''
        [console_scripts]
        coxeter=coxeter.scripts.save:main
    ''',
)
