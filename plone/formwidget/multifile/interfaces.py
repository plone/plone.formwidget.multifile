from plone.namedfile.field import NamedFile
from plone.app.drafts.interfaces import IDraft
from z3c.form.interfaces import IMultiWidget
from zope.interface import Interface


class IMultiFileWidget(IMultiWidget):
    """Marker interface for the multi file widget.
    """

