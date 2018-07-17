import os
import glob
from setuptools import setup, find_packages
from subprocess import check_output
from subprocess import CalledProcessError

setup_path = os.path.dirname(__file__)

def read(fname):
    return open(os.path.join(setup_path, fname),encoding="utf8").read()

REPO_URL = "https://github.com/biothings/biothings.api"

# get version
version = __import__('biothings').get_version()

# should fail if installed from source or from pypi,
# version gets set to MAJOR.MINOR.# commits on master branch if installed from pip repo
# otherwise to MAJOR.MINOR.MICRO as defined in biothings.version
try:
    num_commits = check_output("git rev-list --count master", shell=True).decode('utf-8').strip('\n')
except:
    num_commits = ''

# Calculate commit hash, should fail if installed from source or from pypi
try:
    commit_hash = check_output("git rev-parse HEAD", shell=True).decode('utf-8').strip('\n')
except CalledProcessError:
    commit_hash = ''

# Write commit to file inside package, that can be read later
if commit_hash or num_commits:
    with open('biothings/.git-info', 'w') as git_file:
        git_file.write("{}.git\n{}\n{}".format(REPO_URL, commit_hash, num_commits))

install_requires = [
    'requests==2.8.1',
    'tornado==4.5.3',
    'elasticsearch>=6.1.1',
]
hub_requires = [
    'beautifulsoup4',
    'aiocron',
    'asyncssh==1.7.1',
    'pymongo',
    'psutil',
    'jsonpointer',
    'IPython',
    'boto',
    'multiprocessing_on_dill',
    'pyinotify',
    'sockjs-tornado==1.0.3'
]

setup(
    name="biothings",
    version=version,
    author="Cyrus Afrasiabi, Sebastien Lelong, Chunlei Wu",
    author_email="cwu@scripps.edu",
    description="a toolkit for building high-performance data APIs in biology",
    license="Apache License, Version 2.0",
    keywords="biology annotation web service client api",
    url=REPO_URL,
    packages=find_packages(),
    include_package_data=True,
    scripts=list(glob.glob('biothings/bin/*')),
    long_description=read('README.md'),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Utilities",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    install_requires=install_requires,
    extras_require={
        'hub': hub_requires,
        'dev':  hub_requires + ['sphinx' + 'sphinx_rtd_theme']
    },
)
