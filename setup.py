from setuptools import setup
from mangaloid_instance import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='Mangaloid Instance',
    version=str(version.VERSION),
    author="a-manga-thing",
    description="Reference instance software for mangaloid",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a-manga-thing",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
    ],
    install_requires=open("requirements.txt", "r").readlines()
)

