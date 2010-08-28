from plone.app.drafts.interfaces import ICurrentDraftManagement
from plone.app.drafts.utils import getCurrentUserId, getDefaultKey
from plone.app.drafts.interfaces import IDraftStorage
from plone.app.drafts.draft import Draft
from plone.formwidget.multifile.interfaces import ITemporaryFileHandler
from plone.formwidget.multifile.interfaces import ITemporaryFile
from zope.component import adapts, getUtility
from zope.interface import Interface, implements
from zope.schema.fieldproperty import FieldProperty


class TemporaryFile(Draft):
    """The `TemporaryFile` is used to store a file temporarily in the session
    for later use. This makes it possible to interactively upload files while
    editing a form.
    """

    implements(ITemporaryFile)

    file = FieldProperty(ITemporaryFile['file'])


class TemporaryFileHandler(object):
    """The `TemporaryFileHandler` adapter stores `TemporaryFile` instances in
    the session.
    It adapts the any context.
    """
    adapts(Interface, Interface)
    implements(ITemporaryFileHandler)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def create(self, file_):
        """Creates a draft for the file and appends it to the storage.
        The parameter `file_` is a normal file instance which should by
        accepted by the plone.app.namedfile field.
        """

        current = self._get_adapted_request()
        storage = self._get_draft_storage()
        draft = storage.createDraft(current.userId, current.targetKey,
                                    factory=TemporaryFile)
        draft.file = file_
        current.draft = draft
        current.draftName = draft.__name__

        current.save()
        return draft

    def get(self, key, default=None):
        """Returns a temporary file object identified by a key such
        as "admin:123:draft-10"
        """

        current = self._get_adapted_request()
        storage = self._get_draft_storage()
        draft = storage.getDraft(current.userId, current.targetKey, key)
        return draft.file

    def remove(self, key):
        """Removes a temporary file object form the storage and returns it.
        """

    def _get_draft_storage(self):
        """Returns the draft storage.
        """
        return getUtility(IDraftStorage)

    def _get_adapted_request(self):
        # returns the adapted request for the draft stuff
        adapted_request = ICurrentDraftManagement(self.request, None)
        adapted_request.userId = getCurrentUserId()
        adapted_request.targetKey = getDefaultKey(self.context)
        return adapted_request
