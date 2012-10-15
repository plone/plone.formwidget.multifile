=================
Multi File Widget
=================

Test setup::

    >>> import plone.formwidget.multifile
    >>> from plone.formwidget.multifile.converter import MultiFileConverter
    >>> from plone.formwidget.multifile.widget import MultiFileWidget, MultiFileFieldWidget
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
    >>> from z3c.form.interfaces import IDataManager
    >>> from ZPublisher.HTTPRequest import FileUpload
    >>> from cgi import FieldStorage
    >>> from tempfile import TemporaryFile
    >>> class IMockContent(Interface):
    ...     file = NamedFile(title=u'A file field')
    >>> class IMockContainer(Interface):
    ...     pass
    >>> class MockForm(object):
    ...     context = None
    >>> class MockContent(object):
    ...     implements(IMockContent)
    >>> class MockContainer(object):
    ...     implements(IMockContainer)
    >>> def create_upload(data, filename):
    ...     fp = TemporaryFile('w+b')
    ...     fp.write(data)
    ...     fp.seek(0)
    ...     env = {'REQUEST_METHOD':'PUT'}
    ...     headers = {'content-type':'text/plain',
    ...                'content-length': str(len(data)),
    ...                'content-disposition':'attachment; filename=%s' % filename}
    ...     return FileUpload(FieldStorage(fp=fp, environ=env, headers=headers))

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

AJAX form validation makes ``MultiFileConverter.toFieldValue`` break
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When an AJAX form validation is triggered, the value of the widget is extracted is a list of file
names. We have to make sure ``MultiFileConverter.toFieldValue`` won't break in this situation::

    >>> widget = MultiFileFieldWidget(IMockContent['file'], request)
    >>> widget.form = MockForm()
    >>> widget.context = MockContent()
    >>> widget.form.context = MockContent()
    >>> converter = MultiFileConverter(IMockContent['file'], widget)
    >>> converter.toFieldValue([u'', u'filename1.txt', u'filename2.txt'])
    []

AJAX form validation on object creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When creating an object (when using plone.app.dexterity, for example) the context of the widget is
a container, not an object. When an AJAX form validation is triggered the
``MultiFileConverter.toFieldValue`` must not try to extract the current value from the context,
else it will break, because the context is no suitable::

    >>> class DataManagerWithError(object):
    ...     implements(IDataManager)
    ...     def __init__(self, *args, **kwargs):
    ...         pass
    ...     def query(self, *args, **kwargs):
    ...         raise RuntimeError('Error !')
    >>> zope.component.provideAdapter(
    ...     factory=DataManagerWithError,
    ...     adapts=(IMockContainer, Interface),
    ...     provides=IDataManager
    ... )
    >>> widget = MultiFileFieldWidget(IMockContent['file'], request)
    >>> widget.form = MockForm()
    >>> widget.context = MockContainer()
    >>> widget.form.context = MockContainer()
    >>> converter = MultiFileConverter(IMockContent['file'], widget)
    >>> converter.toFieldValue([u''])
    []
    >>> files = converter.toFieldValue([create_upload('content', 'test.txt')])
    >>> files[0].filename
    u'test.txt'

Filename contains full path
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Internet Explorer <= 7 sends the full path of the file being uploaded, including directories.
``MultiFileConverter.toFieldValue`` must strip the directories and leave only the file name::

    >>> up1 = create_upload('abc', 'c:\\foo\\bar\\test.txt')
    >>> up2 = create_upload('xyz', 'test.txt')
    >>> widget = MultiFileFieldWidget(IMockContent['file'], request)
    >>> widget.form = MockForm()
    >>> widget.context = MockContent()
    >>> widget.form.context = MockContent()
    >>> converter = MultiFileConverter(IMockContent['file'], widget)
    >>> files = converter.toFieldValue([up1, up2])
    >>> files[0].filename
    u'test.txt'
    >>> files[1].filename
    u'test.txt'

