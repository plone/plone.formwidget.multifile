Introduction
============

.. image:: https://secure.travis-ci.org/plone/plone.formwidget.multifile.svg?branch=master
       :target: http://travis-ci.org/plone/plone.formwidget.multifile

.. image:: https://coveralls.io/repos/plone/plone.formwidget.multifile/badge.svg?branch=master
       :target: https://coveralls.io/r/plone/plone.formwidget.multifile

.. image:: https://img.shields.io/pypi/dm/plone.formwidget.multifile.svg
       :target: https://pypi.python.org/pypi/plone.formwidget.multifile/
    :alt: Downloads

.. image:: https://img.shields.io/pypi/v/plone.formwidget.multifile.svg
       :target: https://pypi.python.org/pypi/plone.formwidget.multifile/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/plone.formwidget.multifile.svg
       :target: https://pypi.python.org/pypi/plone.formwidget.multifile/
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/l/plone.formwidget.multifile.svg
       :target: https://pypi.python.org/pypi/plone.formwidget.multifile/
    :alt: License


`plone.formwidget.multifile` is a z3c.form-widget which lets users
upload multiple files, either at once, or in batches using repeated form
submissions.

Browsers that do not implement the file input "multiple" attribute are
supported via javascript adding of multiple file inputs. This also works 
with browsers that do support "multiple", and allows users to add and 
remove files in bundles. Upload does not occur until the form is saved. 


Usage
-----

Using the widget is quite easy::

    >>> from plone.directives import form as directivesform
    >>> from plone.formwidget.multifile import MultiFileFieldWidget
    >>> from plone.namedfile.field import NamedFile
    >>> from zope import schema
    >>> from zope.interface import Interface
    >>> 
    >>> class IMySchema(Interface):
    ...     """My schema interface"""
    ...     
    ...     directivesform.widget(files=MultiFileFieldWidget)
    ...     files = schema.List(title=u'Files',
    ...                         value_type=NamedFile())


Limitations
-----------

We do not yet support ordering.
There is no fallback for non-html5, non-javascript browsers. They will
only be able to upload 1 file at a time.

