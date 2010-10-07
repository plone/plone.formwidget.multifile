from setuptools import setup, find_packages
import os

version = '1.0a1'

tests_require = [
    'zope.app.testing',
    ]

setup(name='plone.formwidget.multifile',
      version=version,
      description="z3c.form widget for adding multiple files",
      long_description=open("README.txt").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Jonas Baumann',
      author_email='j.baumann@4teamwork.ch',
      url='http://svn.plone.org/svn/plone/plone.formwidget.multifile',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.formwidget'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'z3c.form',
        'setuptools',
        'plone.z3cform',
        'plone.namedfile',
        'plone.formwidget.namedfile',
        'plone.app.drafts',
        'simplejson',
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
