from zope.component import queryMultiAdapter
from plone.formwidget.multifile.interfaces import IMultiFileWidget
from plone.namedfile.file import NamedFile
from plone.namedfile.file import INamedFile
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IDataManager
from zope.schema.interfaces import IList
import zope.component
from utils import basename


class MultiFileConverter(BaseDataConverter):
    """Converter for multi file widgets used on `schema.List` fields."""

    zope.component.adapts(IList, IMultiFileWidget)

    def toWidgetValue(self, value):
        """Converts the value to a form used by the widget."""
        return value

    def toFieldValue(self, value):
        """Converts the value to a storable form."""
        if not value:
            return value
        elif not isinstance(value, list):
            value = [value]
        else:
            # Filter out empty strings.
            value = [v for v in value if v]
            if not value:
                return value

        # Now we can be sure we have a non-empty list containing non-false
        # values.

        context = self.widget.context
        dm = queryMultiAdapter((context, self.field), IDataManager)

        # We check if the context implements the interface containing the field.
        # There are situations when this is not true, e.g when creating an
        # object an AJAX form validation is triggered.
        # In this case the context is the container.
        # If we do not check this then dm.query() may throw an exception.
        current_field_value = (
            dm.query()
            if ((dm is not None) and self.field.interface.providedBy(context))
            else None
        )

        if value is current_field_value:
            return value

        files = (self._toFieldSubValue(i, current_field_value) for i in value)
        return [f for f in files if (f is not None)]

    def _toFieldSubValue(self, subvalue, current_field_value):
        """
        Converts a subvalue to an `INamedFile`.

        Parameters:
        subvalue -- The value extracted from the request by the widget.
        current_field_value -- The current value of the field on the context.

        Return: an `INamedFile` or `None` if the subvalue cannot be converted.
        """
        if isinstance(subvalue, basestring) and subvalue.startswith('index:'):
            index = int(subvalue.split(':')[1])
            return current_field_value[index]
        elif INamedFile.providedBy(subvalue):
            return subvalue
        else:
            filename = getattr(subvalue, 'filename', None)
            if filename:
                filename = basename(filename)
                return NamedFile(subvalue, filename=filename.decode('utf-8'))

        return None
