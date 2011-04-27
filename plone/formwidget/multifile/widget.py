import urllib

from Acquisition import aq_inner

import zope.component
from zope.component import adapter

from zope.app.component.hooks import getSite
#from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implements, implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.pagetemplate.interfaces import IPageTemplate

from plone.formwidget.multifile.interfaces import IMultiFileWidget
from plone.formwidget.multifile.utils import get_icon_for

from z3c.form import interfaces
from z3c.form.browser import multi
from z3c.form.widget import FieldWidget
from z3c.form.i18n import MessageFactory as _

from plone.dexterity.i18n import MessageFactory as _

from plone.app.drafts.interfaces import IDraftable

from plone.formwidget.multifile.interfaces import IMultiFileField
#from plone.formwidget.multifile.inlinejavascript import FLASH_UPLOAD_JS, XHR_UPLOAD_JS
from plone.formwidget.multifile.utils import encode, decode, decodeQueryString

from plone.formwidget.multifile.interfaces import IImageScaleTraversable
from zope.interface import alsoProvides
from Acquisition import ImplicitAcquisitionWrapper


# ------------------------------------------------------------------------------
# NOTES
# -----
#
# - To scale an image; here is syntax:
#   http://127.0.0.1:50080/content/view/++widget++field_name/filename.ext/@@images/filename.ext
#   http://127.0.0.1:50080/content/view/++widget++field_name/filename.ext/@@images/filename.ext/thumb
#   - or -
#   <img tal:define="scales options/widget/@@images;
#                    image options/filename;
#                    thumbnail python: scales.scale(image, width=64, height=64);"
#        tal:condition="thumbnail"
#        tal:attributes="src thumbnail/url;
#                        width thumbnail/width;
#                        height thumbnail/height" />
#  - etc - [the rest is like regular scaling; (plone.namedfile.usage.txt)]
#
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# TODO
# ------------------------------------------------------------------------------
# - Cleanup!
# - Option to store files in object or place in container; item will raise
#   error if attempting to store in container
# - HTML templates for image
# - drag/drap to re-order
# - get drag/drop working
# - fix to work with deco (deco converts js <> to &lt; %gt; which is causing
#   display issues
# - Display errors in flash upload on error
# - Add option to allow multi or not (incase developer just wants to use
#   image ajax for preview
# - if multi is true, disable browse button allwoing one 1 image
# - add number of files max; size; etc and disable button on max
# - fallback to list style 'add' if no javascript
#
# - add max number of files(maybe list widget has max already); size_limit;
#
# KSS STUFF
# - Implement kss security; make sure only valid user can delete!!!
# - try using onMouseUp instead of click; want to see click
# - add a spinner to indicate somethings happening?
# - broke download file if files were deleted; add logic if filename!=filename
#   to loop and find

# ------------------------------------------------------------------------------
# BUGS
# ------------------------------------------------------------------------------
# - If users logon session expires, and tryes to add/delete items, they won't
#   work since they are not auth'd and there is no error message; just looks
#   like a failure (500; 503).  Also, drafts will not work for same reason.
# ------------------------------------------------------------------------------


def getFlashInlineJavascript():
    # DEBUG:  import each time to make sure we get debugging changes
    from plone.formwidget.multifile.inlinejavascript import MULTIFILE_INLINE_JS, FLASH_UPLOAD_JS
    return MULTIFILE_INLINE_JS + FLASH_UPLOAD_JS


def getXHRInlineJavascript():
    # DEBUG:  import each time to make sure we get debugging changes
    from plone.formwidget.multifile.inlinejavascript import MULTIFILE_INLINE_JS, XHR_UPLOAD_JS
    return MULTIFILE_INLINE_JS + XHR_UPLOAD_JS


class MultiFileWidget(multi.MultiWidget):
    implements(IMultiFileWidget, IPublishTraverse, IDraftable)

    klass = u'multifile-widget'

    def __init__(self, request):
        super(multi.MultiWidget, self).__init__(request)
        self.request.form.update(decodeQueryString(request.get('QUERY_STRING', '')))

        # FlashUpload does not authenicate properly, therefore a draft would
        # not have been created yet, so we need to update the form which in
        # turn will load the draft
        if self.request.get('__ac') is None and self.request.form.get('ticket') is not None:
            self.request.set('__ac', decode(self.request.get('ticket')))

    @property
    def betterContext(self):
        return self.form.context

    def editing(self):
        return self.mode == 'input'

    def getData(self):
        """
        """
        for index, subwidget in enumerate(self.widgets):
            yield self.renderWidget(subwidget, index)

    def renderWidget(self, subwidget, index):
        """Renders the <li> for one file.
        """
        context = self.betterContext

        view_name = self.name[len(self.form.prefix):]
        view_name = view_name[len(self.form.widgets.prefix):]
        widget_url = '%s/++widget++%s/%s' % (
            self.request.getURL(),
            view_name,
            urllib.quote(subwidget.value.filename)
            )
        download_url = '%s/@@download/%s' % (
            widget_url,
            urllib.quote(subwidget.value.filename)
            )
        scale_url = '%s/@@images/%s' % (
            widget_url,
            urllib.quote(subwidget.value.filename)
            )

        options = {'icon': '/'.join((context.portal_url(),
                                     get_icon_for(context, subwidget.value))),
                   'filename': subwidget.value.filename,
                   'size': int(round(subwidget.value.getSize() / 1024)),
                   'widget_url': widget_url,
                   'download_url': download_url,
                   'scale_url': scale_url,
                   'widget': subwidget,
                   'editable': self.mode == 'input',
                   }

        template = zope.component.getMultiAdapter(
            (self.context, self.request, self, self.field, subwidget),
            IPageTemplate,
            name=self.mode)
        return template(subwidget, **options)

    def update(self):
        # Support old list schema
        from plone.formwidget.multifile.field import MultiFile
        if not isinstance(self.field, MultiFile):
            self.field.multi = MultiFile.multi
            self.field.use_flash_upload = MultiFile.use_flash_upload
            self.field.size_limit = MultiFile.size_limit
            self.field.max_connections = MultiFile.max_connections
            self.field.allowable_file_extensions = MultiFile.allowable_file_extensions

        super(MultiFileWidget, self).update()
        self.portal = getSite()

    def getInlineJS(self):
        #DEBUG
        #self.field.use_flash_upload = False;

        # We need to encode the javascipt since it contains HTML codes
        # that deco will XML serialize ( '<' becomes &lt;) etc which would
        # break the code
        JS="""<script type="text/javascript">// <![CDATA[
        document.write(unescape("%(javascript)s"));
        // ]]></script>
        """

        settings = self.uploadSettings()
        if self.field.use_flash_upload:
            javascript = '<script type="text/javascript">' + getFlashInlineJavascript() % settings + '</script>'
        else:
            javascript = '<script type="text/javascript">' + getXHRInlineJavascript() % settings + '</script>'

        return JS % {'javascript' : urllib.quote(javascript)}

    def contentTypesInfos(self, allowable_file_extensions):
        """
        return some content types infos depending on allowable_file_extensions type
        allowable_file_extensions could be 'image', 'video', 'audio' or any
        extension like '*.doc'
        """
        #context = aq_inner(self.context)
        ext = '*.*;'
        extlist = []
        msg = _(u'Choose files to upload')
        if allowable_file_extensions == 'image' :
            ext = '*.jpg;*.jpeg;*.gif;*.png;'
            msg = _(u'Choose images to upload')
        elif allowable_file_extensions == 'video' :
            ext = '*.flv;*.avi;*.wmv;*.mpg;'
            msg = _(u'Choose video files to upload')
        elif allowable_file_extensions == 'audio' :
            ext = '*.mp3;*.wav;*.ogg;*.mp4;*.wma;*.aif;'
            msg = _(u'Choose audio files to upload')
        elif allowable_file_extensions == 'flash' :
            ext = '*.swf;'
            msg = _(u'Choose flash files to upload')
        elif allowable_file_extensions :
            # you can also pass a list of extensions in allowable_file_extensions request var
            # with this syntax '*.aaa;*.bbb;'
            ext = allowable_file_extensions
            msg = _(u'Choose file for upload : ') + ext

        try :
            extlist = [f.split('.')[1].strip() for f in ext.split(';') if f.strip()]
        except :
            extlist = []
        if extlist == ['*'] :
            extlist = []

        return (ext, extlist, msg)

    def uploadSettings(self):
        """Returns a dectionary contianing settings required for javascript
        """
        context = aq_inner(self.betterContext)
        request = self.request
        session = request.get('SESSION', {})

        portalURL         = self.portal.absolute_url()
        fieldName         = self.field.__name__
        typeupload        = session.get('typeupload', request.get('typeupload', ''))
        contentTypesInfos = self.contentTypesInfos(self.field.allowable_file_extensions)
        ticket            = encode(self.request.cookies.get('__ac', ''))
        requestURL        = "/".join(self.request.physicalPathFromURL(self.request.getURL()))
        widgetURL         = requestURL + '/++widget++' + fieldName
        if self.field.use_flash_upload:
            actionURL     = urllib.quote(widgetURL + '/@@multifile_flash_upload_file')
        else:
            actionURL     = urllib.quote(widgetURL + '/@@multifile_upload_file')

        settings = dict(
            actionURL                  = actionURL,
            deleteURL                  = urllib.quote(widgetURL + '/@@multifile_delete_file'),
            checkScriptURL             = urllib.quote(widgetURL + '/@@multifile_check_file'),
            portalURL                  = portalURL,
            contextURL                 = context.absolute_url(),
            physicalPath               = "/".join(context.getPhysicalPath()),
            typeupload                 = typeupload,
            fieldName                  = self.field.__name__,
            ID                         = self.getUploaderFunctionID(),
            fileListID                 = self.getFileListID(),
            name                       = self.getUploaderID(),
            ticket                     = ticket,
            multi                      = self.field.multi and 'true' or 'false',
            sizeLimit                  = self.field.size_limit and str(self.size_limit * 1024) or '',
            xhrSizeLimit               = self.field.size_limit and str(self.size_limit * 1024) or '0',
            maxConnections             = str(self.field.max_connections),
            buttonText                 = _(u'Browse'),
            deleteMessage              = _(u'Deleting... Please Wait.'),
            dragAndDropText            = _(u'Drag and drop files to upload'),
            fileExtensions             = contentTypesInfos[0],
            fileExtensionsList         = str(contentTypesInfos[1]),
            fileDescription            = contentTypesInfos[2],
            msgAllSuccess              = _(u'All files uploaded with success.'),
            msgSomeSuccess             = _(u' files uploaded with success, '),
            msgSomeErrors              = _(u" uploads return an error."),
            msgFailed                  = _(u"Failed"),
            errorTryAgainWo            = _(u"please select files again without it."),
            errorTryAgain              = _(u"please try again."),
            errorEmptyFile             = _(u"This file is empty :"),
            errorFileLarge             = _(u"This file is too large :"),
            errorMaxSizeIs             = _(u"maximum file size is :"),
            errorBadExt                = _(u"This file has invalid extension :"),
            errorOnlyAllowed           = _(u"Only allowed :"),
            errorNoPermission          = _(u"You don't have permission to add this content in this place."),
            errorAlreadyExists         = _(u"This file already exists with the same name on server :"),
            errorZodbConflict          = _(u"A data base conflict error happened when uploading this file :"),
            errorServer                = _(u"Server error, please contact support and/or try again."),
            errorDraft                 = _(u"A draft could not be created, please contact support."),
        )

        return settings

    def getFileListID(self):
        """Returns the id attribute for the files list
        """
        return 'multi-file-%s-list' % self.name.replace('.', '-')

    def getUploaderID(self):
        """Returns the id attribute for the uploader div. This should
        be uniqe, also when using multiple widgets on the same page.
        """
        return 'multi-file-%s' % self.name.replace('.', '-')
        #return self.getUploaderFunctionID()

    # TODO:  Try to eliminate this method
    def getUploaderFunctionID(self):
        """Returns a suitable id used to name javascript functions.
        """
        return 'multi_file_%s' % self.name.replace('.', '_')

    def publishTraverse(self, request, name):
        # Need to convert the list into a dictionary so we can lookup by filename
        # since delete removes items from list, and browser index could be
        # incorrent
        valueDictionary = {}
        valueMap = {}

        for index, value in enumerate(self.value):
            valueDictionary[value.filename] = value
            valueMap[value.filename] = index

        widget = self.widgets[valueMap.get(name)].__of__(self.betterContext)

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

        pfm = getattr(widget, 'plone_formwidget_multifile')
        widget.context = pfm['dict_context']

        return widget

    def updateWidgets(self):
        """Setup internal widgets based on the value_type for each value item.
        """
        oldLen = len(self.widgets)
        self.widgets = []
        idx = 0
        if self.value:
            for v in self.value:
                widget = self.getWidget(idx)
                self.applyValue(widget, v)

                # For scaling...
                widget_url = '%s/%s/++widget++%s/%s' % (
                    self.betterContext.absolute_url(),
                    'view',  #if self.form.parentForm == 'display' else 'edit',
                    self.field.__name__,
                    urllib.quote(v.filename)
                    )
                dict_context = ObjectishDict({ v.filename : v })
                alsoProvides(dict_context, IMultiFileWidget)
                setattr(widget, 'plone_formwidget_multifile', {
                    'original_context' : widget.context,
                    'dict_context'     : dict_context,
                    'url'              : widget_url
                })
                alsoProvides(widget, IImageScaleTraversable)

                self.widgets.append(widget)
                idx += 1
        missing = oldLen - len(self.widgets)
        if missing > 0:
            # add previous existing new added widgtes
            for i in xrange(missing):
                widget = self.getWidget(idx)
                self.widgets.append(widget)
                idx += 1

    def extract(self, default=interfaces.NO_VALUE):
        """ This method is responsible to get the widgets value based on the
        widget value in the draft only, since it can never be added directly
        via a form (uses ajax calls)."""

        values = []
        append = values.append

        #draftValue = zope.component.getMultiAdapter(
        #   (self.context, self.field), interfaces.IDataManager).query()
        dataManager = zope.component.queryMultiAdapter(
           (self.context, self.field), interfaces.IDataManager)

        if dataManager is None:
            return interfaces.NO_VALUE

        draftValue = dataManager.query()

        if draftValue is None:
            return interfaces.NO_VALUE

        for idx in range(len(draftValue)):
            #widget = self.getWidget(idx)
            append(draftValue[idx])
        if len(values) == 0:
            # no multi value found
            return interfaces.NO_VALUE
        return values

from Acquisition import Implicit
class ObjectishDict(dict, Implicit):
    """We need to be able to do something like
       # getattr(widget.context, widget.field.__name__)
       # and it should return the value
    """
    # XXX: Warning
    # This is probably not good; but I dont know how to protect it in zcml yet
    __allow_access_to_unprotected_subobjects__ = True

    def __getattr__(self, k):
        value = self.get(k)
        return value

@implementer(interfaces.IFieldWidget)
@adapter(IMultiFileField, interfaces.IFormLayer)
def MultiFileFieldWidget(field, request):
    return FieldWidget(field, MultiFileWidget(request))
