=================
Multi File Widget
=================

Like any widget, the file widgets provide the ``IWidget`` interface:

    >>> from zope.interface.verify import verifyClass
    >>> from z3c.form import interfaces
    >>> from plone.formwidget.multifile import MultiFileWidget
    >>> from plone.formwidget.multifile.interfaces import IMultiFileWidget

    >>> verifyClass(interfaces.IWidget, MultiFileWidget)
    True
    >>> verifyClass(IMultiFileWidget, MultiFileWidget)
    True


The widget can be instantiated only using the request:

    >>> from z3c.form.testing import TestRequest
    >>> request = TestRequest()

    >>> widget = MultiFileWidget(request)

Before rendering a widget, one has to set the name and id of the widget:

    >>> widget.id = 'widget.id.files'
    >>> widget.name = 'widget.name.files'

We also need to register the templates for the widgets:

    >>> import zope.component
    >>> from zope.pagetemplate.interfaces import IPageTemplate
    >>> from z3c.form.widget import WidgetTemplateFactory
    
    >>> def getPath(filename):
    ...     import os.path
    ...     import plone.formwidget.multifile
    ...     return os.path.join(os.path.dirname(plone.formwidget.multifile.__file__), filename)

    >>> zope.component.provideAdapter(
    ...     WidgetTemplateFactory(getPath('input.pt'), 'text/html'),
    ...     (None, None, None, None, IMultiFileWidget),
    ...     IPageTemplate, name=interfaces.INPUT_MODE)

    >>> widget.update()

