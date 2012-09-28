from zope.component import queryMultiAdapter
from plone.formwidget.multifile.interfaces import IMultiFileWidget
from plone.namedfile.file import NamedFile
from plone.namedfile.file import INamedFile
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IDataManager
from zope.schema.interfaces import IList
import zope.component
import re


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
        if not value:
            return value

        if not isinstance(value, list):
            value = [value]

        dm = queryMultiAdapter(
            (self.widget.context, self.field),
            IDataManager
        )

        original_value = dm.query() if (dm is not None) else []

        if value is original_value:
            return value

        new_value = []

        for subvalue in value:
            if isinstance(subvalue, basestring) and subvalue.startswith('index:'):
                index = int(subvalue.split(':')[1])
                new_value.append(original_value[index])
            elif INamedFile.providedBy(subvalue):
                new_value.append(subvalue)
            else:
                filename = getattr(subvalue, 'filename', None)
                if filename:
                    # Strip out directories leaving only the file name.
                    filename = re.split(r'[\\/]+', filename)[-1]

                    f = NamedFile(subvalue, filename=filename.decode('utf-8'))
                    new_value.append(f)

        return new_value
