from setuptools import setup, find_packages

setup(
    name='cloud_ip_checker',
    version='0.1',
    packages=find_packages(),
    package_data={'cloud_ip_checker': ['cloud_ip_data/*']},
    install_requires=[],
)

