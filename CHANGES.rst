Changelog
=========

2.1 (unreleased)
----------------

- Python 3 compatibility
  [agitator]


2.0 (2016-08-31)
----------------

Incompatibilities:

- Instead of ``zope.app.file.interfaces.IFile`` use ``plone.namedfile.interfaces.IFile``.
  [thet]

- Fix missing Javascript call that breaks the widget
  [laulaz]

- Add French and Dutch translations
  [laulaz]

- Add travis & coveralls hook
  [tomgross]

- Plone 5.0 support
  [tomgross]

1.1 (2014-03-24)
----------------

- Added Spanish (es) and Basque (eu) translation
  [erral]

- Added PO file generation script
  [erral]

- Use similar pattern to plone.formwidget.namedfile for the data converter.
  [gaudenz]

- Add @@download BrowserView for file downloads
  [gaudenz]

- Base widget on z3c.form.widget.Widget instead of MultiWidget. The MultiWidget
  is for combining different widgets into one.
  [gaudenz]

- Don't call update from render. This is not necessary and can lead to unwanted
  side-effects.
  [gaudenz]

- Extract FileUpload objects instead of relying on Widget.extract to do the mostly
  right thing.
  [gaudenz]

- Base files shown by the widget on the actual fields content instead of a mixture
  of request data and converter magic.
  [gaudenz]

- Improve input template and JavaScript

  - Append file inputs below the file list to not overwrite existing files
  - Remove Hacks for IE7. They no longer work with recent jQuery versions and
    IE7 is mostly irrelevant by now.
  - Use standard file input widget instead of custom add link. This is what people
    expect and as a bonus is already translated. If people want custom links they can
    still override the template.

  - Integrate not yet uploaded files into the same file list.
    [gaudenz]

- Add german translation
  [gaudenz]

1.0a6 (2013-01-22)
------------------

* Fixed bug: "add files" link was opening multiple file dialogs.
  [rafaelbco]
* Fixed bug: bugfix of the previous release didn't work on IE 7.
  [rafaelbco]

1.0a5 (2013-01-21)
------------------

* Fixed bug on IE: When an file-input is opened via a scripted, forced click()
  event, IE won't let you submit the form.
  [rafaelbco]
* Updated pt_BR translation.
  [rafaelbco]

1.0a4 (2012-12-20)
------------------

* Updated URL on setup.py
  [rafaelbco]

1.0a3 (2012-12-20)
------------------

* Changed the UI so now there's a link to "add files" instead of an standard
  input[type=file] HTML element (which still exists, but is hidden). Users were
  complaining that the old UI was confusing since the textbox of the
  input[type=file] element was always empty.
  [rafaelbco]

1.0a2 (2012-12-20)
------------------

* Removed integration with jQuery plugin. Instead we use HTML and javascript,
  and when applicable, the "multiple" extension from HTML5 which lets a
  user upload multiple files at once.
  [tmog]

* Fix minor bugs on the new non-flash implementation.
  [rafaelbco]

* Removed dependency on plone.app.drafts.
  [rafaelbco]

1.0a1 (2011-09-13)
------------------

* Initial release
