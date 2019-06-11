from Acquisition import aq_inner
from plone.formwidget.multifile.interfaces import IMultiFileWidget
from plone.formwidget.multifile.utils import get_icon_for
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data
from Products.Five.browser import BrowserView
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IDataManager
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import NO_VALUE
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound


@implementer(IMultiFileWidget)
class MultiFileWidget(Widget):

    klass = u'multi-file-widget'

    input_template = ViewPageTemplateFile('input.pt')
    display_template = ViewPageTemplateFile('display.pt')
    file_template = ViewPageTemplateFile('file_template.pt')

    def render(self):
        if self.mode == 'input':
            return self.input_template(self)
        else:
            return self.display_template(self)

    def editing(self):
        return self.mode == 'input'

    def get_data(self):
        """Return an iterable of HTML snippets representing the files already
        stored on the context and allowing to download it.
        If the widget is in input mode then removal is allowed too.
        """
        if IAddForm.providedBy(self.form):
            return

        dm = queryMultiAdapter((self.context, self.field), IDataManager)
        if dm is None:
            return

        field_value = dm.query()
        if not field_value:
            return

        for i, value in enumerate(field_value):
            form_value = 'index:%s' % i
            download_url = '%s/++widget++%s/@@download/%i' % (
                self.request.getURL(),
                self.name,
                i)

            yield self.render_file(form_value, value, download_url)

    def render_file(self, form_value, file_, download_url):
        """Renders the <li> for one file.
        """
        form_context = self.form.context

        try:
            size = file_.getSize()
        except AttributeError:
            size = file_.tell()

        options = {'value': form_value,
                   'icon': '/'.join((form_context.portal_url(),
                                     get_icon_for(form_context, file_))),
                   'filename': file_.filename,
                   'size': int(round(size / 1024)),
                   'download_url': download_url,
                   'widget': self,
                   'editable': self.mode == 'input',
                   }

        return self.file_template(**options)

    def extract(self, default=NO_VALUE):
        """Extract all real FileUpload objects.
        """
        try:
            # only return real uploads and indexes for files already present,
            # not files created for empty input fields
            return [f for f in self.request[self.name] if f]
        except KeyError:
            # no value stored on the request
            return default

@implementer(IFieldWidget)
def MultiFileFieldWidget(field, request):
    return FieldWidget(field, MultiFileWidget(request))


@implementer(IPublishTraverse)
class Download(BrowserView):
    """Download a file via ++widget++widget_name/@@download/filename"""

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.file_index = None
        self.content = None

    def publishTraverse(self, request, name):

        try:
            if self.file_index is None: # ../@@download/file_index
                self.file_index = int(name)
                return self
            elif self.file_index == name:
                return self
        except ValueError:
            # NotFound raised below
            pass

        raise NotFound(self, name, request)

    def __call__(self):

        if self.context.ignoreContext:
            raise NotFound("Cannot get the data file from a widget with no context")

        if self.context.form is not None:
            content = aq_inner(self.context.form.getContent())
        else:
            content = aq_inner(self.context.context)
        field = aq_inner(self.context.field)

        dm = getMultiAdapter((content, field,), IDataManager)
        file_list = dm.get()
        try:
            file_ = file_list[self.file_index]
        except (IndexError, TypeError):
            raise NotFound(self, self.file_index, self.request)

        filename = getattr(file_, 'filename', '')

        set_headers(file_, self.request.response, filename=filename)
        return stream_data(file_)
