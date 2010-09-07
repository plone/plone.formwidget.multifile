from zope.publisher.interfaces import NotFound
from Products.CMFCore.utils import getToolByName


def get_icon_for(context, file_):
    """Returns the best icon for the `file_`
    """
    mtr = getToolByName(context, 'mimetypes_registry', None)
    if mtr is None:
        return context.getIcon()
    if file_.contentType == '':
        lookup = None
    else:
        lookup = mtr.lookup(file_.contentType)
    if lookup:
        mti = lookup[0]
        try:
            context.restrictedTraverse(mti.icon_path)
            return mti.icon_path
        except (NotFound, KeyError, AttributeError):
            pass
    return context.getIcon()
