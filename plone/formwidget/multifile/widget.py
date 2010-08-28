from Products.Five.browser import BrowserView
from plone.formwidget.multifile.interfaces import IMultiFileWidget
from plone.formwidget.multifile.interfaces import ITemporaryFileHandler
from plone.namedfile import NamedFile
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.app.component.hooks import getSite
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.interface import implements, implementer


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

class MultiFileWidget(Widget):
    implements(IMultiFileWidget)

    klass = u'multi-file-widget'

    input_template = ViewPageTemplateFile('input.pt')

    def render(self):
        return self.input_template(self)

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
            physical_path="/".join(self.context.getPhysicalPath()),
            )

    def get_uploader_id(self):
        """Returns the id attribute for the uploader div. This should
        be uniqe, also when using multiple widgets on the same page.
        """
        return 'multi-file-%s' % self.name.replace('.', '-')



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
        handler = getMultiAdapter((self.context, self.request),
                                  ITemporaryFileHandler)
        file_ = NamedFile(file_, filename=file_.filename.decode('utf-8'))
        draft = handler.create(file_)
        return draft.__name__
