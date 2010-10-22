from zope.interface import Interface
from zope.schema import Bool, Int, Text
from zope.schema.interfaces import IObject

from plone.namedfile.field import NamedFile
from plone.app.drafts.interfaces import IDraft

from z3c.form.i18n import MessageFactory as _
from z3c.form.interfaces import IMultiWidget


class IMultiFileWidget(IMultiWidget):
    """Marker interface for the multi file widget.
    """


class IMultiFileField(IObject):
    """
    Additional Fields for Multifile
    """
    multi = Bool( title=_(u"title_multi", default=u"Allow Multiple File Uploads"),
                  description=_(u"description_multi", default=u"Allow multiple file uploads if True, or only one file if False"),
                  default=True,
                  required=False)

    useFlashUpload = Bool(title=_(u"title_useFlashUpload", default=u"Use Flash Upload"),
                           description=_(u"description_useFlashUpload",
                                         default=u"By default, the upload script is a javascript only tool. "
                                         "Check this option to replace it with a Flash Upload based script. "
                                         "For modern browsers the javascript tool is more powerful. "
                                         "Flash Upload is just more user friendly under other browsers (MSIE 7, MSIE 8),  "
                                         "but has many problems : don't work in https, don't work behind HTTP Authentication ..."),
                           default=True,
                           required=False)

    sizeLimit = Int( title=_(u"title_sizeLimit", default=u"Size limit"),
                      description=_(u"description_sizeLimit", default=u"Size limit for each file in KB, 0 = no limit"),
                      default=0,
                      required=False)

    maxConnections = Int( title=_(u"title_maxConnections", default=u"Maximum number of simultaneous file connections allowed"),
                            description=_(u"description_maxConnections",
                                          default=u"Maximum number of simultaneous file connections allowed, over "
                                          "this number uploads are placed in a queue, 0 = no limit"),
                            default=2,
                            required=False)

    allowableFileExtensions = Text( title=_(u"title_allowableFileExtensions", default=u"Allowable file extensions"),
                            description=_(u"description_allowableFileExtensions", default=u"Allowable file extensions seperated by a semi-colon or type of image, video, audio or flash."),
                            default=u"*.*;",
                            required=False)
