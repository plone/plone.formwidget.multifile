from Products.Five.browser import BrowserView
from Acquisition import aq_inner, aq_parent
from plone.formwidget.multifile.interfaces import IMultiFileWidget
from plone.formwidget.multifile.utils import get_icon_for
from z3c.form.interfaces import IFieldWidget, IDataConverter
from z3c.form.widget import FieldWidget
from z3c.form.widget import MultiWidget
from zope.app.component.hooks import getSite
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.browser.interfaces import IBrowserView
from zope.interface import implements, implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.component import queryMultiAdapter

from z3c.form import interfaces
from z3c.form.i18n import MessageFactory as _
from operator import attrgetter

import zope.component

def encode(s):
    """ encode string
    """

    return "d".join(map(str, map(ord, s)))


def decode(s):
    """ decode string
    """

    return "".join(map(chr, map(int, s.split("d"))))

#
#            'script'        : '%(action_url)s',
#            'script'        : '@@multi-file-upload-file',
#
INLINE_JAVASCRIPT = """
    jq(document).ready(function() {
        function escapeExpression(str) {
            return str.replace(/([#;&,\.\+\*\~':"\!\^$\[\]\(\)=>\|])/g, "\\$1");
        }

        var parse_response = function(data){
            if(typeof data == "string"){
                try{//try to parse if it's not already done...
                    data = $.parseJSON(data);
                }catch(e){
                    try{
                        data = eval("(" + data + ")");
                    }catch(e){
                        //do nothing
                    }
                }
            }
            return data
        }

        jq('#%(name)s').uploadify({
            'uploader'      : '++resource++uploadify.swf',
            'script'        : '%(action_url)s',
            'fileDataName'  : 'form.widgets.%(field_name)s.buttons.add',
            'cancelImg'     : '++resource++cancel.png',
            'height'        : '30',
            'width'         : '110',
            'folder'        : '%(physical_path)s',
            'scriptData'    : {'cookie': '%(cookie)s'},
            'onSelect'      : function(event, queueId, fileObj) {
                var e = document.getElementById('form-widgets-%(field_name)s-count');
                var count = parseInt(e.getAttribute('value'));
                e.setAttribute('value', count+1);
                var filename = 'form.widgets.%(field_name)s.'+(count);
                scriptData = {'__ac': '%(ac)s',
                             }
                jq('#%(name)s').uploadifySettings( 'scriptData', scriptData, true );
            },
            'onComplete'    : function (event, queueID, fileObj, responseJSON, data) {
                var fieldname = jq(event.target).attr('ref');

                //alert( responseJSON );

                obj = parse_response(responseJSON);

                //alert(obj.status);

                if( obj.status == 'error' ) { return false; }

                //alert(obj.html);

                jq(event.target).siblings('.multi-file-files:first').each(
                    function() {
                        jq(this).append(jq(document.createElement('li')).html(obj.html).attr('class', 'multi-file-file'));

                        //var e = document.getElementById('form-widgets-%(field_name)s-count');
                        //e.setAttribute('value', obj.counter);

                    });
                },
            'auto'          : true,
            'multi'         : true,
            'simUploadLimit': '4',
            'queueSizeLimit': '999',
            'sizeLimit'     : '',
            'fileDesc'      : '',
            'fileExt'       : '*.*',
            'buttonText'    : 'BROWSE',
            'buttonImg'     : '',
            'scriptAccess'  : 'sameDomain',
            'hideButton'    : false
        });
    });
"""


#from Acquisition import Explicit
#class MultiFileWidget(Explicit, MultiWidget):
#class MultiFileWidget(MultiWidget):
import z3c.form.browser.multi
from z3c.form import button
class MultiFileWidget(z3c.form.browser.multi.MultiWidget):
    implements(IMultiFileWidget, IPublishTraverse)

    klass = u'multi-file-widget'

    input_template = ViewPageTemplateFile('input.pt')
    #input_template = ViewPageTemplateFile('file_input.pt')
    display_template = ViewPageTemplateFile('display.pt')
    file_template = ViewPageTemplateFile('file_template.pt')

    json_response = None

    @property
    def counterMarker(self):
        # this get called in render from the template and contains always the
        # right amount of widgets we use.
        return '<input id="%s" type="hidden" name="%s" value="%d" />' % (
            self.counterName.replace('.', '-'), self.counterName, len(self.widgets))

    @property
    def better_context(self):
        return self.form.context

    def render(self):
        self.update()
        if self.mode == 'input':
            if self.json_response is not None:
                return self.json_response
            else:
                return self.input_template(self)
        else:
            return self.display_template(self)

    def editing(self):
        return self.mode == 'input'

    def get_data(self):
        """
        """
        if self.value:
            converter = IDataConverter(self)
            converted_value = converter.toFieldValue(self.value)
            for i, file_ in enumerate(self.value):
                yield self.render_file(file_, index=i)

    #def render_file(self, file_, value=None, index=None, context=None):
    def render_file(self, file_, index=None, context=None):
        """Renders the <li> for one file.
        """
        if context == None:
            context = self.better_context

        #if value == None and index == None:
        if index == None:
            raise ValueError('Either value or index expected')

        #if value == None:
        value = 'index:%i' % index
        view_name = self.name[len(self.form.prefix):]
        view_name = view_name[len(self.form.widgets.prefix):]
        download_url = '%s/++widget++%s/%i/@@download/%s' % (
            self.request.getURL(),
            view_name,
            index,
            file_.filename
            )
        remove_url = '%s/++widget++%s/%i/@@download/%s' % (
            self.request.getURL(),
            view_name,
            index,
            file_.filename
            )

        options = {'value': value,
                   'icon': '/'.join((context.portal_url(),
                                     get_icon_for(context, file_))),
                   'filename': file_.filename,
                   'size': int(round(file_.getSize() / 1024)),
                   'download_url': download_url,
                   'widget': self,
                   'editable': self.mode == 'input',
                   'remove_url': remove_url,
                   }

        return self.file_template(**options)

    def update(self):
        super(MultiFileWidget, self).update()
        self.portal = getSite()

    def get_inline_js(self):
        return INLINE_JAVASCRIPT % self.get_settings()

    def get_settings(self):
        from Products.PythonScripts.standard import url_quote
        fieldName = self.field.__name__
        requestURL = "/".join(self.request.physicalPathFromURL(self.request.getURL()))
        widgetURL = requestURL + '/++widget++' + fieldName
        return dict(
            name=self.get_uploader_id(),
            cookie=encode(self.request.cookies.get(
                    '__ac', '')),
            ac=url_quote(self.request.get('__ac', '')),
            physical_path="/".join(self.better_context.getPhysicalPath()),
            field_name=fieldName,
            formname=url_quote(self.request.getURL().split('/')[-1]),
            widget_url=url_quote(widgetURL),
            action_url=url_quote(widgetURL),
            )

    def get_uploader_id(self):
        """Returns the id attribute for the uploader div. This should
        be uniqe, also when using multiple widgets on the same page.
        """
        return 'multi-file-%s' % self.name.replace('.', '-')

    def publishTraverse(self, request, name):
        widget = self.widgets[int(name)].__of__(self.better_context)
        # fix some stuff, according to z3c.form.field.FieldWidgets.update
        widget.name = self.name + '.' + name
        widget.__name__ = name
        widget.id = self.name.replace('.', '-')
        widget.form = self.form
        widget.ignoreContext = self.ignoreContext
        widget.ignoreRequest = self.ignoreRequest
        widget.mode = self.mode
        widget.update()
        widget.field.__name__ = name

        # we need to be able to do something like
        # getattr(widget.context, widget.field.__name__)
        # and it should return the value

        class objectish_list(list):
            def __getattr__(self, k):
                return self[int(k)]

        widget.context = objectish_list(self.value)

        return widget

    def extract(self, default=interfaces.NO_VALUE):
        # This method is responsible to get the widgets value based on the
        # widget value only since items are never added via a form directly
        # (tey are added one at a time via ajax).
        if self.request.get(self.counterName) is None:
            # counter marker not found
            return interfaces.NO_VALUE
        counter = int(self.request.get(self.counterName, 0))
        values = []
        append = values.append
        # extract value for existing widgets
        value = zope.component.getMultiAdapter( (self.context, self.field),
                                                interfaces.IDataManager).query()
        for idx in range(counter):
            widget = self.getWidget(idx)
            # Added for drafts code since its possible to have counter and no
            # request.form value; especially if ajax validation is enabled
            if (widget.value is None and widget.name not in self.request):
                if not isinstance(value, list) or idx >= len(value):
                    continue
                widget.value = value[idx]
            append(widget.value)
        if len(values) == 0:
            # no multi value found
            return interfaces.NO_VALUE
        return values

    @button.buttonAndHandler(_('Add'), name='add',
                             condition=attrgetter('allowAdding'))
    def handleAdd(self, action):
        """The uploadify flash calls this view for every file added interactively.
        This view saves the file in the session and returns the key where the file
        can be found in the session. When the form is actually submitted the
        widget gets the file from the session and stores it in the actual target.
        """
        try:
            import json
        except:
            import simplejson as json

        SUCCESS = {"status": "success"}
        ERROR =   {"status": "error"}

        # WORKS
        index = len(self.value)
        newWidget = self.getWidget(index)
        converter = IDataConverter(newWidget)
        newWidget.value = converter.toFieldValue(action.extract())
        self.value.append(newWidget.value)
        self.updateWidgets()

        response = {"filename" : newWidget.filename,
                    "html"     : self.render_file(newWidget.value, index=index)
                    }
        response.update(SUCCESS)
        self.json_response = json.dumps(response)

        #return json.dumps(ERROR)

    def __call__(self):
        return self.render()

@implementer(IFieldWidget)
def MultiFileFieldWidget(field, request):
    return FieldWidget(field, MultiFileWidget(request))
