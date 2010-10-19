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

    use_flashupload = Bool(title=_(u"title_use_flashupload", default=u"Use Flash Upload"),
                           description=_(u"description_use_flashupload",
                                          default=u"By default, the upload script is a javascript only tool. "
                                          "Check this option to replace it with a Flash Upload based script. "
                                          "For modern browsers the javascript tool is more powerful. "
                                          "Flash Upload is just more user friendly under other browsers (MSIE 7, MSIE 8),  "
                                          "but has many problems : don't work in https, don't work behind HTTP Authentication ..."),
                           default=True,
                           required=False)

    size_limit = Int( title=_(u"title_size_limit", default=u"Size limit"),
                      description=_(u"description_size_limit", default=u"Size limit for each file in KB, 0 = no limit"),
                      default=0,
                      required=False)

    sim_upload_limit = Int( title=_(u"title_sim_upload_limit", default=u"Simultaneous uploads limit"),
                            description=_(u"description_sim_upload_limit", default=u"Number of simultaneous files uploaded, over this number uploads are placed in a queue, 0 = no limit"),
                            default=2,
                            required=False)

    allowable_file_extensions = Text( title=_(u"title_allowable_file_extensions", default=u"Allowable file extensions"),
                            description=_(u"description_allowable_file_extensions", default=u"Allowable file extensions seperated by a semi-colon or type of image, video, audio or flash."),
                            default=u"*.*;",
                            required=False)
