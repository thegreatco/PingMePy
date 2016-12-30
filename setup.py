from distutils.core import setup

setup(
    name='PingMePy',
    packages=['PingMePy'],
    version='0.5',
    description='A wrapper library around the MongoDB OpsManager / Cloud Manager API',
    author='TheGreatCO',
    author_email='thegreatco@thegreatco.com',
    url='https://github.com/thegreatco/PingMePy',
    keywords=['mms', 'cloud', 'opsmanager', 'cloudmanager', 'mongodb'],
    classifiers=[],
    requires=['requests'],
    install_requires=['requests']
)
__author__ = 'TheGreatCO'
