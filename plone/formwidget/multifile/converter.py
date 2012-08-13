from zope.component import getMultiAdapter, queryMultiAdapter
from plone.formwidget.multifile.interfaces import ITemporaryFileHandler
from plone.formwidget.multifile.interfaces import IMultiFileWidget
from plone.namedfile.file import NamedFile
from plone.namedfile.file import INamedFile
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
        
        if not value:
            return value

        if not isinstance(value, list):
            value = [value]
            
        dm = queryMultiAdapter(
            (self.widget.context, self.field),
            IDataManager
            )

        try:
            original_value = dm.query()
        except TypeError:
            original_value = []

        if value is original_value:
            return value

        handler = getattr(self.widget, '_handler', None)
        if handler is None:
            context = self.widget.form.context
            request = self.widget.request
            handler = self.widget._handler = getMultiAdapter(
                (context, request), ITemporaryFileHandler
                )

        new_value = []

        for subvalue in value:
            if isinstance(subvalue, basestring) and subvalue.startswith('new:'):
                temporary_file_key = subvalue.split(':')[1]
                new_value.append(handler.get(temporary_file_key))
            elif isinstance(subvalue, basestring) and subvalue.startswith('index:'):
                index = int(subvalue.split(':')[1])
                new_value.append(original_value[index])
            elif INamedFile.providedBy(subvalue):
                new_value.append(subvalue)
            elif subvalue.filename:
                file_ = NamedFile(subvalue, filename=subvalue.filename.decode('utf-8'))
                draft = handler.create(file_)
                file_.draftName = draft.__name__
                new_value.append(file_)
                subvalue.seek(0)

        return new_value
