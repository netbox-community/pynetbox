from setuptools import setup

setup(
    name='pynetbox',
    version='3.0.0',
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
        'netaddr==0.7.18',
        'requests==2.10.0',
        'six==1.11.0'
    ],
    zip_safe=False,
    keywords=['netbox'],
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

)
