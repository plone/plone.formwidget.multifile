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

from z3c.form import interfaces


def encode(s):
    """ encode string
    """

    return "d".join(map(str, map(ord, s)))


def decode(s):
    """ decode string
    """

    return "".join(map(chr, map(int, s.split("d"))))

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
            'script'        : '@@multi-file-upload-file',
            'fileDataName'  : 'multifile.file',
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
                scriptData = {'cookie': '%(cookie)s',
                              'multifile.formname' : '%(formname)s',
                              'multifile.fieldname': '%(field_name)s',
                             }
                jq('#%(name)s').uploadifySettings( 'scriptData', scriptData, true );
            },
            'onComplete'    : function (event, queueID, fileObj, responseJSON, data) {
                var fieldname = jq(event.target).attr('ref');

                obj = parse_response(responseJSON);
                if( obj.status == 'error' ) { return false; }

                jq(event.target).siblings('.multi-file-files:first').each(
                    function() {
                        jq(this).append(jq(document.createElement('li')).html(obj.html).attr('class', 'multi-file-file'));

                        var e = document.getElementById('form-widgets-%(field_name)s-count');
                        e.setAttribute('value', obj.counter);

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
class MultiFileWidget(MultiWidget):
    implements(IMultiFileWidget, IPublishTraverse)

    klass = u'multi-file-widget'

    input_template = ViewPageTemplateFile('input.pt')
    display_template = ViewPageTemplateFile('display.pt')
    file_template = ViewPageTemplateFile('file_template.pt')

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
            return self.input_template(self)
        else:
            return self.display_template(self)

    def editing(self):
        return self.mode == 'input'

    def get_data(self):
        """
        """
        if self.value:
            # sometimes the value contains the strings from the form,
            # sometimes it's already converted by the converter. But
            # if we have errors and we are trying to add a new file
            # (thats when entry is a unicode string) we need to put
            # that string again in the form since we did not store the
            # file yet, but we can get the file from the converter..
            converter = IDataConverter(self)
            converted_value = converter.toFieldValue(self.value)
            for i, key_or_file in enumerate(self.value):
                # DEBUG:  just here for testing
                if key_or_file is None:
                    continue
                if isinstance(key_or_file, unicode):
                    file_ = converted_value[i]
                    yield self.render_file(file_, value=key_or_file)

                else:
                    yield self.render_file(key_or_file, index=i)

    def render_file(self, file_, value=None, index=None, context=None):
        """Renders the <li> for one file.
        """
        if context == None:
            context = self.better_context

        if value == None and index == None:
            raise ValueError('Either value or index expected')

        if value == None:
            value = 'index:%i' % index
            view_name = self.name[len(self.form.prefix):]
            view_name = view_name[len(self.form.widgets.prefix):]
            download_url = '%s/++widget++%s/%i/@@download/%s' % (
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
            physical_path="/".join(self.better_context.getPhysicalPath()),
            field_name=fieldName,
            formname=url_quote(self.request.getURL().split('/')[-1]),
            widget_url=url_quote(widgetURL),
            )

    def get_uploader_id(self):
        """Returns the id attribute for the uploader div. This should
        be uniqe, also when using multiple widgets on the same page.
        """
        return 'multi-file-%s' % self.name.replace('.', '-')

    def extract(self, default=interfaces.NO_VALUE):
        import re
        count = 0
        pattern = re.compile('%s.[\d]+$' % self.name)
        for key in self.request.form:
            if pattern.match(key):
                count += 1

        values = []
        append = values.append

        # extract value for existing widgets
        for idx in range(count):
            widget = self.getWidget(idx)
            append(widget.value)
        if len(values) == 0:
            # no multi value found
            return interfaces.NO_VALUE
        return values

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


@implementer(IFieldWidget)
def MultiFileFieldWidget(field, request):
    return FieldWidget(field, MultiFileWidget(request))


class UploadFileToSessionView(BrowserView):
    """The uploadify flash calls this view for every file added interactively.
    This view saves the file in the session and returns the key where the file
    can be found in the session. When the form is actually submitted the
    widget gets the file from the session and stores it in the actual target.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

        cookie = self.request.form.get("cookie")
        if cookie:
            self.request.cookies["__ac"] = decode(cookie)

    def __call__(self):
        try:
            import json
        except:
            import simplejson as json

        SUCCESS = {"status": "success"}
        ERROR =   {"status": "error"}

        try:
            ####################################################################
            # file_: FileUpload object
            # formname: name of form (IE: ++add++content.type; edit)
            # fieldname: name of content type attr field (IE: files)
            ####################################################################
            file_ = self.request.form.get('multifile.file')
            formname = self.request.form.get('multifile.formname')
            fieldname = self.request.form.get('multifile.fieldname')

            # in some cases the context is the view, so lets walk up
            # and search the real context
            context = self.context
            while IBrowserView.providedBy(context):
                context = aq_parent(aq_inner(context))

            # Get form so it will automatically save data on draft
            ######################################################
            # BUG <--- FIX!!
            ######################################################
            # FOR plone 3
            #form = context.context.restrictedTraverse(formname)
            # FOR plone 4
            form = context.restrictedTraverse(formname)

            form = form.form_instance

            ####################################################################
            # TODO; make sure we add IDraftIgnoreAllBehaviors... incase content
            # type does not have draft behavior enabled
            ####################################################################

            # form.update() will force all current draft data to be loaded on to
            # the request.form so we can gain access it to it
            form.update()

            # NOTE:
            # ------------------------------------------------------------------
            # You could not access draft directly to lookup or store aything
            # like this: self.request.DRAFT.  Don't store things directly in
            # _form though; let the drafts module take care of it automattically
            # by just placeing whatever values on request.form and call
            # form.update() again... it will store the draft properly (convert
            # needed values, etc).

            # Grab the widget for this fieldname
            widget = form.widgets.get(fieldname)

            # Get current list length, so we know where to add on to
            counter = len(widget.value)

            # Create a form.widgets.<field_name>.<index> name
            subwidgetName = widget.name + '.%d' % counter

            # Increase counter by 1 (will send back to browser so it can
            # update widget.names.<field_name>.count
            counter += 1

            # Update request with new counter value; make sure its unicode!
            self.request.form[widget.counterName] = unicode(counter)

            # add file_ to request.form
            self.request.form[subwidgetName] = file_

            # update form again (will save file_ on draft)
            form.update()

            for subwidget in widget.widgets:
                if subwidget.name == subwidgetName:
                    response = {"filename" : subwidget.filename,
                                "counter"  : counter,
                                "html"     : subwidget.render(),
                                }
                    response.update(SUCCESS)
                    return json.dumps(response)
        except TypeError:
            pass

        return json.dumps(ERROR)
