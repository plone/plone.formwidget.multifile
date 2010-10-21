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
    jQuery(document).ready(function() {
        jQuery('#%(name)s').uploadify({
            'uploader'      : '++resource++plone.formwidget.multifile/uploadify.swf',
            'script'        : '%(actionURL)s',
            //'checkScript'   : '%(checkScriptURL)s',
            'fileDataName'  : 'qqfile',
            'cancelImg'     : '++resource++plone.formwidget.multifile/cancel.png',
            'folder'        : '%(physicalPath)s',
            'auto'          : true,
            'multi'         : %(multi)s,
            'simUploadLimit': %(simUploadLimit)s,
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

                jQuery('#%(fileListID)s').append(jQuery(response.html));
            }
        });
    });
"""

XHR_UPLOAD_JS = """
    createUploader_%(ID)s= function(){
        xhr_%(ID)s = new qq.FileUploader({
            element: jQuery('#%(name)s')[0],
            action: '%(actionURL)s',
            autoUpload: true,
            multi: %(multi)s,
            cancelImg: '++resource++plone.formwidget.multifile/cancel.png',

            onComplete: function (ID, filename, responseJSON) {
                jQuery('#%(fileListID)s').append(jQuery(responseJSON.html));

                var uploader = xhr_%(ID)s;
                MultiFileUpload.onUploadComplete(uploader, uploader._element, ID, filename, responseJSON);
            },

            allowedExtensions: %(fileExtensionsList)s,
            sizeLimit: %(xhrSizeLimit)s,
            simUploadLimit: %(simUploadLimit)s,
            //template: '<div class="qq-uploader">' +
            //          '<div class="qq-upload-drop-area"><span>%(dragAndDropText)s</span></div>' +
            //          '<div class="qq-upload-button">%(buttonText)s</div>' +
            //          '<ul class="qq-upload-list"></ul>' +
            //          '</div>',
            fileTemplate: '<li>' +
                    '<a class="qq-upload-cancel" href="#">&nbsp;</a>' +
                    '<div class="qq-upload-infos"><span class="qq-upload-file"></span>' +
                    '<span class="qq-upload-spinner"></span>' +
                    '<span class="qq-upload-failed-text">%(msgFailed)s</span></div>' +
                    '<div class="qq-upload-size"></div>' +
                '</li>',
            messages: {
                serverError: "%(errorServer)s",
                draftError: "%(errorDraft)s",
                serverErrorAlreadyExists: "%(errorAlreadyExists)s {file}",
                serverErrorZODBConflict: "%(errorZodbConflict)s {file}, %(errorTryAgain)s",
                serverErrorNoPermission: "%(errorNoPermission)s",
                typeError: "%(errorBadExt)s {file}. %(errorOnlyAllowed)s {extensions}.",
                sizeError: "%(errorFileLarge)s {file}, %(errorMaxSizeIs)s {sizeLimit}.",
                emptyError: "%(errorEmptyFile)s {file}, %(errorTryAgainWo)s"
            }
        });
    }
    jQuery(document).ready(createUploader_%(ID)s);
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
            B simUploadLimit
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