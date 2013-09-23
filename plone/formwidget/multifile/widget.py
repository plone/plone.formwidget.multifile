from Acquisition import aq_inner

from plone.formwidget.multifile.interfaces import IMultiFileWidget
from plone.formwidget.multifile.utils import get_icon_for
from plone.namedfile.utils import set_headers, stream_data
from plone.namedfile.file import INamedFile
from z3c.form.interfaces import IFieldWidget, IDataConverter, IDataManager, NO_VALUE
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.app.component.hooks import getSite
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.interface import implements, implementer
from zope.publisher.interfaces import IPublishTraverse, NotFound
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

def encode(s):
    """ encode string
    """
    return "d".join(map(str, map(ord, s)))


def decode(s):
    """ decode string
    """
    return "".join(map(chr, map(int, s.split("d"))))

class MultiFileWidget(Widget):
    implements(IMultiFileWidget)

    klass = u'multi-file-widget'

    input_template = ViewPageTemplateFile('input.pt')
    display_template = ViewPageTemplateFile('display.pt')
    file_template = ViewPageTemplateFile('file_template.pt')

    @property
    def better_context(self):
        return self.form.context

    def render(self):
        self.update()
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
        if self.value:
            # Depending on when this gets called we'll have INamedFile's,
            # strings ("index:N") or FileUpload's (on failed validations).
            # We have to filter out the FileUpload's since the uploads are gone
            # and we can do nothing about it.
            sub_values = [
                i for i in self.value
                if INamedFile.providedBy(i) or isinstance(i, basestring)
            ]

            converter = IDataConverter(self)
            converted_value = converter.toFieldValue(sub_values)

            if self.form is not None:
                view_name = self.name[len(self.form.prefix):]
                view_name = view_name[len(self.form.widgets.prefix):]
            else:
                view_name = ''

            for i, value in enumerate(converted_value):
                form_value = 'index:%s' % i
                download_url = '%s/++widget++%s/@@download/%i' % (
                    self.request.getURL(),
                    view_name,
                    i,
                )

                yield self.render_file(form_value, value, download_url)

    def render_file(self, form_value, file_, download_url):
        """Renders the <li> for one file.
        """
        context = self.better_context

        try:
            size = file_.getSize()
        except AttributeError:
            size = file_.tell()

        options = {'value': form_value,
                   'icon': '/'.join((context.portal_url(),
                                     get_icon_for(context, file_))),
                   'filename': file_.filename,
                   'size': int(round(size / 1024)),
                   'download_url': download_url,
                   'widget': self,
                   'editable': self.mode == 'input',
                   }

        return self.file_template(**options)

    def update(self):
        super(MultiFileWidget, self).update()
        self.portal = getSite()

    def get_uploader_id(self):
        """Returns the id attribute for the uploader div. This should
        be uniqe, also when using multiple widgets on the same page.
        """
        return 'multi-file-%s' % self.name.replace('.', '-')

    def extract(self, *args, **kwargs):
        """Use the extrat method of the default Widget since the
        MultiWidget expects sub-widgets.
        """
        return Widget.extract(self, *args, **kwargs)

@implementer(IFieldWidget)
def MultiFileFieldWidget(field, request):
    return FieldWidget(field, MultiFileWidget(request))


class Download(BrowserView):
    """Download a file via ++widget++widget_name/@@download/filename"""

    implements(IPublishTraverse)

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
