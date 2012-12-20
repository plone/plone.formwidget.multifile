jQuery(document).ready(function($) {

    // When multiple widgets are the same form then this JS is included multiple times.
    // We need the following code to make sure this event handler will execute only once.
    if (window.__plone_formwidget_multifile_readyExecuted) {
        return;
    }
    window.__plone_formwidget_multifile_readyExecuted = true;

    /* Event handler of the change event of the input[type=file]'s.
     *
     * When a file is selected then a new entry on the list of files to be uploaded is created
     * by cloning the parent element and unhiding the filename part.
     */
    function changeHandler(e) {
        var element = e.target,
            $element = $(element),
            name = '';

        if (element.files !== undefined) {
            filenames = [];
            $.each(element.files, function(i, v) {
                filenames.push(v.name);
            });
            name = filenames.join(', ');
        }
        else {
            name = $element.val().replace(/^.*[\\\/]/, '');
        }

        new_picker = $element.parent().clone(true);
        new_picker.find('input').val('');
        new_picker.insertBefore($element.parent());
        $element.siblings('.multi-file-placeholder').prepend(name).show();
    }

    /* Attach a handler to the change event of all file inputs specified by the given selector.
     *
     * This function makes sure behavior will be consistent between IE and other browsers.
     * See: http://stackoverflow.com/a/2876677
     */
    function bindFileInputChangeEvent(selector, handler) {
        if ($.browser.msie) {
            $(selector).click(function(e) {
                setTimeout(
                    function() {
                        if ($(e.target).val().length > 0) {
                            handler(e);
                        }
                    },
                    0
                );
            });
        } else {
            $(selector).change(handler);
        }
    }

    // Bind the event handler of the change event of the input[type=file]'s.
    bindFileInputChangeEvent('.multi-file-picker input', changeHandler);

    // Bind the event handler for the "remove file" link.
    $('.multi-file-picker .multi-file-remove-file').click(function(e) {
        if ($('.multi-file-picker').length > 1) {
            $(this).parents('.multi-file-picker:first').remove();
        }

        return false;
    });

    // Bind the event handler for the "add files" link.
    $('.multi-file-add-files').click(function() {
        $(this).parent().find('input[type=file]:first').click();
        return false;
    });

    // Hide the input[type=file]'s
    $('.multi-file-picker input[type=file]').hide();
});
