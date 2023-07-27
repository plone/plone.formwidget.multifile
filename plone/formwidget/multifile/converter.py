from plone.formwidget.multifile.interfaces import IMultiFileWidget
from plone.namedfile.interfaces import INamed
from plone.namedfile.utils import safe_basename
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IDataManager
from z3c.form.interfaces import IEditForm
from zope.component import adapts
from zope.component import queryMultiAdapter
from zope.schema.interfaces import ISequence
from ZPublisher.HTTPRequest import FileUpload

import six


class MultiFileConverter(BaseDataConverter):
    """Converter for multi file widgets used on `schema.List` fields."""

    adapts(ISequence, IMultiFileWidget)

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

        context = self.widget.context
        dm = queryMultiAdapter((context, self.field), IDataManager)
        if dm is None:
            return

        if IEditForm.providedBy(self.widget.form):
            current_field_value = dm.query()
        else:
            current_field_value = []

        collection_type = self.field._type
        files = (self._toFieldSubValue(i, current_field_value) for i in value)
        return collection_type(f for f in files if (f is not None))

    def _toFieldSubValue(self, value, current_field_value):
        """
        Converts a subvalue to an `INamedFile`.

        Parameters:
        value -- The value extracted from the request by the widget.
        current_field_value -- The current value of the field on the context.

        Return:
        a value of the fields value_type or it's `missing_value` if the value cannot be converted.

        See plone.formwidget.namedfile.converter.NamedDataConverter
        """

        value_type = self.field.value_type._type
        missing_value = self.field.value_type.missing_value

        if value is None or value == '':
            return missing_value
        elif INamed.providedBy(value):
            return value
        elif isinstance(value, six.string_types) and value.startswith('index:'):
            # we already have the file
            index = int(value.split(':')[1])
            try:
                return current_field_value[index]
            except IndexError:
                return missing_value
        elif isinstance(value, FileUpload):
            # create a new file

            headers = value.headers
            filename = safe_basename(value.filename)
            if filename is not None and not isinstance(filename, six.text_type):
                # Work-around for
                # https://bugs.launchpad.net/zope2/+bug/499696
                filename = filename.decode('utf-8')

            contentType = 'application/octet-stream'
            if headers:
                contentType = headers.get('Content-Type', contentType)

            value.seek(0)
            data = value.read()
            if data or filename:
                return value_type(data=data, contentType=contentType, filename=filename)
            else:
                return missing_value

        else:
            return value_type(data=str(value))
