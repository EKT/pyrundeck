from setuptools import setup, find_packages

setup(
    name="PyRundeck",
    version="0.3.3alpha",
    description="A thin, pure Python wrapper for the Rundeck API",
    author="Panagiotis Koutsourakis",
    author_email="kutsurak@ekt.gr",
    license='BSD',
    url='https://github.com/EKT/pyrundeck',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet :: REST API client',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='rest api client rundeck',
    packages=find_packages(exclude=['tests', '*_virtualenv', 'doc']),
    install_requires=[
        'lxml>=3.4.4',
        'requests>=2.7.0',
        'pyopenssl>=0.15.1',
        'ndg-httpsclient>=0.4.0',
        'pyasn1>=0.1.8'
    ]
)
