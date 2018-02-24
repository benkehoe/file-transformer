from setuptools import setup

def find_version(name):
    import os.path, codecs, re
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, name), 'r') as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='file-transformer',
    version=find_version('file_transformer.py'),
    description='Helper main for executables that transform files and/or stdin/stdout',
    py_modules=['file_transformer'],
    author='Ben Kehoe',
    author_email='bkehoe@irobot.com',
    project_urls={
        "Source code": "https://github.com/benkehoe/file-transformer",
    },
    license='Apache Software License 2.0',
    classifiers=(
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: Apache Software License',
    ),
)