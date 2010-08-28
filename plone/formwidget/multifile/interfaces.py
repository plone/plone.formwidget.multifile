from plone.namedfile.field import NamedFile
from plone.app.drafts.interfaces import IDraft
from z3c.form.interfaces import IWidget
from zope.interface import Interface


class IMultiFileWidget(IWidget):
    """Marker interface for the multi file widget.
    """


class ITemporaryFileHandler(Interface):
    """Marker interface for the temporary file handler adapter.
    """

    def create(self, temporary_file):
        """Appending a temporary file to the storage.
        """

    def get(self, key, default=None):
        """Returns a temporary file object identified by key.
        """

    def remove(self, key):
        """Removes a temporary file object form the storage and returns it.
        """


class ITemporaryFile(IDraft):
    """TemporaryFile schema
    """

    file = NamedFile(title=u'File', required=False)
