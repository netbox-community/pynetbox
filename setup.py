from setuptools import setup

setup(
    name='pynetbox',
    description='NetBox API client library',
    url='https://github.com/digitalocean/pynetbox',
    author='Zach Moody',
    author_email='zmoody@do.co',
    license='Apache2',
    include_package_data=True,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=[
        'pynetbox',
        'pynetbox.lib'
    ],
    install_requires=[
        'netaddr==0.*',
        'requests==2.*',
        'six==1.*',
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
