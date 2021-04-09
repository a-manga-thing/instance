from setuptools import setup, find_packages
from mangaloid_instance import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mangaloid-instance',
    version=str(version.VERSION),
    author="a-manga-thing",
    description="Reference instance software for mangaloid",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a-manga-thing",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
    ],
    install_requires=open("requirements.txt", "r").read().splitlines(),
    entry_points={
        'console_scripts': [
            'mangaloid-instance=mangaloid_instance.main:run',
        ],
    },
)
