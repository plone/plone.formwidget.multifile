from zope.component import getMultiAdapter
from plone.formwidget.multifile.interfaces import ITemporaryFileHandler
from plone.formwidget.multifile.interfaces import IMultiFileWidget
from z3c.form.converter import BaseDataConverter
from zope.schema.interfaces import IList
import zope.component


class MultiFileConverter(BaseDataConverter):
    """Converter for multi file widgets used on `schema.List` fields.
    """

    zope.component.adapts(IList, IMultiFileWidget)

    def toWidgetValue(self, value):
        """Converts the value to a form used by the widget.
        """
        return value

    def toFieldValue(self, value):
        """Converts the value to a storable form.
        """
        # we need to get the original value from the widget, which get
        # with ignore the request
#         ignoreRequest = self.widget.ignoreRequest
#         self.widget.update()
#         orignal_value = self.widget.value
#         self.widget.ignoreRequest = ignoreRequest
#         self.widget.value = None

        context = self.widget.context
        request = context.REQUEST
        handler = getMultiAdapter((context, request),
                                  ITemporaryFileHandler)
        new_value = []
        for subvalue in value:
            if subvalue.startswith('new:'):
                temporary_file_key = subvalue.split(':')[1]
                new_value.append(handler.get(temporary_file_key))
#             elif subvalue.startswith('index:'):
#                 index = int(temporary_file_key.split(':')[1])
#                 new_value.append(orignal_value[index])
            else:
                new_value.append(subvalue)
        return new_value
