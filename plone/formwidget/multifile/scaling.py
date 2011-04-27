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

class ImageScaling(scaling.ImageScaling):
    """ view used for generating (and storing) image scales """
    implements(ITraversable, IPublishTraverse)

    scaling.ImageScale = ImageScale

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
