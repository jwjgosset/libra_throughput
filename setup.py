from setuptools import setup  # type: ignore
from setuptools import find_packages

setup(
    name='libra_metrics',
    version='0.1.0',
    description=('Plugin to acquire metrics about libra comms from Apollo \
        Server and feed them to Nagios as check results'),
    author='Jonathan Gosset',
    author_email='jonathan.gosset@nrcan-rncan.gc.ca',
    packages=find_packages(exclude=('tests')),
    package_data={
        'acquisition_nagios': [
            'data/*.config'
        ]
    },
    python_requires='>3.6',
    # Requires python packages
    install_requires=[
        'requests',
        'click',
        'dataclasses'
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'mypy'
        ]
    },
    entry_points={
        'console_scripts': [
            'check_libra_metrics = \
                libra_metrics.bin.check_libra_metrics:main'
        ]
    }
)
