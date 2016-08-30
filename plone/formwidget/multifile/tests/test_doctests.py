import doctest
import unittest
import zope.app.testing.placelesssetup


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../README.txt',
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
        ))
