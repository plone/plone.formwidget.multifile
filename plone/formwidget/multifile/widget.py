import urllib

from Acquisition import aq_inner

import zope.component
from zope.component import adapter

from zope.app.component.hooks import getSite
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implements, implementer
from zope.publisher.interfaces import IPublishTraverse

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
from plone.formwidget.multifile.utils import encode, decodeQueryString


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
# - IE8 displays a blank <li> item in between each upload
# ------------------------------------------------------------------------------

def getFlashInlineJavascript():
    # DEBUG:  import each time to make sure we get debugging changes
    from plone.formwidget.multifile.inlinejavascript import DELETE, FLASH_UPLOAD_JS
    return DELETE + FLASH_UPLOAD_JS

def getXHRInlineJavascript():
    # DEBUG:  import each time to make sure we get debugging changes
    from plone.formwidget.multifile.inlinejavascript import DELETE, XHR_UPLOAD_JS
    return DELETE + XHR_UPLOAD_JS

class MultiFileWidget(multi.MultiWidget):
    implements(IMultiFileWidget, IPublishTraverse, IDraftable)

    klass = u'multi-file-widget'

    input_template = ViewPageTemplateFile('input.pt')
    display_template = ViewPageTemplateFile('display.pt')
    file_template = ViewPageTemplateFile('file_template.pt')

    def __init__(self, request):
        super(multi.MultiWidget, self).__init__(request)
        self.request.form.update(decodeQueryString(request.get('QUERY_STRING', '')))

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
            #converter = IDataConverter(self)
            #converted_value = converter.toFieldValue(self.value)
            for i, file_ in enumerate(self.value):
                yield self.render_file(file_, index=i)

    def render_file(self, file_, index=None, context=None):
        """Renders the <li> for one file.
        """
        if context == None:
            context = self.better_context

        if index == None:
            raise ValueError('Either value or index expected')

        value = 'index:%i' % index
        view_name = self.name[len(self.form.prefix):]
        view_name = view_name[len(self.form.widgets.prefix):]
        download_url = '%s/++widget++%s/%s/@@download/%s' % (
            self.request.getURL(),
            view_name,
            #index,
            file_.filename,
            file_.filename
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
        settings = self.upload_settings()
        if self.field.use_flashupload:
            #return FLASH_UPLOAD_JS % settings
            return getFlashInlineJavascript() % settings
        else:
            #return XHR_UPLOAD_JS % settings
            return getXHRInlineJavascript() % settings

    def content_types_infos(self, allowable_file_extensions):
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

    def upload_settings(self):
        """Returns a dectionary contianing settings required for javascript
        """
        context = aq_inner(self.better_context)
        request = self.request
        session = request.get('SESSION', {})
        portal_url = self.portal.absolute_url()

        # use a ticket for authentication (used for flashupload only)
        ticket = encode(self.request.cookies.get('__ac', ''))

        # Added
        fieldName = self.field.__name__
        requestURL = "/".join(self.request.physicalPathFromURL(self.request.getURL()))
        widgetURL = requestURL + '/++widget++' + fieldName
        if self.field.use_flashupload:
            action_url = urllib.quote(widgetURL + '/@@multifile_flash_upload_file')
        else:
            action_url = urllib.quote(widgetURL + '/@@multifile_upload_file')

        delete_url = urllib.quote(widgetURL + '/@@multifile_delete')

        settings = dict(
            multi                   = self.field.multi and 'true' or 'false',
            action_url              = action_url,
            delete_url              = delete_url,
            field_name              = self.field.__name__,
            ticket                  = ticket,
            portal_url              = portal_url,
            typeupload              = '',
            context_url             = context.absolute_url(),
            physical_path           = "/".join(context.getPhysicalPath()),
            id                      = self.get_uploader_function_id(),
            file_list_id            = self.get_file_list_id(),
            name                    = self.get_uploader_id(),
            size_limit              = self.field.size_limit and str(self.size_limit * 1024) or '',
            xhr_size_limit          = self.field.size_limit and str(self.size_limit * 1024) or '0',
            sim_upload_limit        = str(self.field.sim_upload_limit),
            button_text             = _(u'Browse'),
            delete_message          = _(u'Deleting... Please Wait.'),
            draganddrop_text        = _(u'Drag and drop files to upload'),
            msg_all_sucess          = _(u'All files uploaded with success.'),
            msg_some_sucess         = _(u' files uploaded with success, '),
            msg_some_errors         = _(u" uploads return an error."),
            msg_failed              = _(u"Failed"),
            error_try_again_wo      = _(u"please select files again without it."),
            error_try_again         = _(u"please try again."),
            error_empty_file        = _(u"This file is empty :"),
            error_file_large        = _(u"This file is too large :"),
            error_maxsize_is        = _(u"maximum file size is :"),
            error_bad_ext           = _(u"This file has invalid extension :"),
            error_onlyallowed       = _(u"Only allowed :"),
            error_no_permission     = _(u"You don't have permission to add this content in this place."),
            error_already_exists    = _(u"This file already exists with the same name on server :"),
            error_zodb_conflict     = _(u"A data base conflict error happened when uploading this file :"),
            error_server            = _(u"Server error, please contact support and/or try again."),
            error_draft             = _(u"A draft could not be created, please contact support."),
        )

        typeupload = session.get('typeupload', request.get('typeupload', ''))
        settings['typeupload'] = typeupload

        content_types_infos = self.content_types_infos(self.field.allowable_file_extensions)
        settings['file_extensions'] = content_types_infos[0]
        settings['file_extensions_list'] = str(content_types_infos[1])
        settings['file_description'] = content_types_infos[2]

        return settings

    def get_file_list_id(self):
        """Returns the id attribute for the files list
        """
        return 'multi-file-%s-list' % self.name.replace('.', '-')

    def get_uploader_id(self):
        """Returns the id attribute for the uploader div. This should
        be uniqe, also when using multiple widgets on the same page.
        """
        return 'multi-file-%s' % self.name.replace('.', '-')
        #return self.get_uploader_function_id()

    # TODO:  Try to eliminate this method
    def get_uploader_function_id(self):
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

        widget = self.widgets[valueMap.get(name)].__of__(self.better_context)

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
