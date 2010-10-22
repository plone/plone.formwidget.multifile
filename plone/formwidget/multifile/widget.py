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
# - add max number of files(maybe list widget has max already); sizeLimit;
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
        download_url = '%s/++widget++%s/%s/@@download/%s' % (
            self.request.getURL(),
            view_name,
            urllib.quote(subwidget.value.filename),
            urllib.quote(subwidget.value.filename)
            )

        options = {'icon': '/'.join((context.portal_url(),
                                     get_icon_for(context, subwidget.value))),
                   'filename': subwidget.value.filename,
                   'size': int(round(subwidget.value.getSize() / 1024)),
                   'download_url': download_url,
                   'widget': self,
                   'editable': self.mode == 'input',
                   }

        template = zope.component.getMultiAdapter(
            (self.context, self.request, self, self.field, subwidget),
            IPageTemplate,
            name=self.mode)
        return template(subwidget, **options)

    def update(self):
        # Support old list schema
        from plone.formwidget.multifile import MultiFileField
        if not isinstance(self.field, MultiFileField):
            self.field.multi = MultiFileField.multi
            self.field.useFlashUpload = MultiFileField.useFlashUpload
            self.field.sizeLimit = MultiFileField.sizeLimit
            self.field.maxConnections = MultiFileField.maxConnections
            self.field.allowableFileExtensions = MultiFileField.allowableFileExtensions

        super(MultiFileWidget, self).update()
        self.portal = getSite()

    def getInlineJS(self):
        JS="""<script type="text/javascript">// <![CDATA[
        %(javascript)s
        // ]]></script>
        """

        # DEBUG; remove CDATA
        JS="""<script type="text/javascript">
        %(javascript)s
        </script>
        """
        settings = self.uploadSettings()
        if self.field.useFlashUpload:
            javascript = getFlashInlineJavascript() % settings
        else:
            javascript = getXHRInlineJavascript() % settings

        return JS % {'javascript' : javascript}

    def contentTypesInfos(self, allowableFileExtensions):
        """
        return some content types infos depending on allowableFileExtensions type
        allowableFileExtensions could be 'image', 'video', 'audio' or any
        extension like '*.doc'
        """
        #context = aq_inner(self.context)
        ext = '*.*;'
        extlist = []
        msg = _(u'Choose files to upload')
        if allowableFileExtensions == 'image' :
            ext = '*.jpg;*.jpeg;*.gif;*.png;'
            msg = _(u'Choose images to upload')
        elif allowableFileExtensions == 'video' :
            ext = '*.flv;*.avi;*.wmv;*.mpg;'
            msg = _(u'Choose video files to upload')
        elif allowableFileExtensions == 'audio' :
            ext = '*.mp3;*.wav;*.ogg;*.mp4;*.wma;*.aif;'
            msg = _(u'Choose audio files to upload')
        elif allowableFileExtensions == 'flash' :
            ext = '*.swf;'
            msg = _(u'Choose flash files to upload')
        elif allowableFileExtensions :
            # you can also pass a list of extensions in allowableFileExtensions request var
            # with this syntax '*.aaa;*.bbb;'
            ext = allowableFileExtensions
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
        contentTypesInfos = self.contentTypesInfos(self.field.allowableFileExtensions)
        ticket            = encode(self.request.cookies.get('__ac', ''))
        requestURL        = "/".join(self.request.physicalPathFromURL(self.request.getURL()))
        widgetURL         = requestURL + '/++widget++' + fieldName
        if self.field.useFlashUpload:
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
            sizeLimit                  = self.field.sizeLimit and str(self.sizeLimit * 1024) or '',
            xhrSizeLimit               = self.field.sizeLimit and str(self.sizeLimit * 1024) or '0',
            maxConnections             = str(self.field.maxConnections),
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

        # we need to be able to do something like
        # getattr(widget.context, widget.field.__name__)
        # and it should return the value
        class objectish_dict(dict):
            def __getattr__(self, k):
                value = self.get(k)
                if value is None:
                    raise ValueError('invalid key')
                return value

        widget.context = objectish_dict(valueDictionary)

        return widget

    def extract(self, default=interfaces.NO_VALUE):
        """ This method is responsible to get the widgets value based on the
        widget value in the draft only, since it can never be added directly
        via a form (uses ajax calls)."""

        values = []
        append = values.append

        draftValue = zope.component.getMultiAdapter(
            (self.context, self.field), interfaces.IDataManager).query()

        if draftValue is None:
            return interfaces.NO_VALUE

        for idx in range(len(draftValue)):
            #widget = self.getWidget(idx)
            append(draftValue[idx])
        if len(values) == 0:
            # no multi value found
            return interfaces.NO_VALUE
        return values


@implementer(interfaces.IFieldWidget)
@adapter(IMultiFileField, interfaces.IFormLayer)
def MultiFileFieldWidget(field, request):
    return FieldWidget(field, MultiFileWidget(request))
