Introduction
============

.. image:: https://coveralls.io/repos/github/plone/plone.formwidget.multifile/badge.svg?branch=master
   :target: https://coveralls.io/github/plone/plone.formwidget.multifile?branch=master


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
