import doctest
import unittest
import zope.app.testing.placelesssetup
import zope.testing.doctest


def test_suite():
    return unittest.TestSuite((
        zope.testing.doctest.DocFileSuite('../README.txt',
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        ))
