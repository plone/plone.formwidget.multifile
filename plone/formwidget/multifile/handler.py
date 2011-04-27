from plone.supermodel.exportimport import ObjectHandler
from plone.formwidget.multifile import field

class MultiFileFieldHandler(ObjectHandler):

    filteredAttributes = ObjectHandler.filteredAttributes.copy()
    filteredAttributes.update({'schema': 'rw'})

MultiFileHandler = MultiFileFieldHandler(field.MultiFile)
