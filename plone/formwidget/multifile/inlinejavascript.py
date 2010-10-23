"""Contains the inline javascript Multifile widget requires for flash and
ajax uploads"""

MULTIFILE_INLINE_JS = """
    jQuery(document).ready(function() {
        jQuery('#%(name)s').multifile({
            'deleteURL'     : '%(deleteURL)s',
            'deleteMessage' : '%(deleteMessage)s'
        });
    });
"""

FLASH_UPLOAD_JS = """
    // TODO:
    // - create custom queue;
    // - notify user that file was not uploaded if it was a duplicate
    //   (just add to INFO bar;  create a routine to update info bar and use it)
    // - implement error messages
    // - onLeave overlay
    // - use thumbs for thumbs (@@image resize); overlay for larger images click

    jQuery(document).ready(function() {
        jQuery('#%(name)s').uploadify({
            'uploader'      : '++resource++plone.formwidget.multifile/uploadify.swf',
            'script'        : '%(actionURL)s',
            'checkScript'   : '%(checkScriptURL)s',
            'fileDataName'  : 'qqfile',
            'cancelImg'     : '++resource++plone.formwidget.multifile/cancel.png',
            'folder'        : '%(physicalPath)s',
            'auto'          : true,
            'multi'         : %(multi)s,
            'simUploadLimit': %(maxConnections)s,
            'sizeLimit'     : '%(sizeLimit)s',
            'fileDesc'      : '%(fileDescription)s',
            'fileExt'       : '%(fileExtensions)s',
            'buttonText'    : '%(buttonText)s',
            'scriptAccess'  : 'sameDomain',
            'hideButton'    : false,
            'scriptData'    : {'ticket' : '%(ticket)s', 'typeupload' : '%(typeupload)s'},
            'onComplete'    : function (event, queueID, fileObj, responseJSON, data) {
                try{
                    response = jQuery.parseJSON(responseJSON);
                } catch(err){
                    return false;
                }

                // TODO:  Do something to indicate the error
                if( response.error ) { return false; }

                // unescape html before appending it
                jQuery('#%(fileListID)s').append(jQuery("<div />").html(response.html).text());
            }
        });

        // Override uploadify's default onCheck bindings
        jQuery('#%(name)s').multifileOverrideFlashOnCheck();

    });
"""

XHR_UPLOAD_JS = """

    createUploader_%(ID)s= function(){
        xhr_%(ID)s = new qq.FileUploader({
            element: jQuery('#%(name)s')[0],
            debug : true,
            action: '%(actionURL)s',
            //button:
            multiple: %(multi)s,
            maxConnections: %(maxConnections)s,
            allowedExtensions: %(fileExtensionsList)s,
            sizeLimit: %(xhrSizeLimit)s,
            cancelImg: '++resource++plone.formwidget.multifile/cancel.png',
            onSubmit: function(id, fileName){
                var success = true;
                jQuery.ajax({
                    url: '%(checkScriptURL)s',
                    data: {filename : fileName},
                    dataType: 'json',
                    type: 'POST',
                    async: false,
                    success: function(data) {
                        if (data.filename) {
                            var uploader = xhr_%(ID)s;
                            uploader._addToList(id, fileName);
                            jQuery(uploader._getItemByFileId(id)).addClass('qq-upload-fail');

                            var message = uploader._options.messages['serverErrorAlreadyExists'];
                            function r(name, replacement){ message = message.replace(name, replacement); }
                            r('{file}', uploader._formatFileName(fileName));
                            jQuery(uploader._getItemByFileId(id)).find('.qq-upload-failed-text').html(message);
                            success = false;
                        }
                    }
                });
                return success;
            },
            //onProgress: function(id, fileName, loaded, total){},
            //onCancel: function(id, fileName){},
            onComplete: function (ID, filename, responseJSON) {
                var uploader = xhr_%(ID)s;
                if (responseJSON.error) {
                    // TODO move to multifile.js
                    var message = uploader._options.messages[responseJSON.error];
                    function r(name, replacement){ message = message.replace(name, replacement); }
                    r('{file}', uploader._formatFileName(filename));
                    r('{extensions}', uploader._options.allowedExtensions.join(', '));
                    r('{sizeLimit}', uploader._formatSize(uploader._options.sizeLimit));
                    r('{minSizeLimit}', uploader._formatSize(uploader._options.minSizeLimit));
                    jQuery(uploader._getItemByFileId(ID)).find('.qq-upload-failed-text').html(message);
                    jQuery(uploader._getItemByFileId(ID)).prepend('<a class="qq-error-cancel" href="#">&nbsp;</a>');
                }
                // unescape html before appending it
                jQuery('#%(fileListID)s').append(jQuery("<div />").html(responseJSON.html).text());
                jQuery(uploader._getItemByFileId(ID)).remove();
            },
            messages: {
                serverError:              "%(errorServer)s",
                draftError:               "%(errorDraft)s",
                serverErrorAlreadyExists: "%(errorAlreadyExists)s {file}",
                serverErrorZODBConflict:  "%(errorZodbConflict)s {file}, %(errorTryAgain)s",
                serverErrorNoPermission:  "%(errorNoPermission)s",
                typeError:                "%(errorBadExt)s {file}. %(errorOnlyAllowed)s {extensions}.",
                sizeError:                "%(errorFileLarge)s {file}, %(errorMaxSizeIs)s {sizeLimit}.",
                emptyError:               "%(errorEmptyFile)s {file}, %(errorTryAgainWo)s",
                minSizeError:             "{file} is too small, minimum file size is {minSizeLimit}.",
                onLeave:                  "The files are being uploaded, if you leave now the upload will be cancelled.",
            },
            //listElement: null,
            template: '<div class="qq-uploader">' +
                      '<div class="qq-upload-drop-area"><span>%(dragAndDropText)s</span></div>' +
                      '<div class="qq-upload-button">%(buttonText)s</div>' +
                      '<ul class="qq-upload-list"></ul>' +
                      '</div>',
            fileTemplate: '<li>' +
                    '<a class="qq-upload-cancel" href="#">&nbsp;</a>' +
                    '<div class="qq-upload-infos"><span class="qq-upload-file"></span>' +
                    '<span class="qq-upload-spinner"></span>' +
                    '<span class="qq-upload-size"></span></div>' +
                    '<div class="qq-upload-failed-text">%(msgFailed)s</div>' +
                '</li>',
            showMessage: function(message){
                //alert(message);
            },
        });
    }
    jQuery(document).ready(createUploader_%(ID)s);

    jQuery(document).ready(function() {
        // Attach an qq-error-cancel click binding event
        jQuery('#%(name)s').multifileFileUploaderBindErrorCancel();
    });
"""

NADA = """
List of vars used; for debug so we can remove unsed vars
Ledgend:  B=Both, F=Flash Only, A=Ajax Only, N=None, M=Multifile
            B actionURL
            M deleteURL
            F checkScriptURL
            N portalURL
            N contextURL
            F physicalPath
            F typeupload                 Not really used though
            N fieldName
            B ID
            B fileListID
            B name
            F ticket
            B multi
            F sizeLimit
            A xhrSizeLimit
            B maxConnections
            B buttonText
            M deleteMessage
            A dragAndDropText
            F fileExtensions
            A fileExtensionsList
            F fileDescription
            N msgAllSuccess
            N msgSomeSuccess
            N msgSomeErrors
            A msgFailed
            A errorTryAgainWo
            A errorTryAgain
            A errorEmptyFile
            A errorFileLarge
            A errorMaxSizeIs
            A errorBadExt
            A errorOnlyAllowed
            A errorNoPermission
            A errorAlreadyExists
            A errorZodbConflict
            A errorServer
            A errorDraft
"""