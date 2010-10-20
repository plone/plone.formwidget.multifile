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


class DeleteFile(BrowserView):
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

    # Is this needed now since adapted uses attribute to call function?
    #def __call__(self):
    #    pass

    def multifile_delete(self):
        response = self.request.RESPONSE
        response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
        response.setHeader('Cache-control', 'no-cache')
        # the good content type woul be text/json or text/plain but IE
        # do not support it
        response.setHeader('Content-Type', 'text/html; charset=utf-8')

        html = u'<dt>%s</dt><dd>%s</dd>';

        filename = self.request.form.get('filename')
        if filename is None:
            msg = u'Can not delete file; Filename does not exist.  Contact Administrator'
            return json.dumps({u'error': '%s' % msg,
                               u'html' : html % ('Error', msg)
                              })

        # Make sure draft proxy exists or we will be editing real content object
        if not isinstance(self.content, Z3cFormDraftProxy):
            msg = u'Can not delete %s; draft proxy is not enabled.  Contact Administrator' % filename
            return json.dumps({u'error': '%s' % msg,
                               u'html' : html % ('Error', msg)
                              })

        self.widget.widgets = [subwidget for subwidget in self.widget.widgets
                        if (filename != subwidget.filename)]
        self.widget.value = [subwidget.value for subwidget in self.widget.widgets]

        dm = zope.component.getMultiAdapter(
            (self.content, self.widget.field), interfaces.IDataManager)
        dm.set(interfaces.IDataConverter(self.widget).toFieldValue(self.widget.value))

        msg = u'%s sucessfully deleted.' % filename
        return json.dumps({u'success': '%s' % msg,
                           u'html' : html % ('Info', msg)
                          })