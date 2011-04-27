from zope.interface import implements
from zope.schema import List

from plone.formwidget.multifile.interfaces import IMultiFileField


class MultiFile(List):
    """MultiFile field that provides addtional properties for widget
    (extends schema.List)
    """

    implements(IMultiFileField)

    # XXX: DEBUG test; trying to get proper schema to appear in editor!!
    _type = list
    #schema = IMultiFileField

    multi = True
    use_flash_upload = True
    size_limit = 0
    max_connections = 1
    allowable_file_extensions = u"*.*;"

    def __init__(self,
        multi=True,
        use_flash_upload=True,
        size_limit=0,
        max_connections=1,
        allowable_file_extensions=u"*.*;",
        **kw
    ):
        self.multi = multi
        self.use_flash_upload = use_flash_upload
        self.size_limit = size_limit
        self.max_connections = max_connections
        self.allowable_file_extensions = allowable_file_extensions

        super(MultiFile, self).__init__(**kw)
