import os
import urllib
import logging

from Acquisition import aq_inner, aq_parent

import zope.component
from zope.browser.interfaces import IBrowserView

from ZPublisher.HTTPRequest import FileUpload

from Products.Five.browser import BrowserView

from z3c.form import interfaces

from plone.app.z3cformdrafts.drafting import Z3cFormDraftProxy

from plone.formwidget.multifile.utils import decode

try :
    # python 2.6
    import json
except :
    # plone 3.3
    import simplejson as json

logger = logging.getLogger('plone.formwidget.multifile')


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
        if self.widget.field.use_flashupload and self.request.get('__ac') is None:
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
                file_ = request.BODYFILE
                file_data = file_.read()
                file_.seek(0)
            except AttributeError :
                # in case of cancel during xhr upload
                logger.info("Upload of %s has been aborted" % file_name)
                # not really useful here since the upload block
                # is removed by "cancel" action, but
                # could be useful if someone change the js behavior
                return  json.dumps({u'error': u'emptyError'})
            except :
                logger.info("Error when trying to read the file %s in request" % file_name)
                return json.dumps({u'error': u'serverError'})

            try :
                file_data = FileUpload(aFieldStorage=FieldStorageStub(file_, {}, file_name))
            except TypeError:
                return json.dumps({u'error': u'serverError'})
        elif not self.widget.field.use_flashupload:
            # using classic form post method (MSIE<=8)
            file_data = request.get("qqfile", None)
            filename = getattr(file_data, 'filename', '')
            file_name = filename.split("\\")[-1]
            upload_with = "CLASSIC FORM POST"
            # we must test the file size in this case (no client test)
            if not self._check_file_size(file_data) :
                logger.info("Test file size : the file %s is too big, upload rejected" % file_name)
                return json.dumps({u'error': u'sizeError'})
        else:
            # using flash upload
            file_data = request.get("qqfile", None)
            filename = getattr(file_data, 'filename', '')
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
        converter = interfaces.IDataConverter(newWidget)
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
            request.URL = request.getURL()[0:(request.getURL().find('/', len(self.content.absolute_url()) + 1))]
            responseJSON = {u'success'  : True,
                            u'filename' : newWidget.filename,
                            u'html'     : widget.render_widget(newWidget, int(index)),
                            u'counter'  : len(widget.widgets),
                        }
        else :
            responseJSON = {u'error': 'error'}

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
        data.seek(0, os.SEEK_SET)
        max_size = int(self.widget.field.size_limit)
        if file_size <= max_size:
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
