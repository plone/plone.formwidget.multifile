from zope.component import getMultiAdapter, queryMultiAdapter
from plone.formwidget.multifile.interfaces import ITemporaryFileHandler
from plone.formwidget.multifile.interfaces import IMultiFileWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IDataManager
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
        dm = queryMultiAdapter((self.widget.context, self.field),
                               IDataManager)
        try:
            original_value = dm.query()
        except TypeError:
            original_value = []

        if original_value and getattr(self.widget, '_converted', False):
            return original_value

        context = self.widget.form.context
        request = context.REQUEST
        handler = getMultiAdapter((context, request),
                                  ITemporaryFileHandler)
        new_value = []

        for subvalue in value:
            if isinstance(subvalue, unicode) and subvalue.startswith('new:'):
                temporary_file_key = subvalue.split(':')[1]
                new_value.append(handler.get(temporary_file_key))
            elif isinstance(subvalue, unicode) and subvalue.startswith('index:'):
                index = int(subvalue.split(':')[1])
                new_value.append(original_value[index])
            else:
                new_value.append(subvalue)

        self.widget._converted = True

        return new_value
