from Products.Five.browser import BrowserView
from Acquisition import aq_inner, aq_parent
from plone.formwidget.multifile.interfaces import IMultiFileWidget
from plone.formwidget.multifile.interfaces import ITemporaryFileHandler
from plone.formwidget.multifile.utils import get_icon_for
from plone.namedfile import NamedFile
from z3c.form.interfaces import IFieldWidget, IDataConverter
from z3c.form.widget import FieldWidget
from z3c.form.widget import MultiWidget, Widget
from zope.app.component.hooks import getSite
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.browser.interfaces import IBrowserView
from zope.component import getMultiAdapter
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


# NOTE, THIS IS NOT A PYTHON DICT:
# NEVER ADD A COMMA (,) AT THE END OF THE LAST KEY/VALUE PAIR, THIS BREAKS ALL
# M$ INTERNET EXPLORER

INLINE_JAVASCRIPT = """

    jq(document).ready(function() {
        jq('#%(name)s').uploadify({
            'uploader'      : '++resource++uploadify.swf',
            'script'        : '@@multi-file-upload-file',
            'cancelImg'     : '++resource++cancel.png',
            'height'        : '30',
            'width'         : '110',
            'folder'        : '%(physical_path)s',
            'scriptData'    : {'cookie': '%(cookie)s'},
            'onComplete'    : multifile_uploadify_response,
            'auto'          : true,
            'multi'         : true,
            'simUploadLimit': '4',
            'queueSizeLimit': '999',
            'sizeLimit'     : '',
            'fileDesc'      : '',
            'fileExt'       : '*.*',
            'buttonText'    : 'BROWSE',
            'buttonImg'     : '',
            'scriptAccess'  : 'sameDomain',
            'hideButton'    : false
        });
    });
"""


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
            for i, key_or_file in enumerate(self.value):
                if isinstance(key_or_file, unicode):
                    file_ = converted_value[i]
                    yield self.render_file(file_, value=key_or_file)

                else:
                    yield self.render_file(key_or_file, index=i)

    def render_file(self, file_, value=None, index=None, context=None):
        """Renders the <li> for one file.
        """
        if context == None:
            context = self.better_context

        if value == None and index == None:
            raise ValueError('Either value or index expected')

        if value == None:
            value = 'index:%i' % index
            view_name = self.name[len(self.form.prefix):]
            view_name = view_name[len(self.form.widgets.prefix):]
            download_url = '%s/++widget++%s/%i/@@download/%s' % (
                self.request.getURL(),
                view_name,
                index,
                file_.filename,
                )

        options = {'value': value,
                   'icon': '/'.join((context.portal_url(),
                                     get_icon_for(context, file_))),
                   'filename': file_.filename,
                   'size': int(round(file_.getSize() / 1024)),
                   'download_url': download_url,
                   'widget': self,
                   'editable': self.mode == 'input',
                   }

        return self.file_template(**options)

    def update(self):
        super(MultiFileWidget, self).update()
        self.portal = getSite()

    def get_inline_js(self):
        return INLINE_JAVASCRIPT % self.get_settings()

    def get_settings(self):
        return dict(
            name=self.get_uploader_id(),
            cookie=encode(self.request.cookies.get(
                    '__ac', '')),
            physical_path="/".join(self.better_context.getPhysicalPath()),
            )

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


class UploadFileToSessionView(BrowserView):
    """The uploadify flash calls this view for every file added interactively.
    This view saves the file in the session and returns the key where the file
    can be found in the session. When the form is actually submitted the
    widget gets the file from the session and stores it in the actual target.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

        cookie = self.request.form.get("cookie")
        if cookie:
            self.request.cookies["__ac"] = decode(cookie)

    def __call__(self):
        file_ = self.request.form['Filedata']
        # in some cases the context is the view, so lets walk up
        # and search the real context

        context = self.context
        while IBrowserView.providedBy(context):
            context = aq_parent(aq_inner(context))

        handler = getMultiAdapter((context, self.request),
                                  ITemporaryFileHandler)
        file_ = NamedFile(file_, filename=file_.filename.decode('utf-8'))
        draft = handler.create(file_)
        return draft.__name__
