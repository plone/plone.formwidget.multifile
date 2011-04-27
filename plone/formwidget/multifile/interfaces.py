from zope.interface import Interface, alsoProvides

from zope.schema import Bool, Int, Text, List
from zope.schema import interfaces

from z3c.form.i18n import MessageFactory as _
from z3c.form.interfaces import IMultiWidget

from plone.namedfile.interfaces import HAVE_BLOBS
if HAVE_BLOBS:
    from plone.namedfile.field import NamedBlobImage as NamedImage
else:
    from plone.namedfile.field import NamedImage


class IMultiFileWidget(IMultiWidget):
    """Marker interface for the multi file widget.
    """


class IValueType(Interface):
    """Marker interface for value_type field so we can adapt a custom widget
    """


class IList(Interface):
    """Marker interface to allow default/missing_field to adapt to IList widget
    """


class IMultiFileField(interfaces.IList):
    """
    Additional Fields for Multifile
    """
    multi = Bool(
        title=_(u"title_multi", default=u"Allow Multiple File Uploads"),
        description=_(
            u"description_multi",
            default=u"Allow multiple file uploads if True, or only one file if False"),
        default=True,
        required=False)

    use_flash_upload = Bool(
        title=_(u"title_use_flash_upload", default=u"Use Flash Upload"),
        description=_(
            u"description_use_flash_upload",
            default=u"By default, the upload script is a javascript only tool. "
                    u"Check this option to replace it with a Flash Upload based script. "
                    u"For modern browsers the javascript tool is more powerful. "
                    u"Flash Upload is just more user friendly under other browsers (MSIE 7, MSIE 8),  "
                    u"but has many problems : don't work in https, don't work behind HTTP Authentication ..."),
        default=False,
        required=False)

    size_limit = Int(
        title=_(u"title_size_limit", default=u"Size limit"),
        description=_(
            u"description_size_limit",
            default=u"Size limit for each file in KB, 0 = no limit"),
        default=0,
        required=False)

    max_connections = Int(
        title=_(u"title_max_connections", default=u"Maximum number of simultaneous file connections allowed"),
        description=_(
            u"description_max_connections",
            default=u"Maximum number of simultaneous file connections allowed, over "
                    u"this number uploads are placed in a queue, 0 = no limit"),
        default=1,
        required=False)

    allowable_file_extensions = Text(
        title=_(u"title_allowable_file_extensions", default=u"Allowable file extensions"),
        description=_(
            u"description_allowable_file_extensions",
            default=u"Allowable file extensions seperated by a semi-colon or type of image, video, "
                    u"audio or flash."),
        default=u"*.*;",
        required=False)

    value_type = NamedImage(
        title=_("Value Type"),
        description=_(u"Enter the dotted name to the Image type field like "
                       u"plone.namedfile.field.NamedBlobImage."),
        required=True)
    alsoProvides(value_type, IValueType)

    default = List(
        title=interfaces.IList['default'].title,
        description=interfaces.IList['default'].description,
        required=False)
    alsoProvides(default, IList)

    missing_value = List(
        title=interfaces.IList['missing_value'].title,
        description=interfaces.IList['missing_value'].description,
        required=False)
    alsoProvides(missing_value, IList)


class IImageScaleTraversable(Interface):
    """Marker for items that should provide access to image scales for named
    image fields via the @@images view.
    """
