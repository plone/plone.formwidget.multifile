import zope.i18nmessageid
from zope.interface import implements
from zope.schema import List

from plone.formwidget.multifile.widget import MultiFileWidget
MultiFileWidget
from plone.formwidget.multifile.widget import MultiFileFieldWidget
MultiFileFieldWidget

from plone.formwidget.multifile.interfaces import IMultiFileField


MessageFactory = zope.i18nmessageid.MessageFactory(
    'plone.formwidget.multifile')


class MultiFileField(List):
    """MultiFileField that provides addtional properties for widget
    (extends schema.List)
    """

    implements(IMultiFileField)

    multi = True
    useFlashUpload = True
    sizeLimit = 0
    maxConnections = 1
    allowableFileExtensions = u"*.*;"

    def __init__(self,
        multi=True,
        useFlashUpload=True,
        sizeLimit=0,
        maxConnections=1,
        allowableFileExtensions=u"*.*;",
        **kw
    ):
        self.multi = multi
        self.useFlashUpload = useFlashUpload
        self.sizeLimit = sizeLimit
        self.maxConnections = maxConnections
        self.allowableFileExtensions = allowableFileExtensions

        super(MultiFileField, self).__init__(**kw)
