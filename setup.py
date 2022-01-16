import os

from setuptools import setup, find_packages


def read(f_name):
    return open(os.path.join(os.path.dirname(__file__), f_name)).read()


setup(
    name='nwg-shell-config',
    version='0.1.3',
    description='nwg-shell configuration utility',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["glade/*", "panel/*", "executors/*", "drawer/*", "dock/*", "bar/*", "wrapper/*", "shell/*"]
    },
    url='https://github.com/nwg-piotr/nwg-shell-config',
    license='MIT',
    author='Piotr Miller',
    author_email='nwg.piotr@gmail.com',
    python_requires='>=3.5.0',
    install_requires=[],
    entry_points={
        'gui_scripts': [
            'nwg-shell-config = nwg_shell_config.main:main'
        ]
    }
)
