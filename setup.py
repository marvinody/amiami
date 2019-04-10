import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='amiami',
    version='0.0.1',
    author='marvinody',
    author_email='manny@sadpanda.moe',
    description='amiami lame api scraper that works through the api',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://bitbucket.org/marvinody/amiami/',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
    ]
)
