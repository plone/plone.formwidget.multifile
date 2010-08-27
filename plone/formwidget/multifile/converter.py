from z3c.form.converter import BaseDataConverter
from zope.schema.interfaces import IList
from plone.formwidget.multifile.interfaces import IMultiFileWidget
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
        return value
