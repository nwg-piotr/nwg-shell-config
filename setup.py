import os

from setuptools import setup, find_packages


def read(f_name):
    return open(os.path.join(os.path.dirname(__file__), f_name)).read()


setup(
    name='nwg-shell-config',
    version='0.4.20',
    description='nwg-shell configuration utility',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["glade/*", "langs/*", "shell/*", "updates/*"]
    },
    url='https://github.com/nwg-piotr/nwg-shell-config',
    license='MIT',
    author='Piotr Miller',
    author_email='nwg.piotr@gmail.com',
    python_requires='>=3.5.0',
    install_requires=[],
    entry_points={
        'gui_scripts': [
            'nwg-shell-config = nwg_shell_config.main:main',
            'nwg-lock = nwg_shell_config.locker:main',
            'nwg-shell-help = nwg_shell_config.help:main',
            'nwg-autotiling = nwg_shell_config.autotiling:main',
            'nwg-shell-updater = nwg_shell_config.updater:main',
            'nwg-shell-translate = nwg_shell_config.translate:main',
            'nwg-update-indicator = nwg_shell_config.update_indicator:main'
        ]
    }
)
