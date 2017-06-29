from setuptools import setup

setup(
    name='pynetbox',
    version='2.0.1',
    description='A python API for netbox',
    url='https://github.com/digitalocean/pynetbox',
    author='Zach Moody',
    author_email='zmoody@do.co',
    license='Apache2',
    packages=[
        'pynetbox',
        'pynetbox.lib'
    ],
    install_requires=[
        'netaddr',
        'requests'
    ],
    zip_safe=False
)
