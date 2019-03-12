# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack


import os
import re
import shutil
from pip._internal import main as pip_main

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import setuptools

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
SOURCE_PATH = os.path.join(ROOT_PATH, 'source')
README_PATH = os.path.join(ROOT_PATH, 'README.rst')


HOOK_PATH = os.path.join(
    ROOT_PATH, 'hook'
)

RESOURCE_PATH = os.path.join(
    ROOT_PATH, 'resource'
)

BUILD_PATH = os.path.join(
    ROOT_PATH, 'build'
)


# Read version from source.
with open(os.path.join(
    SOURCE_PATH, 'ftrack_connect_pipeline_definition', '_version.py')
) as _version_file:
    VERSION = re.match(
        r'.*__version__ = \'(.*?)\'', _version_file.read(), re.DOTALL
    ).group(1)

STAGING_PATH = os.path.join(
    BUILD_PATH, 'ftrack-connect-pipeline-definition-{}'.format(VERSION)
)


class BuildPlugin(setuptools.Command):
    '''Build plugin.'''

    description = 'Download dependencies and build plugin .'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        '''Run the build step.'''
        # Clean staging path
        shutil.rmtree(STAGING_PATH, ignore_errors=True)

        # Copy resource files
        shutil.copytree(
            RESOURCE_PATH,
            os.path.join(STAGING_PATH, 'resource')
        )

        # Copy hook files
        shutil.copytree(
            HOOK_PATH,
            os.path.join(STAGING_PATH, 'hook')
        )

        pip_main(
            [
                'install',
                '.',
                '--target',
                os.path.join(STAGING_PATH, 'dependencies'),
                '--process-dependency-links'
            ]
        )

        result_path = shutil.make_archive(
            os.path.join(
                BUILD_PATH,
                'ftrack-connect-pipeline-definition-{0}'.format(VERSION)
            ),
            'zip',
            STAGING_PATH
        )

        print 'Result: ' + result_path


# Custom commands.
class PyTest(TestCommand):
    '''Pytest command.'''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        '''Import pytest and run.'''
        import pytest
        errno = pytest.main(self.test_args)
        raise SystemExit(errno)


# Configuration.
setup(
    name='ftrack-connect-pipeline-definition',
    version=VERSION,
    description='Collection of definitions of package and packages.',
    long_description=open(README_PATH).read(),
    keywords='ftrack',
    url='https://bitbucket.org/ftrack/ftrack-connect-pipeline-definition',
    author='ftrack',
    author_email='support@ftrack.com',
    license='Apache License (2.0)',
    packages=find_packages(SOURCE_PATH),
    package_dir={
        '': 'source'
    },
    setup_requires=[
        'sphinx >= 1.2.2, < 2',
        'sphinx_rtd_theme >= 0.1.6, < 2',
        'lowdown >= 0.1.0, < 2',
    ],
    tests_require=[
        'pytest >= 2.3.5, < 3'
    ],
    cmdclass={
        'test': PyTest,
        'build_plugin': BuildPlugin
    },
    zip_safe=False
)