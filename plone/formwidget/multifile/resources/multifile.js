/** *
 * JQuery Helpers for MultiFile Upload
 *
 */

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
        },
        // Overrides the flash onClick function, since the onCheck function
        // does not contain the json response.  Submitted a bug report so when
        // uploadify is fixed, we can just implement a custon onSubmit function
        // instead of overriding
        multifileOverrideFlashOnCheck:function() {
            jQuery(this).each(function() {
                // Override default onCheck routine
                jQuery(this).unbind("uploadifyCheckExist");
                jQuery(this).bind("uploadifyCheckExist", {'action': settings.onCheck}, function(event, checkScript, fileQueueObj, folder, single) {
                    var postData = new Object();
                    postData = fileQueueObj;
                    //postData.folder = pagePath + folder;
                    if (single) {
                        for (var ID in fileQueueObj) {
                           var singleFileID = ID;
                        }
                    }
                    jQuery.post(checkScript, postData, function(data) {
                        for(var key in data) {
                            if (event.data.action(event, checkScript, fileQueueObj, folder, single) !== false) {
                                // Never allow duplicates, since server will reject them
                                // You would need to delete, then re-add to replace
                                document.getElementById(jQuery(event.target).attr('id') + 'Uploader').cancelFileUpload(key, true, true);
                            }
                        }
                        if (single) {
                            document.getElementById(jQuery(event.target).attr('id') + 'Uploader').startFileUpload(singleFileID, true);
                        } else {
                            document.getElementById(jQuery(event.target).attr('id') + 'Uploader').startFileUpload(null, true);
                        }
                    }, "json");
                });
            });
        },
        // Override qq.UploadHandlerForm.prototype._getIframeContentJSON
        // Allows json response to be embedded in <script> tags, otherwise
        // html response will fail unless html was previously encoded
        // Submitted this 'fix' as a request so this override may be able to be
        // removed in future
        multifileOverrideFileUploaderIframeJSONHandler:function() {
            qq.UploadHandlerForm.prototype._getIframeContentJSON = function(iframe){
                // iframe.contentWindow.document - for IE<7
                var doc = iframe.contentDocument ? iframe.contentDocument: iframe.contentWindow.document,
                    response;

                // XXX: Added for multifile, since returned HTML in response does not parse
                // correctly when added directly to an iframe body
                responseText = doc.getElementById('json-response') ? doc.getElementById('json-response').innerHTML : doc.body.innerHTML;
                try{
                    //response = eval("(" + doc.body.innerHTML + ")");
                    response = jQuery.parseJSON( responseText );
                } catch(err){
                    response = {};
                }

                return response;
            }
        }
    })
})(jQuery);
