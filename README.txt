Introduction
============

`plone.formwidget.multifile` is a z3c.form-widget which lets users
upload multiple files, either at once, or in batches using repeat form
submissions.

The widget relies on `plone.app.drafts` to save uploaded files into a
temporary container. This is transparent to the user.


Usage
-----

Using the widget is quiet easy::

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

Some browsers do not support uploading multiple files using HTML.
