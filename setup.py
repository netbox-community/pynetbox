from setuptools import setup, find_packages

setup(
    version='6.6.2.test',
    name="kani-fork-pynetbox",
    description="NetBox API client library",
    url="https://github.com/kani999/pynetbox",
    author="Zach Moody",
    author_email="zmoody@do.co",
    license="Apache2",
    include_package_data=True,
    #use_scm_version=True,
    #setup_requires=["setuptools_scm"],
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "requests>=2.20.0,<3.0",
        "six==1.*",
    ],
    zip_safe=False,
    keywords=["netbox"],
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
