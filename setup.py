from setuptools import setup

setup(
    name='pynetbox',
    version='2.0.4',
    description='NetBox API client library',
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
    zip_safe=False,
    keywords=['netbox'],
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

)
