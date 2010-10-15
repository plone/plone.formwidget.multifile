/** *
 * JQuery Helpers for Plone Quick Upload
 *   
 */    

var MultiFileUpload = {};
    
/*
MultiFileUpload.addUploadFields = function(uploader, domelement, file, id, fillTitles) {
    if (fillTitles)  {
        var labelfiletitle = jQuery('#uploadify_label_file_title').val();
        var blocFile = uploader._getItemByFileId(id);
        if (typeof id == 'string') id = parseInt(id.replace('qq-upload-handler-iframe',''));
        jQuery('.qq-upload-cancel', blocFile).after('\
                  <div class="uploadField">\
                      <label>' + labelfiletitle + '&nbsp;:&nbsp;</label> \
                      <input type="text" \
                             class="file_title_field" \
                             id="title_' + id + '" \
                             name="title" \
                             value="" />\
                  </div>\
                   ')
    }
    MultiFileUpload.showButtons(uploader, domelement);
}

MultiFileUpload.showButtons = function(uploader, domelement) {
    var handler = uploader._handler;
    if (handler._files.length) {
        jQuery('.uploadifybuttons', jQuery(domelement).parent()).show();
        return 'ok';
    }
    return false;
}

MultiFileUpload.sendDataAndUpload = function(uploader, domelement, typeupload) {
    var handler = uploader._handler;
    var files = handler._files;
    var missing = 0;
    for ( var id = 0; id < files.length; id++ ) {
        if (files[id]) {
            var fileContainer = jQuery('.qq-upload-list li', domelement)[id-missing];
            var file_title = '';
            if (fillTitles)  {
                file_title = jQuery('.file_title_field', fileContainer).val();
            }
            uploader._queueUpload(id, {'title': file_title, 'typeupload' : typeupload});
        }
        // if file is null for any reason jq block is no more here
        else missing++;
    }
}    
*/

MultiFileUpload.onAllUploadsComplete = function(){
    Browser.onUploadComplete();
}

/*
MultiFileUpload.clearQueue = function(uploader, domelement) {
    var handler = uploader._handler;
    var files = handler._files;
    for ( var id = 0; id < files.length; id++ ) {
        if (files[id]) {
            handler.cancel(id);
        }
        jQuery('.qq-upload-list li', domelement).remove();
        handler._files = [];
        if (typeof handler._inputs != 'undefined') handler._inputs = {};
    }    
}    
*/

MultiFileUpload.onUploadComplete = function(uploader, domelement, id, fileName, responseJSON) {
    var uploadList = jQuery('.qq-upload-list', domelement);
    if (responseJSON.success) {        
        window.setTimeout( function() {
            jQuery(uploader._getItemByFileId(id)).remove();
            // after the last upload, if no errors, reload the page
            var newlist = jQuery('li', uploadList);
            if (! newlist.length) window.setTimeout( MultiFileUpload.onAllUploadsComplete, 5);       
        }, 50);
    }
    
}

/*
function multifile_uploadify_response(event, ID, fileObj, response, data) {
  var fieldname = jq(event.target).attr('ref');
  var html = '<span>' + fileObj.name + '</span> &mdash; ' +
    '<span class="discreet">' + Math.round(fileObj.size / 1024) +
    ' KB &mdash; <a href="" class="multi-file-remove-file">remove</a>'
    + '</span><input type="hidden" name="' + fieldname +
    ':list" value="new:' + response + '" />';
  jq(event.target).siblings('.multi-file-files:first').each(
    function() {
      jq(this).append(jq(document.createElement('li')).html(html).
                      attr('class', 'multi-file-file'));
    });
}
*/

jq(
  function($) {
    $('.multi-file-remove-file').live('click',
      function(e) {
        alert('removing file');
        e.preventDefault();
        $(this).parents('.multi-file-file:first').remove();
      });
  }
);
