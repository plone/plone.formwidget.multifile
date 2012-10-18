from zope.publisher.interfaces import NotFound
from Products.CMFCore.utils import getToolByName
from zope.app.file.interfaces import IFile
import re


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


def basename(path):
    """
    Given a path strip out directories leaving only the file name.

    Note: we don't use `os.path.basename` because this function works only
    if the given path uses the same directory delimiter of the current operating
    system. We need to handle both "/" and "\".
    """
    return re.split(r'[\\/]+', path)[-1]
