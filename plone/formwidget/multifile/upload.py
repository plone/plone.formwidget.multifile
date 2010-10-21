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

try :
    # python 2.6
    import json
except :
    # plone 3.3
    import simplejson as json

logger = logging.getLogger('plone.formwidget.multifile')


class MultiFileUpload(BrowserView):
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

    def checkFile(self):
        response = self.request.RESPONSE
        response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
        response.setHeader('Cache-control', 'no-cache')
        # the good content type woul be text/json or text/plain but IE
        # do not support it
        response.setHeader('Content-Type', 'text/html; charset=utf-8')

        responseJSON = {}
        for key, value in self.request.form.items():
            if key == 'folder':
                continue
            if self._fileExists(value):
                responseJSON[key] = value
        return json.dumps(responseJSON)

    def flashUploadFile(self):
        return self.uploadFile()

    def uploadFile(self):
        if not isinstance(self.content, Z3cFormDraftProxy):
            logger.info("Draft does not exist; maybe user could not be authorized!")
            return json.dumps({u'error': u'draftError'})

        response = self.request.RESPONSE
        response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
        response.setHeader('Cache-control', 'no-cache')
        # the good content type woul be text/json or text/plain but IE
        # do not support it
        response.setHeader('Content-Type', 'text/html; charset=utf-8')

        if self.request.HTTP_X_REQUESTED_WITH :
            # using ajax upload
            filename = urllib.unquote(self.request.HTTP_X_FILE_NAME)
            upload_with = "XHR"
            try :
                fileObject = self.request.BODYFILE
                fileData = fileObject.read()
                fileObject.seek(0)
            except AttributeError :
                # in case of cancel during xhr upload
                logger.info("Upload of %s has been aborted" % filename)
                # not really useful here since the upload block
                # is removed by "cancel" action, but
                # could be useful if someone change the js behavior
                return  json.dumps({u'error': u'emptyError'})
            except :
                logger.info("Error when trying to read the file %s in request" % filename)
                return json.dumps({u'error': u'serverError'})

            try :
                fileData = FileUpload(aFieldStorage=FieldStorageStub(fileObject, {}, filename))
            except TypeError:
                return json.dumps({u'error': u'serverError'})
        elif not self.widget.field.use_flashupload:
            # using classic form post method (MSIE<=8)
            fileData = self.request.get("qqfile", None)
            filename = getattr(fileData, 'filename', '').split("\\")[-1]
            upload_with = "CLASSIC FORM POST"
        else:
            # using flash upload
            fileData = self.request.get("qqfile", None)
            filename = getattr(fileData, 'filename', '').split("\\")[-1]
            upload_with = "FLASH"

        if not fileData:
            return json.dumps({u'error': u'emptyError'})

        if self._fileExists(filename) :
            logger.info("The file id for %s already exists, upload rejected" % filename)
            return json.dumps({u'error': u'serverErrorAlreadyExists'})

        # Don't rely on flash or ajax to check filesize as it can be hacked
        if not self._checkFileSize(fileData) :
            logger.info("Test file size : the file %s is too big, upload rejected" % filename)
            return json.dumps({u'error': u'sizeError'})

        logger.info("uploading file with %s : filename=%s" % (upload_with, filename))

        index = len(self.widget.value)
        newWidget = self.widget.getWidget(index)
        converter = interfaces.IDataConverter(newWidget)
        newWidget.value = converter.toFieldValue(fileData)

        if newWidget.value is not None:
            self.widget.value.append(newWidget.value)
            self.widget.updateWidgets()
            # Save on draft
            dm = zope.component.getMultiAdapter(
                (self.content, self.widget.field), interfaces.IDataManager)
            dm.set(interfaces.IDataConverter(self.widget).toFieldValue(self.widget.value))

            # TODO; need to create a url create function in widget
            #logger.info("file url: %s" % newWidget.value.absolute_url())

            # Reset requestURL so file URL will be rendered properly
            self.request.URL = self.request.getURL()[0:(self.request.getURL().find('/', len(self.content.absolute_url()) + 1))]
            responseJSON = {u'success'  : True,
                            u'filename' : newWidget.filename,
                            u'html'     : self.widget.renderWidget(newWidget, int(index)),
                            u'counter'  : len(self.widget.widgets),
                        }
        else :
            responseJSON = {u'error': 'error'}

        # If iframe was used; wrap the response in a <script> tag or will get json parse errors
        if self.request.HTTP_X_REQUESTED_WITH or self.widget.field.use_flashupload:
            return json.dumps(responseJSON)
        else:
            return '<script id="json-response" type="text/plain">' + json.dumps(responseJSON) + '</script>'

    def _checkFileSize(self, data):
        """ Checks to make sure falie length is less than allowable maximum
        size
        """
        maxSize = int(self.widget.field.size_limit)
        if not maxSize :
            return 1
        #file_size = len(data.read()) / 1024
        data.seek(0, os.SEEK_END)
        fileSize = data.tell() / 1024
        data.seek(0, os.SEEK_SET)
        maxSize = int(self.widget.field.size_limit)
        if fileSize <= maxSize:
            return 1
        return 0

    def _fileExists(self, filename):
        """
        check if file exists
        """
        for fileObject in self.widget.value:
            if fileObject.filename == filename:
                return True
        return False


class FieldStorageStub:
    """Used so we can create a FileUpload object
    """
    def __init__(self, file, headers={}, filename=''):
        self.file = file
        self.headers = headers
        self.filename = filename
