from setuptools import setup, find_packages

setup(
    name="pynetbox",
    description="NetBox API client library",
    url="https://github.com/netbox-community/pynetbox",
    author="Zach Moody",
    author_email="zmoody@do.co",
    license="Apache2",
    include_package_data=True,
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    packages=find_packages(exclude=["tests", "tests.*"]),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        "requests>=2.20.0,<3.0",
        "packaging<24.0"
    ],
    zip_safe=False,
    keywords=["netbox"],
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
