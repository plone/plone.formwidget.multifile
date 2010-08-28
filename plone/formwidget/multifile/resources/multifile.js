function multifile_uploadify_response(event, ID, fileObj, response, data) {
  console.info(event, ID, fileObj, response, data);
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

jq(
  function($) {
    $('.multi-file-remove-file').live('click',
      function(e) {
        e.preventDefault();
        $(this).parents('.multi-file-file:first').remove();
      });
  }
);