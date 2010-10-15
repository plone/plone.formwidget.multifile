from Acquisition import aq_inner

from zope.interface import alsoProvides
from z3c.form.interfaces import IFormLayer

from plone.z3cform.interfaces import IFormWrapper
from plone.z3cform import z2

from plone.app.kss.plonekssview import PloneKSSView

from kss.core import kssaction

from z3c.form.i18n import MessageFactory as _

from plone.formwidget.multifile.widget import decode
from plone.app.z3cformdrafts.drafting import Z3cFormDraftProxy


class MultifileRemove(PloneKSSView):
    """KSS actions for multifile remove actions
    """

    @kssaction
    def remove(self, formname, fieldname, filelistid, fileindex, filename):
        """Remove a file from the multifile draft
        """
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        alsoProvides(request, IFormLayer)

        # Find the form, the field and the widget
        form = request.traverseName(context, formname)
        if IFormWrapper.providedBy(form):
            formWrapper = form
            form = form.form_instance
            if not z2.IFixedUpRequest.providedBy(request):
                z2.switch_on(form, request_layer=formWrapper.request_layer)

        form.update()

        index = len(form.prefix) + len(form.widgets.prefix)
        raw_fieldname = fieldname[index:]
        widget = form.widgets.get(raw_fieldname, None)

        ksscore = self.getCommandSet('core')
        kssplone = self.getCommandSet('plone')

        # Put in a function, so it will not cache (for testing)
        remove(raw_fieldname, filelistid, filename, fileindex, widget, ksscore, kssplone)


def remove(fieldname, filelistid, filename, fileindex, widget, ksscore, kssplone):
    """Just used to test logic out since it will not be cached like class
    above!"""

    # Make sure draft proxy exists or we will be editing real content object
    if not isinstance(widget.context, Z3cFormDraftProxy):
        kssplone.issuePortalMessage(_(u'ERROR:  Can not delete %s; draft proxy is not enabled.  Contact Administrator' % filename), msgtype='error')
        return False

    try:
        filename = decode(filename)
    except ValueError:
        kssplone.issuePortalMessage(_(u'ERROR:  Can not delete %s; Can not decode filename.  Contact Administrator' % filename), msgtype='error')
        return False

    # Can not rely on index provided by browser to locate file since it is not
    # updated when a item is deleted; so loop though the values and to locate
    # file
    value = getattr(widget.context, fieldname, [])
    success = False
    for index, file_ in enumerate(value):
        if file_.filename == filename:
            value.pop(index)
            success = True
            break

    # Make sure we don't have a mismatch which can happen if user logs on
    # one machine; updates on another, then continues on original
    if not success:
        kssplone.issuePortalMessage(_(u'ERROR:  Can not delete %s since it could not be found.  Try reloading page first.' % filename), msgtype='error')
        return False

    nodeId = ksscore.getCssSelector('#%s .kssattr-fileindex-%s' % (filelistid, fileindex))
    kssplone.issuePortalMessage(_(u'Successfully Removed %s' % filename))
    ksscore.deleteNode(nodeId)
