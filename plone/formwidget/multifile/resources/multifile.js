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
        var file_input = e.target,
            $file_input = $(file_input),
            $widget = $file_input.closest('.multi-file'),
            name = '',
            filenames = [],
            $new_file_input,
            $placeholder,
            $upload;

        if (file_input.files !== undefined) {
            $.each(file_input.files, function(i, v) {
                filenames.push(v.name);
            });
            name = filenames.join(', ');
        }
        else {
            name = $file_input.val().replace(/^.*[\\\/]/, '');
        }

        // copy the placeholder and fill in the new values
        $placeholder = $widget.find('#multi-file-placeholder');
        $upload = $placeholder.clone(true);
        $upload.removeAttr('id');
        $upload.find('.filename').text(name);
        $placeholder.before($upload);
        $upload.show();

        // clone a new file input and copy the filled one into the list
        $new_file_input = $file_input.clone(true);
        $new_file_input.val('');
        $file_input.hide();
        $file_input.after($new_file_input);
        $upload.find('.filename').before($file_input);
    }

    // Bind the event handler of the change event of the input[type=file]'s.
    $('.multi-file-picker input').change(changeHandler);

    // Bind the event handler for the "remove file" link.
    $('.multi-file .multi-file-remove-file').click(function(e) {
        $(this).closest('.multi-file-file').remove();
        return false;
    });

});
