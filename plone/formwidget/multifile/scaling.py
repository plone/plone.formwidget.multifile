from Acquisition import aq_inner
from zope.interface import implements
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces import IPublishTraverse, NotFound
from plone.scale.storage import AnnotationStorage

from plone.namedfile import scaling
from plone.formwidget.multifile.interfaces import IImageScaleTraversable
from zope.interface import alsoProvides
from Acquisition import ImplicitAcquisitionWrapper

class ImageScale(scaling.ImageScale):
    """ view used for rendering image scales """

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, context, request, **info):
        self.context = context
        self.request = request
        self.__dict__.update(**info)

        pfm = getattr(context, 'plone_formwidget_multifile', None)
        if pfm is not None:
            url = pfm['url']
        else:
            url = self.context.absolute_url()
        extension = self.data.contentType.split('/')[-1].lower()
        if 'uid' in info:
            name = info['uid']
        else:
            name = info['fieldname']
        self.__name__ = '%s.%s' % (name, extension)
        self.url = '%s/@@images/%s' % (url, self.__name__)

# XXX:  Remove; just put here for testing...
from Acquisition import aq_base
from cgi import escape
from logging import exception
from Acquisition import aq_base
from AccessControl.ZopeGuards import guarded_getattr
from ZODB.POSException import ConflictError
from zope.component import queryUtility
from zope.interface import implements
from zope.traversing.interfaces import ITraversable, TraversalError
from zope.publisher.interfaces import IPublishTraverse, NotFound
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.scale.storage import AnnotationStorage
from plone.scale.scale import scaleImage
from Products.Five import BrowserView

from plone.namedfile.interfaces import IAvailableSizes
from plone.namedfile.utils import set_headers, stream_data

from zope.component import queryMultiAdapter


class ImageScaling(scaling.ImageScaling):
    """ view used for generating (and storing) image scales """
    implements(ITraversable, IPublishTraverse)

    # XXX:  Is this okay or am I monkey patching here by accident; just want
    #       to make sure extended class has access to ImageScale above only
    #       for this module; not original...  Trace and check!
    scaling.ImageScale = ImageScale

    # XXX: Remove; just for testing
    def EDDIE(self):
        pass

    def __init__(self, context, request):
        super(scaling.ImageScaling, self).__init__(context, request)
        pfm = getattr(self.context, 'plone_formwidget_multifile', None)
        if pfm is not None:
            self.context = ImplicitAcquisitionWrapper(pfm['original_context'], pfm['dict_context'])

    def publishTraverse(self, request, name):
        """ used for traversal via publisher, i.e. when using as a url

        Normally a widget is not used to traverse an object; but multi
        widget is a specail case.  We need to wrap context here so url can
        be found etc

        EXAMPLE:
        http://127.0.0.1:50080/content/view/++widget++field_name/filename.ext/@@images/filename.ext
        http://127.0.0.1:50080/content/view/++widget++field_name/filename.ext/@@images/filename.ext/thumb
        """
        stack = request.get('TraversalRequestNameStack')
        image = None
        if stack:
            # field and scale name were given...
            scale = stack.pop()
            image = self.scale(name, scale)             # this is aq-wrapped
        elif '-' in name and getattr(self.context, name) is None:
            # we got a uid...
            if '.' in name:
                name, ext = name.rsplit('.', 1)
            storage = AnnotationStorage(self.context)
            info = storage.get(name)
            if info is not None:
                scale_view = ImageScale(self.context, self.request, **info)
                return scale_view.__of__(self.context)
        else:
            # otherwise `name` must refer to a field...
            # Context must be the container, but we need to be able to getattr on context.context somehow
            value = getattr(self.context, name)

            scale_view = ImageScale(self.context, self.request, data=value, fieldname=name)
            return scale_view.__of__(self.context)
        if image is not None:
            return image
        raise NotFound(self, name, self.request)

    def scale(self, fieldname=None, scale=None, height=None, width=None, **parameters):
        # TODO:  Look into other (better) ways to accomplish a custom create factory
        """This is more of a hack to allow object types that extend NamedImage
        to be able to provide their own factory since we are extending the
        plone.namedfile.scaling.ImageScaling and can't direclty extend a custom
        field.  The custom field must mark IImageScaleTraversable for this to
        work (see collective.formwidget.watermark.interfaces/widget/scaling
        for examples.

        Ideally plone.namedfile.scaling should provide a named utility or
        something for the create method to make this cleaner.
        """
        if fieldname is None:
            fieldname = IPrimaryFieldInfo(self.context).fieldname
        if scale is not None:
            available = self.getAvailableSizes(fieldname)
            if not scale in available:
                return None
            width, height = available[scale]
        if height is None and width is None:
            value = getattr(self.context, fieldname)
            info = dict(data=value, fieldname=fieldname)
        else:
            storage = AnnotationStorage(self.context, self.modified)
            factory = self.create
            # Here is where we allow a custom factory...
            orig_value = getattr(self.context, fieldname)
            scaling_adapter = queryMultiAdapter((self.context, self.request), name='images')
            if scaling_adapter is not None:
                scaling_adapter.context = self.context
                factory = scaling_adapter.create

            info = storage.scale(factory=factory,
                fieldname=fieldname, height=height, width=width, **parameters)
        if info is not None:
            scale_view = ImageScale(self.context, self.request, **info)
            return scale_view.__of__(self.context)