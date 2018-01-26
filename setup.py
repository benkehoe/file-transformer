from setuptools import setup

setup(
    name='file-transformer',
    version='0.1.0',
    description='Helper main for executables that transform files and/or stdin/stdout',
    py_modules=['file_transformer'],
    author='Ben Kehoe',
    author_email='bkehoe@irobot.com',
    project_urls={
        "https://github.com/benkehoe/file-transformer",
    },
    license='Apache Software License 2.0',
    classifiers=(
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License',
    ),
)