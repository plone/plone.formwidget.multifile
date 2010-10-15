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
    use_flashupload = False
    size_limit = 0
    sim_upload_limit = 1
    allowable_file_extensions = u"*.*;"

    def __init__(self,
        multi=True,
        use_flashupload=False,
        size_limit=0,
        sim_upload_limit=1,
        allowable_file_extensions=u"*.*;",
        **kw
    ):
        self.multi = multi
        self.use_flashupload = use_flashupload
        self.size_limit = size_limit
        self.sim_upload_limit = sim_upload_limit
        self.allowable_file_extensions = allowable_file_extensions

        super(MultiFileField, self).__init__(**kw)
