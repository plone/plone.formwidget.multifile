/** *
 * JQuery Helpers for MultiFile Upload
 *
 */

var MultiFileUpload = {};


MultiFileUpload.onAllUploadsComplete = function(){
    Browser.onUploadComplete();
}


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

