import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='amiami',
    version='0.0.9',
    author='marvinody',
    author_email='manny@amiami.sadpanda.moe',
    description='amiami api wrapper',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/marvinody/amiami',
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.10",
    ]
)
