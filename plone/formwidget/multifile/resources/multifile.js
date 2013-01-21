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
            $parent = $element.parent(),
            name = '',
            filenames = [],
            $newPicker,
            $newInput,
            $addFilesLink,
            idParts,
            index,
            newInputId;

        if (element.files !== undefined) {
            $.each(element.files, function(i, v) {
                filenames.push(v.name);
            });
            name = filenames.join(', ');
        }
        else {
            name = $element.val().replace(/^.*[\\\/]/, '');
        }

        // Calculate the new id for the new input[type=file].
        idParts = $element.attr('id').split(':');
        index = parseInt(idParts[1], 10) + 1;
        newInputId = idParts[0] + ':' + index;

        // If the "add new link" is a label then change the "for" attribute to point to the new
        // input[type=file].
        $addFilesLink = $parent.siblings('.multi-file-add-files');
        if ($addFilesLink.attr('for')) {
            $addFilesLink.attr('for', newInputId);
        }

        // Create new file picker.
        $newPicker = $parent.clone(true);
        $newInput = $newPicker.find('input');
        $newInput.val('');
        $newInput.attr('id', newInputId);
        $newPicker.insertBefore($parent);

        // Show the filename of the selected files.
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
        $(this).parents('.multi-file-picker:first').remove();
        return false;
    });

    // Problem: When an file-input is opened via a scripted, forced click() event, IE won't let
    // you submit the form.
    //
    // Solution: Replace <a>add new files</a> by a label for the input. If you click it, IE will
    // open the file dialog.
    //
    // Caveats:
    // - The input cannot be hidden with "display: none" for this to work. We have to hide the
    //   input in another way.
    // - On other browsers clicking on the label won't open the file dialog. So we add an event
    //   handler to do that.
    //
    // See: https://gist.github.com/4337047
    var $addFilesLink = $('.multi-file-add-files');
    if ($.browser.msie) {
        $addFilesLink.replaceWith(function() {
            var $this = $(this),
                $label;

            return $('<label/>', {
                'for': $this.siblings('.multi-file-picker').find('input[type=file]').attr('id'),
                'text': $this.text()
            });
        });
    } else {
        $addFilesLink.click(function() {
            var $this = $(this);
            $this.siblings('.multi-file-picker').find('input[type=file]').click();
            return false;
        });
    }

    // Hide the input[type=file]'s
    // We cannot simply use the hide() function because if we do IE won't open the file dialog when
    // the label of the input is clicked.
    var $input = $('.multi-file-picker input[type=file]');
    $input.css('width', '0');
    $input.css('height', '0');
});
