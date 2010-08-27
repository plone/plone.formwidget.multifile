from plone.formwidget.multifile import IMultiFileWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.app.component.hooks import getSite
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implements, implementer


class MultiFileWidget(Widget):
    implements(IMultiFileWidget)

    klass = u'multi-file-widget'

    input_template = ViewPageTemplateFile('input.pt')

    def render(self):
        return self.input_template(self)

    def update(self):
        self.portal = getSite()


@implementer(IFieldWidget)
def QueryStringFieldWidget(field, request):
    return FieldWidget(field, MultiFileWidget(request))
