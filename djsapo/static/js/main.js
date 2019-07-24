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
  /* bootstrap tool tip */
  $('[data-toggle="tooltip"]').tooltip();
  /* print page */
  $('#print').click(function() {
    window.print();
    return false;
  });
  /* comments form */
  $("#commentsForm").submit(function(e){
    e.preventDefault();
    var $body = $("#id_body").val();
    $.ajax({
      type: "POST",
      url: $manager,
      data: {'aid':$aid,'body':$body,'mod':'comment','oid':0},
      cache: false,
      beforeSend: function(){
        $("#commentsModal").modal('hide');
      },
      success: function(data){
        $("#comments-list").append(data);
        //window.location.hash = "";
        //window.location.hash = "id_bounce";
        $('html, body').animate({scrollTop:$(document).height()}, 'slow');
        //location.hash = "id_bounce";
      },
      error: function(data){
        console.log(data);
        $.growlUI("Comment Form", "Error");
      }
    });
    return false;
  });
  $('#commentsModal').on('shown.bs.modal', function () {
    $('#id_body').focus();
  })
  /* function to update a name/value pair for models */
  $('.set-val').on('change', function() {
    var $dis = $(this);
    var $name = $dis.attr("name");
    var $value = $dis.val();
    $.ajax({
      type: "POST",
      url: $manager,
      data: {'aid':$aid,'value':$value,'name':$name,'mod':'alert','oid':0},
      cache: false,
      beforeSend: function(){
        spinner.spin(target);
      },
      success: function(data) {
        spinner.stop(target);
        if (data == 'Success') {
          $.growlUI('Success', "Data saved.");
        } else {
          $.growlUI('Error', data);
        }
      }
    });
  });
  /* multiselect for moving elements between two select fields */
  $('#categories').multiselect({
    afterMoveToRight:function($left, $right, $options) {
      var $oid = $options[0]['attributes']['value']['value'];
      $.ajax({
        type: "POST",
        url: $manager,
        data: {"aid":$aid,"oid":$oid,"action":"add","mod":"category"},
        beforeSend: function(){
          spinner.spin(target);
        },
        success: function(data) {
          spinner.stop(target);
          $.growlUI("Concern Type", "Added");
          return true;
        },
        error: function(data) {
          spinner.stop(target);
          $.growlUI("Concern Type", "Error");
          return false;
        }
      });
    },
    afterMoveToLeft:function($left, $right, $options) {
      var $oid = $options[0]['attributes']['value']['value'];
      $.ajax({
        type: "POST",
        url: $manager,
        data: {"aid":$aid,"oid":$oid,"action":"remove","mod":"category"},
        beforeSend: function(){
          spinner.spin(target);
        },
        success: function(data) {
          spinner.stop(target);
          $.growlUI("Concern Type", "Removed");
          return true;
        },
        error: function(data) {
          spinner.stop(target);
          $.growlUI("Concern Type", "Error");
          return false;
        }
      });
    }
  });
  /* remove a team member */
  $('.remove-member').on('click', function(e){
    e.preventDefault();
    var $dis = $(this);
    var $uid = $dis.attr("data-uid");
    var $mid = $dis.attr("data-mid");
    var $ln = $dis.attr("data-last_name");
    var $fn = $dis.attr("data-first_name");
    $dis.html('<i class="fa fa-refresh fa-spin"></i>');
    $.ajax({
      type: "POST",
      url: $manager,
      data: {"aid":$aid,"oid":$uid,"action":"remove","mod":"team"},
      success: function(data) {
        $('.tooltip').remove();
        $dis.html('<i class="fa fa-ban red" data-toggle="tooltip" data-placement="top" aria-hidden="true" title="'+$ln + ', '+ $fn + ' is no longer a member of the alert team"></i>');
        $('[data-toggle="tooltip"]').tooltip();
        $("#member_"+$mid).addClass('strike');
        $("#member_"+$mid).html('<span data-toggle="tooltip" data-placement="top" title="'+$ln + ', '+ $fn + ' is no longer a member of the alert team">'+$ln + ', '+ $fn + '</span>');
        $.growlUI("Team Member", "Removed");
      }
    });
    return false;
  });
  /* clear django cache object by cache key and refresh content */
  $('.clear-cache').on('click', function(e){
    e.preventDefault();
    var $dis = $(this);
    var $cid = $dis.attr("data-cid");
    var $target = '#' + $dis.attr("data-target");
    var $html = $dis.html();
    $dis.html('<i class="fa fa-refresh fa-spin"></i>');
    $.ajax({
      type: "POST",
      url: $clearCacheUrl,
      data: {"cid":$cid},
      success: function(data) {
        $.growlUI("Cache", "Clear");
        $($target).html(data);
        $dis.html('<i class="fa fa-refresh"></i>');
      },
      error: function(data) {
        $.growlUI("Error", data);
      }
    });
    return false;
  });
});
