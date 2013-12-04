from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''

setup(
    name='Sheepdog',
    version='0.1.1',
    author='Adam Greig',
    author_email='adam@adamgreig.com',
    packages=['sheepdog', 'sheepdog.dog', 'sheepdog.sheep'],
    url='http://sheepdog.readthedocs.org',
    license='MIT',
    description='Shepherd GridEngine',
    long_description=long_description,
    test_suite='nose.collector',
    tests_require=['nose', 'requests'],
    install_requires=[
        "Flask >= 0.10.1",
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
