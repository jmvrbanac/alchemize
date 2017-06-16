from setuptools import setup, find_packages

requirements = ['six']

desc = ''
with open('README.rst') as f:
    desc = f.read()

setup(
    name='alchemize',
    version='0.6.0',
    description=('A simple library that allows for serialization and '
                 'deserialization of models via mapping definitions'),
    long_description=(desc),
    url='https://github.com/jmvrbanac/alchemize',
    author='John Vrbanac',
    author_email='john.vrbanac@linux.com',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: POSIX :: Linux'
    ],
    keywords='model serialize deserialize transmute',
    packages=find_packages(exclude=['contrib', 'docs', 'spec*']),
    install_requires=requirements,
    package_data={},
    data_files=[],
    entry_points={}
)
