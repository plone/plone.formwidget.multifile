from zope import interface
from zope import component

from zope.schema._bootstrapinterfaces import WrongType
from zope.dottedname.resolve import resolve

from plone.schemaeditor.fields import FieldFactory
from plone.schemaeditor import interfaces as schemaeditor_interfaces

from plone.namedfile.interfaces import INamedField

import z3c.form.browser.text
from z3c.form import validator
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import ITextWidget, NOVALUE
from z3c.form.widget import FieldWidget

from plone.formwidget.multifile.interfaces import IMultiFileField, IValueType
from plone.formwidget.multifile import MessageFactory
from plone.formwidget.multifile.field import MultiFile


def getDottedName(obj):
    """Returns the dotted.name
    """
    return u'%s.%s' % (obj.__class__.__module__, obj.__class__.__name__)


@interface.implementer(schemaeditor_interfaces.IFieldEditFormSchema)
@component.adapter(IMultiFileField)
def getMultiFileFieldSchema(field):
    return IMultiFileField


# Register us with schemaeditor
MultiFileFactory = FieldFactory(
    MultiFile,
    MessageFactory(u'label_multi_file_field', default=u'Multiple Files/Images'),
    )


# Just for schema editor
# Create a special TextWidget/Converter for value_type field so we can provide
# a value_type in dot notation
# ------------------------------------------------------------------------------
class TextLineValueTypeConverter(BaseDataConverter):
    """Data converter for IValueType to converted objects to dotted
    names and vice versa"""

    component.adapts(IValueType, ITextWidget)

    def toWidgetValue(self, value):
        """Convert from image object to HTML representation."""
        # if the value is the missing value, then an empty list is produced.
        if value is self.field.missing_value:
            return u''

        if not INamedField.providedBy(value):
            return u''
        return getDottedName(value)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value

        if INamedField.providedBy(value):
            return value

        try:
            obj = resolve(value)()
        except ImportError:
            return self.field.missing_value

        if not INamedField.providedBy(obj):
            return self.field.missing_value

        return obj


class TextWidget(z3c.form.browser.text.TextWidget):
    def extract(self, default=NOVALUE):
        value = super(TextWidget, self).extract(default)
        if value is NOVALUE:
            return value

        try:
            value = resolve(value)()
        except ImportError:
            return NOVALUE

        return value


class NamedFileWidgetValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        """See interfaces.IValidator"""

        result = None
        try:
            result = super(NamedFileWidgetValidator, self).validate(value)
        except WrongType:
            if not INamedField.providedBy(value):
                raise WrongType(value, self._type, self.__name__)

        return result

validator.WidgetValidatorDiscriminators(NamedFileWidgetValidator, field=IValueType)


@component.adapter(IValueType, z3c.form.interfaces.IFormLayer)
@interface.implementer(z3c.form.interfaces.IFieldWidget)
def TextFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, TextWidget(request))
