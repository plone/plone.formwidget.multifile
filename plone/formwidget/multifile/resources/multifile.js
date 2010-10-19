/** *
 * JQuery Helpers for MultiFile Upload
 *
 */

var MultiFileUpload = MultiFileUpload || {};

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

if(jQuery)(
    function(jQuery){
        jQuery.extend(jQuery.fn,{
            multifile:function(options) {
                jQuery(this).each(function(){
                    multisettings = jQuery.extend({
                    deleteURL     : '', // url to delete view
                    deleteMessage : 'Deleting... Please Wait.' // message to display while deleting
                }, options);
                // Do initial bind here
                jQuery(this).multifileBindEvents();
            });
        },
        multifileBindEvents:function() {
            jQuery(this).each(function() {
                jQuery(this).multifileBindHover();
                jQuery(this).multifileBindDelete();
            });
        },
        multifileBindHover:function() {
            jQuery(this).each(function() {
                jQuery(".multifile-hover").live('mouseover mouseout', function(event) {
                    if (event.type == 'mouseover') {
                        jQuery(this).css({ borderStyle:"inset", cursor:"wait" });
                        jQuery(this).closest('li.multifile-file').find('.multifile-info').show();
                    } else {
                        jQuery(this).closest('li.multifile-file').find('.multifile-info').hide();
                    }
                });
            });
        },
        multifileBindDelete:function() {
            jQuery(this).each(function() {
                jQuery(".multifile-delete").live('click', function(event) {
                    event.preventDefault();

                    // TODO:  Add a spinner
                    var delete_anchor = jq(this).html(multisettings.deleteMessage);

                    // Ajax request
                    jq.ajax({
                        type     : "POST",
                        url      : multisettings.deleteURL,
                        data     : {filename: jq(this).closest('li.multifile-file').find('a .filename').html()},
                        dataType : "json",
                        success  : function(responseJSON){
                            if(responseJSON.success) {
                                jq(delete_anchor).closest('li.multifile-file').remove();
                                jq('#content').before(jq(document.createElement('dl')).html(responseJSON.html).attr('class', 'portalMessage info'));
                            } else {
                                jq(delete_anchor).html('Error');
                                jq('#content').before(jq(document.createElement('dl')).html(responseJSON.html).attr('class', 'portalMessage error'));
                            }
                        }
                    });
                });
            });
        }
    })
})(jQuery);
