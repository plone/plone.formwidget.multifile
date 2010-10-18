"""Contains the inline javascript MultiFile widget requires for flash and
ajax uploads"""

DELETE = """
    jQuery(document).ready(function() {
        bindDelete = function(scope) {
          $('.multifiledelete', scope).click(function(event) {
            event.preventDefault();

            // TODO:  Add a spinner
            var delete_anchor = $(this).html('%(delete_message)s');

            // Ajax request
            $.ajax({
                type     : "POST",
                url      : "%(delete_url)s",
                data     : {filename: $(this).closest('li.multi-file-file').find('a .filename').html()},
                dataType : "json",
                success  : function(responseJSON){
                    if(responseJSON.success) {
                        $(delete_anchor).closest('li.multi-file-file').remove();
                        $('#content').before($(document.createElement('dl')).html(responseJSON.html).attr('class', 'portalMessage info'));
                    } else {
                        $(delete_anchor).html('Error');
                        $('#content').before($(document.createElement('dl')).html(responseJSON.html).attr('class', 'portalMessage error'));
                    }
                }
            });
          });
        }
        bindDelete(this);
    });
"""

FLASH_UPLOAD_JS = """
    jQuery(document).ready(function() {
        jQuery('#%(name)s').uploadify({
            'uploader'      : '++resource++plone.formwidget.multifile/uploadify.swf',
            'script'        : '%(action_url)s',
            'fileDataName'  : 'qqfile',
            'cancelImg'     : '++resource++plone.formwidget.multifile/cancel.png',
            'folder'        : '%(physical_path)s',
            'auto'          : true,
            'multi'         : %(multi)s,
            'simUploadLimit': %(sim_upload_limit)s,
            'sizeLimit'     : '%(size_limit)s',
            'fileDesc'      : '%(file_description)s',
            'fileExt'       : '%(file_extensions)s',
            'buttonText'    : '%(button_text)s',
            'scriptAccess'  : 'sameDomain',
            'hideButton'    : false,
            'scriptData'    : {'ticket' : '%(ticket)s', 'typeupload' : '%(typeupload)s'},
            'onComplete'    : function (event, queueID, fileObj, responseJSON, data) {
                try{
                    response = jQuery.parseJSON( responseJSON );
                } catch(err){
                    return false;
                }

                // TODO:  Do something to indicate the error
                if( response.error ) { return false; }

                var newLi = $(response.html);
                bindDelete(newLi);
                jQuery('#%(file_list_id)s').append(newLi);
            },
        });
    });
"""

XHR_UPLOAD_JS = """
    createUploader_%(id)s= function(){
        xhr_%(id)s = new qq.FileUploader({
            element: jQuery('#%(name)s')[0],
            action: '%(action_url)s',
            autoUpload: true,
            multi: %(multi)s,
            cancelImg: '++resource++plone.formwidget.multifile/cancel.png',

            onComplete: function (id, filename, responseJSON) {
                var newLi = $(responseJSON.html);
                bindDelete(newLi);
                jQuery('#%(file_list_id)s').append(newLi);

                var uploader = xhr_%(id)s;
                MultiFileUpload.onUploadComplete(uploader, uploader._element, id, filename, responseJSON);
            },

            allowedExtensions: %(file_extensions_list)s,
            sizeLimit: %(xhr_size_limit)s,
            simUploadLimit: %(sim_upload_limit)s,
            //template: '<div class="qq-uploader">' +
            //          '<div class="qq-upload-drop-area"><span>%(draganddrop_text)s</span></div>' +
            //          '<div class="qq-upload-button">%(button_text)s</div>' +
            //          '<ul class="qq-upload-list"></ul>' +
            //          '</div>',
            fileTemplate: '<li>' +
                    '<a class="qq-upload-cancel" href="#">&nbsp;</a>' +
                    '<div class="qq-upload-infos"><span class="qq-upload-file"></span>' +
                    '<span class="qq-upload-spinner"></span>' +
                    '<span class="qq-upload-failed-text">%(msg_failed)s</span></div>' +
                    '<div class="qq-upload-size"></div>' +
                '</li>',
            messages: {
                serverError: "%(error_server)s",
                draftError: "%(error_draft)s",
                serverErrorAlreadyExists: "%(error_already_exists)s {file}",
                serverErrorZODBConflict: "%(error_zodb_conflict)s {file}, %(error_try_again)s",
                serverErrorNoPermission: "%(error_no_permission)s",
                typeError: "%(error_bad_ext)s {file}. %(error_onlyallowed)s {extensions}.",
                sizeError: "%(error_file_large)s {file}, %(error_maxsize_is)s {sizeLimit}.",
                emptyError: "%(error_empty_file)s {file}, %(error_try_again_wo)s"
            }
        });
    }
    jQuery(document).ready(createUploader_%(id)s);
"""
