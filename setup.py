from setuptools import setup, find_packages

setup(
    name="phecs",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    description="A grug-brained ecs for python. Inspired by HECS (rust).",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wegfawefgawefg/phecs",
    author="Gibson Martin",
    author_email="668es218pur@gmail.com",
    license="GPLv3",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 4 - Beta",
        "Topic :: Games/Entertainment",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
)
