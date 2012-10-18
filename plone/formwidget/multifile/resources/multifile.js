jQuery(document).ready(function($) {

    var changeHandler = function(e) {
        var element = e.target;
        var $element = $(element);

        if (! $element.is(":visible") ) {
            return false
        };

        name = '';
        if (element.files != undefined) {
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
        $element.hide();
    };

    /* Attach a handler to the change event of all file inputs specified by the given selector.
     *
     * This function makes sure behavior will be consistent between IE and other browsers.
     * See: http://stackoverflow.com/a/2876677
     */
    var bindFileInputChangeEvent = function(selector, handler) {
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

    bindFileInputChangeEvent('.multi-file-picker input', changeHandler);

    $('.multi-file-picker .multi-file-remove-file').click(function(e) {
        if ($('.multi-file-picker').length > 1) {
            $(this).parents('.multi-file-picker:first').remove();
        }

        return false;
    });
});
