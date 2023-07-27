from plone.namedfile.interfaces import IFile
from Products.CMFCore.utils import getToolByName
from zope.publisher.interfaces import NotFound


def get_icon_for(context, file_):
    """Returns the best icon for the `file_`
    """
    mtr = getToolByName(context, 'mimetypes_registry', None)
    if mtr is None:
        return context.getIcon()
    if IFile.providedBy(file_):
        lookup = mtr.lookup(file_.contentType)
    else:
        lookup = (mtr.lookupExtension(file_.filename.rsplit('.')[-1]), )
    if lookup:
        mti = lookup[0]
        try:
            context.restrictedTraverse(mti.icon_path)
            return mti.icon_path
        except (NotFound, KeyError, AttributeError):
            pass
    return context.getIcon()
