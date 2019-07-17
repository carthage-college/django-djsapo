/* spinner: instantiate */
var opts = {
  lines: 13, // The number of lines to draw
  length: 20, // The length of each line
  width: 10, // The line thickness
  radius: 30, // The radius of the inner circle
  corners: 1, // Corner roundness (0..1)
  rotate: 0, // The rotation offset
  direction: 1, // 1: clockwise, -1: counterclockwise
  color: '#000', // #rgb or #rrggbb or array of colors
  speed: 1, // Rounds per second
  trail: 60, // Afterglow percentage
  shadow: false, // Whether to render a shadow
  hwaccel: false, // Whether to use hardware acceleration
  className: 'search-results', // The CSS class to assign to spinner
  zIndex: 2e9, // The z-index (defaults to 2000000000)
  top: '50px', // Top position relative to parent in px
  left: 'auto' // Left position relative to parent in px
};
var target = document.getElementById("alert-container");
var spinner = new Spinner(opts).spin(target);
spinner.stop(target);

/**
* simple function to show/hide an element based on the value
* of another dom object
**/
function toggle(dis, val, dom) {
  if (dis == val) {
    $(dom).show();
  } else {
    $(dom).hide();
  }
}

$(function() {
  /* remove team member */
  $('.remove-member').on('click', function(e){
    e.preventDefault();
    var $dis = $(this);
    var $url = $dis.attr("data-url");
    var $id = $dis.attr("data-cid");
    var $em = $dis.attr("data-email");
    var $ln = $dis.attr("data-last_name");
    var $fn = $dis.attr("data-first_name");
    var $html = $dis.html();
    console.log('id = ' + $id);
    $dis.html('<i class="fa fa-refresh fa-spin"></i>');
    $.ajax({
      type: "POST",
      url: $url,
      data: {"cid":$id,"email":$em,"last_name":$ln,"first_name":$fn},
      success: function(data) {
        $dis.closest('li').remove();
        $.growlUI("Team member", "Removed");
      }
    });
    return false;
  });
  /* datepicker */
  $("#id_interaction_date").datepicker({
    firstDay:1,
    changeFirstDay:false,
    dateFormat:'yy-mm-dd',
    buttonImage:'//www.carthage.edu/themes/shared/img/ico/calendar.gif',
    showOn:'both',
    buttonImageOnly:true
  });
  /* wysiwyg for textarea fields */
  $('textarea').trumbowyg({
    btns: [
      ['formatting'], ['strong', 'em', 'del'], ['link'],
      ['justifyLeft', 'justifyCenter', 'justifyRight', 'justifyFull'],
      ['unorderedList', 'orderedList'], ['horizontalRule'], ['viewHTML'],
    ],
    tagsToRemove: ['script', 'link'],
    removeformatPasted: true, semantic: true, autogrow: true, resetCss: true
  });
  /* fancy picker for select fields */
  $('select').selectpicker();
  /* override the submit event to handle some things */
  $('form#profile').submit(function(){
    // set the value of the student field to email address selected
    // via autocomplete
    $('#autoComplete').val($('#autoComplete').attr('data-email'));
    /* check textarea for just br tag */
    $("textarea").each(function(){
      if (this.value == "<br>") {
          this.value = "";
      }
    });
    // disable submit button after users clicks it
    $(this).children('input[type=submit]').attr('disabled', 'disabled');
  });
});
