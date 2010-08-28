function multifile_uploadify_response(event, ID, fileObj, response, data) {
  console.info(event, ID, fileObj, response, data);
  var fieldname = jq(event.target).attr('ref');
  var html = '<span>' + fileObj.name + '</span> &mdash; ' +
    '<span class="discreet">' + Math.round(fileObj.size / 1024) +
    ' KB</span><input type="hidden" name="' + fieldname +
    ':list" value="new:' + response + '" />';
  jq(event.target).siblings('.multi-file-files:first').each(
    function() {
      jq(this).append(jq(document.createElement('li')).html(html));
    });
}
