from plone.formwidget.multifile.interfaces import IMultiFileWidget
from plone.formwidget.multifile.utils import get_icon_for

from z3c.form.interfaces import IFieldWidget, IDataConverter
from z3c.form.widget import FieldWidget
from z3c.form.widget import MultiWidget, Widget
from zope.app.component.hooks import getSite
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.interface import implements, implementer
from zope.publisher.interfaces import IPublishTraverse


def encode(s):
    """ encode string
    """
    return "d".join(map(str, map(ord, s)))


def decode(s):
    """ decode string
    """
    return "".join(map(chr, map(int, s.split("d"))))


class MultiFileWidget(MultiWidget):
    implements(IMultiFileWidget, IPublishTraverse)

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
        """
        """
        if self.value:
            # sometimes the value contains the strings from the form,
            # sometimes it's already converted by the converter. But
            # if we have errors and we are trying to add a new file
            # (thats when entry is a unicode string) we need to put
            # that string again in the form since we did not store the
            # file yet, but we can get the file from the converter..
            converter = IDataConverter(self)
            converted_value = converter.toFieldValue(self.value)

            own = list(self.value)

            view_name = self.name[len(self.form.prefix):]
            view_name = view_name[len(self.form.widgets.prefix):]
            drafts = 0

            for i, value in enumerate(converted_value):
                form_value = 'index:%s'%(i-drafts)
                try:
                    index = own.index(value)
                    download_url = '%s/++widget++%s/%i/@@download/%s' % (
                        self.request.getURL(),
                        view_name,
                        index,
                        value.filename,
                        )
                except (IndexError, ValueError):
                    download_url = None
                    if hasattr(value, 'draftName'):
                        form_value = 'new:%s'%value.draftName
                        drafts += 1
            
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

    def publishTraverse(self, request, name):
        widget = self.widgets[int(name)].__of__(self.better_context)
        # fix some stuff, according to z3c.form.field.FieldWidgets.update
        widget.name = self.name + '.' + name
        widget.__name__ = name
        widget.id = self.name.replace('.', '-')
        widget.form = self.form
        widget.ignoreContext = self.ignoreContext
        widget.ignoreRequest = self.ignoreRequest
        widget.mode = self.mode
        widget.update()
        widget.field.__name__ = name

        # we need to be able to do something like
        # getattr(widget.context, widget.field.__name__)
        # and it should return the value

        class objectish_list(list):
            def __getattr__(self, k):
                return self[int(k)]

        widget.context = objectish_list(self.value)

        return widget


@implementer(IFieldWidget)
def MultiFileFieldWidget(field, request):
    return FieldWidget(field, MultiFileWidget(request))

