from setuptools import setup, find_packages


setup(
    name='coxeter',
    version='0.1',
    py_modules=find_packages(),
    install_requires=[
        'click',
        'pillow',
        'tqdm',
    ],
    entry_points='''
        [console_scripts]
        coxeter=bin.save:main
    ''',
)
