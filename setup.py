from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''

def get_version():
    with open("sheepdog/__init__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return line[15:-2]
    raise Exception("Could not find version number")

setup(
    name='Sheepdog',
    version=get_version(),
    author='Adam Greig',
    author_email='adam@adamgreig.com',
    packages=['sheepdog'],
    url='http://sheepdog.readthedocs.org',
    license='MIT',
    description='Shepherd GridEngine',
    long_description=long_description,
    test_suite='nose.collector',
    tests_require=['nose', 'requests'],
    install_requires=[
        "Flask >= 0.10.1",
        "requests >= 2.0.1",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering',
    ],
)
