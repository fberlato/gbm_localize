from distutils.core import setup, Extension
#from setuptools import find_packages
#import numpy as np




setup(
    name='gbm_localize',
    version='0.1',
    author='Francesco Berlato',
    description='Package for GBM trigger data localization',
    packages=['gbm_localize', 'gbm_localize.utils'],
    requires=['numpy', 'threeML', 'gbm_drm_gen', 'trigdat_reader'],
    #packages=find_packages(exclude=['tests']),
    #include_package_data=True
)
