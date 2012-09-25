=================
Multi File Widget
=================

Test setup::

    >>> import plone.formwidget.multifile
    >>> from plone.formwidget.multifile.converter import MultiFileConverter
    >>> from plone.formwidget.multifile.widget import MultiFileWidget, MultiFileFieldWidget
    >>> from plone.formwidget.multifile.temporaryfile import TemporaryFileHandler
    >>> from plone.formwidget.multifile.interfaces import IMultiFileWidget
    >>> from plone.namedfile.field import NamedFile
    >>> from zope.interface import Interface, implements
    >>> from zope.interface.verify import verifyClass
    >>> from z3c.form import interfaces
    >>> from z3c.form.testing import TestRequest
    >>> from z3c.form.widget import WidgetTemplateFactory
    >>> import zope.component
    >>> from zope.pagetemplate.interfaces import IPageTemplate
    >>> import os.path
    >>> class MockForm(object):
    ...     context = None
    >>> class MockContext(object):
    ...     implements(Interface)
    >>> zope.component.provideAdapter(TemporaryFileHandler)

Like any widget, the file widgets provide the ``IWidget`` interface::

    >>> verifyClass(interfaces.IWidget, MultiFileWidget)
    True
    >>> verifyClass(IMultiFileWidget, MultiFileWidget)
    True

The widget can be instantiated only using the request::

    >>> request = TestRequest()
    >>> widget = MultiFileWidget(request)

Before rendering a widget, one has to set the name and id of the widget::

    >>> widget.id = 'widget.id.files'
    >>> widget.name = 'widget.name.files'

We also need to register the templates for the widgets::

    >>> def getPath(filename):
    ...     return os.path.join(os.path.dirname(plone.formwidget.multifile.__file__), filename)
    >>> zope.component.provideAdapter(
    ...     WidgetTemplateFactory(getPath('input.pt'), 'text/html'),
    ...     (None, None, None, None, IMultiFileWidget),
    ...     IPageTemplate, name=interfaces.INPUT_MODE)
    >>> widget.update()

Regression tests
----------------

When an AJAX form validation is triggered, the value of the widget is extracted is a list o file
names. We have to make sure ``MultiFileConverter.toFieldValue`` won't break in this situation::

    >>> field = NamedFile(title=u'Some Title')
    >>> widget = MultiFileFieldWidget(field, request)
    >>> widget.form = MockForm()
    >>> widget.form.context = MockContext()
    >>> converter = MultiFileConverter(field, widget)
    >>> converter.toFieldValue([u'', u'filename1.txt', u'filename2.txt'])
    []