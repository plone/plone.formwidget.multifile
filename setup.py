from setuptools import find_packages
from setuptools import setup


version = '2.1.dev0'

tests_require = [
    'zope.app.testing',
    ]

setup(name='plone.formwidget.multifile',
      version=version,
      description="z3c.form widget for adding multiple files",
      long_description=open("README.rst").read() + "\n" + \
          open("CHANGES.rst").read(),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        ],
      keywords='',
      author='Jonas Baumann',
      author_email='j.baumann@4teamwork.ch',
      url='https://github.com/plone/plone.formwidget.multifile',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.formwidget'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'six',
        'z3c.form',
        'setuptools',
        'plone.z3cform',
        'plone.namedfile',
        'plone.formwidget.namedfile',
        'Products.CMFPlone',
        # -*- Extra requirements: -*-
        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
