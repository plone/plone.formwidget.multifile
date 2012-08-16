(function($) {
    function init_multifile() {
	$('.multi-file-picker input').live('change',
        function(e) {
	  if (! $(this).is(":visible") ) { return false };

	  name = "";
	  if (this.files != undefined) {
	    filenames = [];
	    $.each(this.files, function(i,v) {
	      filenames.push(v.name);
	      });
	      name = filenames.join(", ");
	    }
	  else {
	    name = $(this).val().replace(/^.*[\\\/]/, '');
	  }
	     
	  new_picker = $(this).parent().clone(true);
	  new_picker.find('input').val("");
          new_picker.insertBefore($(this).parent());
	  $(this).siblings('.multi-file-placeholder').prepend(name).show();
	  $(this).hide();
        });
      $('.multi-file-picker .multi-file-remove-file').click(
        function(e) {
	  if (jQuery('.multi-file-picker').length > 1) {
	    jQuery(this).parents('.multi-file-picker:first').remove()
	  };
	  return false
        });
    }

    init_multifile();
    
})(jQuery); 
