from plone.namedfile.field import NamedFile
from plone.app.drafts.interfaces import IDraft
from z3c.form.interfaces import IMultiWidget
from zope.interface import Interface


class IMultiFileWidget(IMultiWidget):
    """Marker interface for the multi file widget.
    """

#from zope.interface import Interface, implements
#from zope.component import adapts
from zope.schema import Bool, Int, Text
#from Products.CMFDefault.formlib.schema import SchemaAdapterBase
#from Products.CMFPlone.interfaces import IPloneSiteRoot
#from Products.CMFCore.utils import getToolByName
#from zope.formlib.form import FormFields
#from plone.app.controlpanel.form import ControlPanelForm
from z3c.form.i18n import MessageFactory as _
from zope.schema.interfaces import IObject

class IMultiFile(IObject):
    """
    Additional Fields for Multifile
    """
    use_flashupload = Bool(title=_(u"title_use_flashupload", default=u"Use Flash Upload"),
                           description=_(u"description_use_flashupload",
                                          default=u"By default, the upload script is a javascript only tool. "
                                          "Check this option to replace it with a Flash Upload based script. "
                                          "For modern browsers the javascript tool is more powerful. "
                                          "Flash Upload is just more user friendly under other browsers (MSIE 7, MSIE 8),  "
                                          "but has many problems : don't work in https, don't work behind HTTP Authentication ..."),
                           default=False,
                           required=False)
    auto_upload = Bool(title=_(u"title_auto_upload", default=u"Automatic upload on select"),
                                 description=_(u"description_auto_upload", default=u"Check if you want to start the files upload on select, without submit the form. "
                                                "Note that you cannot choose file titles "
                                                "with this option set to True."),
                                 default=False,
                                 required=False)
    fill_titles = Bool(title=_(u"title_fill_titles", default=u"Fill title before upload"),
                                 description=_(u"description_fill_titles", default=u"If checked, you can fill the files titles "
                                                "before upload. Uncheck if you don't need titles."),
                                 default=True,
                                 required=False)

    size_limit = Int( title=_(u"title_size_limit", default=u"Size limit"),
                      description=_(u"description_size_limit", default=u"Size limit for each file in KB, 0 = no limit"),
                      default=0,
                      required=True)

    sim_upload_limit = Int( title=_(u"title_sim_upload_limit", default=u"Simultaneous uploads limit"),
                            description=_(u"description_sim_upload_limit", default=u"Number of simultaneous files uploaded, over this number uploads are placed in a queue, 0 = no limit"),
                            default=2,
                            required=True)

    allowable_file_extensions = Text( title=_(u"title_allowable_file_extensions", default=u"Allowable file extensions"),
                            description=_(u"description_allowable_file_extensions", default=u"Allowable file extensions seperated by a semi-colon or type of image, video, audio or flash."),
                            default=u"*.*;",
                            required=False)
