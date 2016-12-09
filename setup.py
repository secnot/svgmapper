from setuptools import setup, find_packages


setup(
    name='svgmapper',
    version='0.1',
    description="""SVG mapping library for construction of SVG images
    by concatenating existing ones. Supports placement, scaling and
    rotationg (90 degree)""",
    
    # Main homepage
    url='https://github.com/secnot/svgmapper/',
    
    # Extra info and author details
    author='SecNot',

    keywords=['svg',],

    license='GPLv2',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        ],

    # package
    packages = ['svgmapper'],
    install_requires = ['lxml', 'pgi', 'unittest2', 'nose'],
    zip_safe = False,

    # Tests
    test_suite='nose.collector',
    tests_require=['nose'],
)
