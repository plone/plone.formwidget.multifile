from zope.publisher.interfaces import NotFound

from ZPublisher.HTTPRequest import HTTPRequest

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


def decodeQueryString(QueryString):
    """decode *QueryString* into a dictionary, as ZPublisher would do"""
    r = HTTPRequest(None,
                    {'QUERY_STRING' : QueryString,
                     'SERVER_URL' : '',
                     },
                    None,
                    1)
    r.processInputs()
    return r.form


def encode(s):
    """ encode string
    """

    return "d".join(map(str, map(ord, s)))


def decode(s):
    """ decode string
    """

    return "".join(map(chr, map(int, s.split("d"))))
