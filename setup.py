from distutils.core import setup


setup(
    name='gbm_localize',
    version='0.1',
    author='Francesco Berlato',
    description='Package for GBM trigger data localization',
    packages=['gbm_localize', 'gbm_localize.utils'],
    requires=['numpy', 'threeML', 'gbm_drm_gen', 'trigdat_reader'],
    #package_dir={'gbm_localize': 'gbm_localize'},
    package_data={'gbm_localize': ['nb_templates/*.ipynb']}
    #include_package_data=True
)
