Introduction
============

`plone.formwidget.multifile` is a z3c.form-widget based on jQuery 
`uploadify <http://www.uploadify.com>`_ plugin, which uses flash for 
uploading.

Using flash makes it possible to select multiple files at once in the file
selection dialog provided by the browser / operating system. After selecting
the files the flash plugin will upload each file by once and the files are
then stored in a draft
(`plone.app.drafts <http://pypi.python.org/pypi/plone.app.drafts>`_). When
submitting the form the converter will get the files from the drafts storage.


Usage
-----

Using the widget is quiet easy::

    >>> from plone.directives import form as directivesform
    >>> from plone.formwidget.multifile.widget import MultiFileFieldWidget
    >>> from plone.namedfile.field import NamedFile
    >>> from zope import schema
    >>> from zope.interface import Interface
    >>> 
    >>> class MySchema(Interface):
    ...     """My schema interface"""
    ...     
    ...     directivesform.widget(files=MultiFileFieldWidget)
    ...     files = schema.List(title=u'Files',
    ...                         value_type=NamedFile())
