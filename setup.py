from setuptools import setup, find_packages


def extract_requirements(filename):
    with open(filename, 'r') as requirements_file:
        return [x[:-1] for x in requirements_file.readlines()]

install_requires = extract_requirements('requirements.txt')

setup(
    name="bridge_common",
    version="0.1",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    url="http://www.redhat.com",
    author="Rohan Kanade.",
    author_email="rkanade@redhat.com",
    license="LGPL-2.1+",
    zip_safe=False,
    install_requires=install_requires
)