from zope.publisher.interfaces import NotFound
from Products.CMFCore.utils import getToolByName


def get_icon_for(self, file_):
    """Returns the best icon for the `file_`
    """
    mtr = getToolByName(self.context, 'mimetypes_registry', None)
    if mtr is None:
        return self.context.getIcon()
    lookup = mtr.lookup(file_.contentType)
    if lookup:
        mti = lookup[0]
        try:
            self.context.restrictedTraverse(mti.icon_path)
            return mti.icon_path
        except (NotFound, KeyError, AttributeError):
            pass
    return self.context.getIcon()
