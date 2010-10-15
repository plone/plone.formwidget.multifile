from Products.Five.browser import BrowserView
from Acquisition import aq_inner, aq_parent
from plone.formwidget.multifile.interfaces import IMultiFileWidget
from plone.formwidget.multifile.utils import get_icon_for
from z3c.form.interfaces import IFieldWidget, IDataConverter
from z3c.form.widget import FieldWidget
from z3c.form.widget import MultiWidget
from zope.app.component.hooks import getSite
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.browser.interfaces import IBrowserView
from zope.interface import implements, implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.component import queryMultiAdapter

from z3c.form import interfaces
from z3c.form.i18n import MessageFactory as _
from operator import attrgetter

import zope.component

import logging
logger = logging.getLogger('plone.formwidget.multifile')

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
# - Remove add button function
# - If fill titles is True; then be sure to use attr on file.title
#   (allow field to be updated or false); more for when saving images in own
#   folder)  <-- Git rid of fill_titles; can be done after file uploaded once
#   template is returned!!!!!!
# - Display errors in flash upload on error
# ------------------------------------------------------------------------------
# BUGS
# ------------------------------------------------------------------------------
# - maunal upload broken for flash; staticly set to auto; no titles for now
# ------------------------------------------------------------------------------


def encode(s):
    """ encode string
    """

    return "d".join(map(str, map(ord, s)))

def decode(s):
    """ decode string
    """

    return "".join(map(chr, map(int, s.split("d"))))

FLASH_UPLOAD_JS = """
    jQuery(document).ready(function() {
        jQuery('#%(name)s').uploadify({
            'uploader'      : '++resource++plone.formwidget.multifile/uploadify.swf',
            'script'        : '%(action_url)s',
            'fileDataName'  : 'qqfile',
            'cancelImg'     : '++resource++plone.formwidget.multifile/cancel.png',
            'folder'        : '%(physical_path)s',
            'auto'          : true,
            'multi'         : true,
            'simUploadLimit': %(sim_upload_limit)s,
            'sizeLimit'     : '%(size_limit)s',
            'fileDesc'      : '%(file_description)s',
            'fileExt'       : '%(file_extensions)s',
            'buttonText'    : '%(button_text)s',
            'scriptAccess'  : 'sameDomain',
            'hideButton'    : false,
            'scriptData'    : {'ticket' : '%(ticket)s', 'typeupload' : '%(typeupload)s'},
            'onComplete'    : function (event, queueID, fileObj, responseJSON, data) {
                try{
                    response = jQuery.parseJSON( responseJSON );
                } catch(err){
                    return false;
                }

                // TODO:  Do something to indicate the error
                if( response.error ) { return false; }

                jQuery('#%(file_list_id)s').append(jQuery(document.createElement('li')).html(response.html).attr('class', 'multi-file-file'));
            },
        });
    });
"""

XHR_UPLOAD_JS = """
    var fillTitles = false
    var auto = true

    addUploadFields_%(id)s = function(file, id) {
        var uploader = xhr_%(id)s;
        PloneQuickUpload.addUploadFields(uploader, uploader._element, file, id, fillTitles);
    }
    sendDataAndUpload_%(id)s = function() {
        var uploader = xhr_%(id)s;
        PloneQuickUpload.sendDataAndUpload(uploader, uploader._element, '%(typeupload)s');
    }
    clearQueue_%(id)s = function() {
        var uploader = xhr_%(id)s;
        PloneQuickUpload.clearQueue(uploader, uploader._element);
    }
    onUploadComplete_%(id)s = function(id, fileName, responseJSON) {
        var uploader = xhr_%(id)s;
        PloneQuickUpload.onUploadComplete(uploader, uploader._element, id, fileName, responseJSON);
    }
    createUploader_%(id)s= function(){
        xhr_%(id)s = new qq.FileUploader({
            element: jQuery('#%(name)s')[0],
            action: '%(action_url)s',
            autoUpload: true,
            cancelImg: '++resource++plone.formwidget.multifile/cancel.png',

            onAfterSelect: addUploadFields_%(id)s,
            onComplete: function (id, filename, responseJSON) {
                    jQuery('#%(file_list_id)s').append(jQuery(document.createElement('li')).html(responseJSON.html).attr('class', 'multi-file-file'));
                    //var e = document.getElementById('form-widgets-%(field_name)s-count');
                    //e.setAttribute('value', responseJSON.counter);
                var uploader = xhr_%(id)s;
                PloneQuickUpload.onUploadComplete(uploader, uploader._element, id, filename, responseJSON);
            },

            allowedExtensions: %(file_extensions_list)s,
            sizeLimit: %(xhr_size_limit)s,
            simUploadLimit: %(sim_upload_limit)s,
            template: '<div class="qq-uploader">' +
                      '<div class="qq-upload-drop-area"><span>%(draganddrop_text)s</span></div>' +
                      '<div class="qq-upload-button">%(button_text)s</div>' +
                      '<ul class="qq-upload-list"></ul>' +
                      '</div>',
            fileTemplate: '<li>' +
                    '<a class="qq-upload-cancel" href="#">&nbsp;</a>' +
                    '<div class="qq-upload-infos"><span class="qq-upload-file"></span>' +
                    '<span class="qq-upload-spinner"></span>' +
                    '<span class="qq-upload-failed-text">%(msg_failed)s</span></div>' +
                    '<div class="qq-upload-size"></div>' +
                '</li>',
            messages: {
                serverError: "%(error_server)s",
                draftError: "%(error_draft)s",
                serverErrorAlreadyExists: "%(error_already_exists)s {file}",
                serverErrorZODBConflict: "%(error_zodb_conflict)s {file}, %(error_try_again)s",
                serverErrorNoPermission: "%(error_no_permission)s",
                typeError: "%(error_bad_ext)s {file}. %(error_onlyallowed)s {extensions}.",
                sizeError: "%(error_file_large)s {file}, %(error_maxsize_is)s {sizeLimit}.",
                emptyError: "%(error_empty_file)s {file}, %(error_try_again_wo)s"
            }
        });
    }
    jQuery(document).ready(createUploader_%(id)s);
"""


#from Acquisition import Explicit
#class MultiFileWidget(Explicit, MultiWidget):
#class MultiFileWidget(MultiWidget):
import z3c.form.browser.multi
from z3c.form import button
from plone.app.drafts.interfaces import IDraftable
from plone.dexterity.i18n import MessageFactory as _
class MultiFileWidget(z3c.form.browser.multi.MultiWidget):
    implements(IMultiFileWidget, IPublishTraverse, IDraftable)

    klass = u'multi-file-widget'

    input_template = ViewPageTemplateFile('input.pt')
    display_template = ViewPageTemplateFile('display.pt')
    file_template = ViewPageTemplateFile('file_template.pt')

    responseJSON = None

    def __init__(self, request):
        super(z3c.form.browser.multi.MultiWidget, self).__init__(request)
        self.request.form.update(decodeQueryString(request.get('QUERY_STRING','')))

    @property
    def better_context(self):
        return self.form.context

    def render(self):
        self.update()
        if self.mode == 'input':
            if self.responseJSON is not None:
                return self.responseJSON
            else:
                return self.input_template(self)
        else:
            return self.display_template(self)

    def editing(self):
        return self.mode == 'input'

    def get_data(self):
        """
        """
        if self.value:
            converter = IDataConverter(self)
            converted_value = converter.toFieldValue(self.value)
            for i, file_ in enumerate(self.value):
                yield self.render_file(file_, index=i)

    #def render_file(self, file_, value=None, index=None, context=None):
    def render_file(self, file_, index=None, context=None):
        """Renders the <li> for one file.
        """
        if context == None:
            context = self.better_context

        #if value == None and index == None:
        if index == None:
            raise ValueError('Either value or index expected')

        #if value == None:
        value = 'index:%i' % index
        view_name = self.name[len(self.form.prefix):]
        view_name = view_name[len(self.form.widgets.prefix):]
        download_url = '%s/++widget++%s/%i/@@download/%s' % (
            self.request.getURL(),
            view_name,
            index,
            file_.filename
            )
        remove_url = '%s/++widget++%s/%i/@@download/%s' % (
            self.request.getURL(),
            view_name,
            index,
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
                   'remove_url': remove_url,
                   }

        return self.file_template(**options)

    def update(self):
        super(MultiFileWidget, self).update()
        self.portal = getSite()

    def get_inline_js(self):
        #return INLINE_JAVASCRIPT % self.get_settings()

        settings = self.upload_settings()
        if self.field.use_flashupload:
            return FLASH_UPLOAD_JS % settings
        else:
            return XHR_UPLOAD_JS % settings

    def content_types_infos (self, allowable_file_extensions):
        """
        return some content types infos depending on allowable_file_extensions type
        allowable_file_extensions could be 'image', 'video', 'audio' or any
        extension like '*.doc'
        """
        context = aq_inner(self.context)
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
        if extlist==['*'] :
            extlist = []

        return ( ext, extlist, msg)


    def upload_settings(self):
        """Returns a dectionary contianing settings required for javascript
        """
        from Products.PythonScripts.standard import url_quote
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
            action_url=url_quote(widgetURL + '/@@multifile_flash_upload_file')
        else:
            action_url=url_quote(widgetURL + '/@@multifile_upload_file')

        settings = dict(
            action_url              = action_url,
            field_name              = self.field.__name__,
            ticket                  = ticket,
            portal_url              = portal_url,
            typeupload              = '',
            context_url             = context.absolute_url(),
            physical_path           = "/".join(context.getPhysicalPath()),
            id                      = self.get_uploader_function_id(),
            file_list_id            = self.get_file_list_id(),
            name                    = self.get_uploader_id(),
            fill_titles             = self.field.fill_titles and 'true' or 'false',
            auto_upload             = self.field.auto_upload and 'true' or 'false',
            size_limit              = self.field.size_limit and str(self.size_limit*1024) or '',
            xhr_size_limit          = self.field.size_limit and str(self.size_limit*1024) or '0',
            sim_upload_limit        = str(self.field.sim_upload_limit),
            button_text             = _(u'Browse'),
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

    def get_uploader_function_id(self):
        """Returns a suitable id used to name javascript functions.
        """
        return 'multi_file_%s' % self.name.replace('.', '_')

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

    def extract(self, default=interfaces.NO_VALUE):
        """ This method is responsible to get the widgets value based on the
        widget value in the draft only, since it can never be added directly
        via a form (uses ajax calls)."""

        values = []
        append = values.append

        draftValue = zope.component.getMultiAdapter(
            (self.context, self.field), interfaces.IDataManager).query()

        for idx in range(len(draftValue)):
            widget = self.getWidget(idx)
            append(draftValue[idx])
        if len(values) == 0:
            # no multi value found
            return interfaces.NO_VALUE
        return values


@implementer(IFieldWidget)
def MultiFileFieldWidget(field, request):
    return FieldWidget(field, MultiFileWidget(request))

# Additional imports
try:
    import json
except:
    import simplejson as json

import os
import mimetypes
import random
import urllib
from Acquisition import aq_inner, aq_parent
from AccessControl import SecurityManagement
from ZPublisher.HTTPRequest import HTTPRequest

from zope.security.interfaces import Unauthorized
from zope.filerepresentation.interfaces import IFileFactory
from zope.component import getUtility

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.interfaces import IImageContent
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.app.container.interfaces import INameChooser
from plone.i18n.normalizer.interfaces import IIDNormalizer

from plone.app.z3cformdrafts.drafting import Z3cFormDraftProxy
#import ticket as ticketmod
#from collective.quickupload import siteMessageFactory as _
#from collective.quickupload.browser.quickupload_settings import IQuickUploadControlPanel
try :
    # python 2.6
    import json
except :
    # plone 3.3
    import simplejson as json

def decodeQueryString(QueryString):
    """decode *QueryString* into a dictionary, as ZPublisher would do"""
    r = HTTPRequest(None,
                    {'QUERY_STRING' : QueryString,
                     'SERVER_URL' : '',
                     },
                    None,
                    1)
    r.processInputs()
    return r.form


from ZPublisher.HTTPRequest import FileUpload
class UploadFile(BrowserView):
    """The ajax XHR calls this view for every file added interactively.
    This view saves the file on a draft.  When the form is actually submitted
    the widget gets the files from the draft and stores it in the actual target.
    """

    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request

        # in some cases the context is the view, so lets walk up
        # and search the real context
        context = self.context
        while IBrowserView.providedBy(context):
            context = aq_parent(aq_inner(context))
        self.widget = context

        self.content = aq_inner(self.widget.context)

        # FlashUpload does not authenicate properly, therefore a draft would
        # not have been created yet, so we need to update the form which in
        # turn will load the draft
        if self.widget.field.use_flashupload:
            self.request.set('__ac', decode(self.request.get('ticket')))
            self.widget.form.update()
            self.widget = self.widget.form.widgets[self.widget.field.__name__]
            self.content = aq_inner(self.widget.context)

    # Is this needed now since adapted uses attribute to call function?
    def __call__(self):
        #if self.widget.field.use_flashupload:
        #    return self.multifile_flash_upload_file()
        #else:
        #    return self.multifile_upload_file()
        return self.multifile_upload_file()

    def multifile_flash_upload_file(self):
        return self.multifile_upload_file()

    def multifile_upload_file(self):
        if not isinstance(self.content, Z3cFormDraftProxy):
            logger.info("Draft does not exist; maybe user could not be authorized!")
            return json.dumps({u'error': u'draftError'})

        widget = self.widget
        request = self.request
        response = request.RESPONSE

        response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
        response.setHeader('Cache-control', 'no-cache')
        # the good content type woul be text/json or text/plain but IE
        # do not support it
        response.setHeader('Content-Type', 'text/html; charset=utf-8')

        if request.HTTP_X_REQUESTED_WITH :
            # using ajax upload
            file_name = urllib.unquote(request.HTTP_X_FILE_NAME)
            upload_with = "XHR"
            try :
                file = request.BODYFILE
                file_data = file.read()
                file.seek(0)
            except AttributeError :
                # in case of cancel during xhr upload
                logger.info("Upload of %s has been aborted" %file_name)
                # not really useful here since the upload block
                # is removed by "cancel" action, but
                # could be useful if someone change the js behavior
                return  json.dumps({u'error': u'emptyError'})
            except :
                logger.info("Error when trying to read the file %s in request"  %file_name)
                return json.dumps({u'error': u'serverError'})

            try :
                file_data = FileUpload(aFieldStorage = FieldStorageStub(file, {}, file_name))
            except TypeError:
                return json.dumps({u'error': u'serverError'})
        elif not self.widget.field.use_flashupload:
            # using classic form post method (MSIE<=8)
            file_data = request.get("qqfile", None)
            filename = getattr(file_data,'filename', '')
            file_name = filename.split("\\")[-1]
            upload_with = "CLASSIC FORM POST"
            # we must test the file size in this case (no client test)
            if not self._check_file_size(file_data) :
                logger.info("Test file size : the file %s is too big, upload rejected" % file_name)
                return json.dumps({u'error': u'sizeError'})
        else:
            # using flash upload
            file_data = request.get("qqfile", None)
            filename = getattr(file_data,'filename', '')
            file_name = filename.split("\\")[-1]
            upload_with = "FLASH"
            #TODO: Implement CheckFile view (flash will use it to comfirm first)
            # we must test the file size in this case (no client test)
            #if not self._check_file_size(file_data) :
            #    logger.info("Test file size : the file %s is too big, upload rejected" % file_name)
            #    return json.dumps({u'error': u'sizeError'})

        if not file_data:
            return json.dumps({u'error': u'emptyError'})

        if not self._check_file_id(widget, file_name) :
            logger.info("The file id for %s already exists, upload rejected" % file_name)
            return json.dumps({u'error': u'serverErrorAlreadyExists'})

        logger.info("uploading file with %s : filename=%s" % (upload_with, file_name))

        index = len(widget.value)
        newWidget = widget.getWidget(index)
        converter = IDataConverter(newWidget)
        newWidget.value = converter.toFieldValue(file_data)

        if newWidget.value is not None:
            widget.value.append(newWidget.value)
            widget.updateWidgets()
            # Save on draft
            dm = zope.component.getMultiAdapter(
                (self.content, widget.field), interfaces.IDataManager)
            dm.set(interfaces.IDataConverter(widget).toFieldValue(widget.value))

            # TODO; need to create a url create function in widget
            #logger.info("file url: %s" % newWidget.value.absolute_url())

            # Reset requestURL so file URL will be rendered properly
            request.URL = request.getURL()[0:(request.getURL().find('/', len(self.content.absolute_url())+1))]
            responseJSON = {u'success'  : True,
                            u'filename' : newWidget.filename,
                            u'html'     : widget.render_file(newWidget.value, index=index),
                            u'counter'  : len(widget.widgets),
                        }
        else :
            responseJSON = {u'error': f['error']}

        # If iframe was used; wrap the response in a <script> tag or will get json parse errors
        if request.HTTP_X_REQUESTED_WITH or self.widget.field.use_flashupload:
            return json.dumps(responseJSON)
        else:
            return '<script id="json-response" type="text/plain">' + json.dumps(responseJSON) + '</script>'

    def _check_file_size(self, data):
        max_size = int(self.widget.field.size_limit)
        if not max_size :
            return 1
        #file_size = len(data.read()) / 1024
        data.seek(0, os.SEEK_END)
        file_size = data.tell() / 1024
        data.seek(0, os.SEEK_SET )
        max_size = int(self.widget.field.size_limit)
        if file_size<=max_size:
            return 1
        return 0

    def _check_file_id(self, widget, filename):
        for file_ in widget.value:
            if file_.filename == filename:
                return False
        return True


class FieldStorageStub:
    """Used so we can create a FileUpload object
    """
    def __init__(self, file, headers={}, filename=''):
        self.file = file
        self.headers = headers
        self.filename = filename


class CheckFile(BrowserView):
    """
    check if file exists
    """
    def check_file(self) :
        context = aq_inner(self.context)
        request = self.request

    def __call__(self):
        """
        """
        return self.check_file()

