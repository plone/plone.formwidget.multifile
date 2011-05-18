/**
 * http://github.com/valums/file-uploader
 *
 * Patch the following function in the fileuploader.js file to enable
 * script to properly work with multifile's json response embed within
 * a <script> tag (otherwise it can not parse the html returned in the
 * response.
 *
 * I have created a bug tracker report on valums site to request patch be
 * included in future versions.
 *
 */

    /**
     * Returns json object received by iframe from server.
     */
    _getIframeContentJSON: function(iframe){
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
    },
