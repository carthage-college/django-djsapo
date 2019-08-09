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
var target = document.getElementById('alert-container');
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
  /* team manager modal */
  $('#teamModalOpen').on('click',function(){
  });
  /* print page */
  $('#print').click(function() {
    window.print();
    return false;
  });
  /* datepicker */
  $('#id_interaction_date').datepicker({
    firstDay:1,
    changeFirstDay:false,
    dateFormat:'yy-mm-dd',
    buttonImage:'//www.carthage.edu/themes/shared/img/ico/calendar.gif',
    showOn:'both',
    buttonImageOnly:true
  });
  /* wysiwyg for textarea fields */
  var $trumBowygDict = {
    btns: [
      ['formatting'], ['strong', 'em', 'del'],
      ['unorderedList', 'orderedList'], ['horizontalRule'], ['viewHTML'],
    ],
    tagsToRemove: ['script', 'link'],
    removeformatPasted: true, semantic: true, autogrow: true, resetCss: true
  };
  $('textarea').trumbowyg($trumBowygDict);
  /* fancy picker for select fields */
  $('#id_relationship').selectpicker();
  $('#id_category').selectpicker();
  /* toggle interaction fields */
  $('input[name="interaction"]').click(function() {
    toggle(this.value, 'Yes', '#interactionFields');
  });
  $('#students-toggle').change(function() {
    this.form.submit();
  });
  /* comments form */
  $(document).on('click','.comment-update', function (e) {
    var $dis = $(this);
    var $oid = $dis.attr('data-fid');
    if ($oid) {
      $.ajax({
        url: $manager,
        type: 'post',
        data: {'aid':$aid,'action':'fetch','mod':'comment','oid':$oid},
        success: function(data){
          // Add response in Modal body
          $('#id_fid').val(data['id']);
          $('#id_body').val(data['msg']);
          // Display Modal
          $('#id_body').trumbowyg('destroy');
          $('#commentsForm').modal('show');
          $('#id_body').trumbowyg($trumBowygDict);
        }
      });
    }
  });
  $('#commentsForm').submit(function(e){
    e.preventDefault();
    var $body = $('#id_body').val();
    var $oid = $('#id_fid').val();
    $.ajax({
      type: 'POST',
      url: $manager,
      data: {'aid':$aid,'body':$body,'mod':'comment','oid':$oid},
      cache: false,
      beforeSend: function(){
        $('#commentsModal').modal('hide');
      },
      success: function(data){
        if (data['id']) {
          $('#fid_' + data['id']).replaceWith(data['msg']);
        } else {
          $('#comments-list').prepend(data['msg']);
        }
        $('#id_body').val('');
        $('.modal-backdrop').remove();
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
  $('#commentsModal').on('hidden.bs.modal', function () {
    $('#id_body').trumbowyg('destroy');
  });
  /* function to update a name/value pair for models */
  $('.set-val').on('change', function() {
    var $dis = $(this);
    var $name = $dis.attr('name');
    var $value = $dis.val();
    $.ajax({
      type: 'POST',
      url: $manager,
      data: {'aid':$aid,'value':$value,'name':$name,'mod':'alert','oid':0},
      cache: false,
      beforeSend: function(){
        spinner.spin(target);
      },
      success: function(data) {
        spinner.stop(target);
        if (data['msg'] == 'Success') {
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
        type: 'POST',
        url: $manager,
        data: {'aid':$aid,'oid':$oid,'action':'add','mod':'category'},
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
        type: 'POST',
        url: $manager,
        data: {'aid':$aid,'oid':$oid,'action':'remove','mod':'category'},
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
  $(document).on('click','.remove-member', function (e) {
    e.preventDefault();
    var $dis = $(this);
    var $uid = $dis.attr('data-uid');
    var $mid = $dis.attr('data-mid');
    var $ln = $dis.attr('data-last_name');
    var $fn = $dis.attr('data-first_name');
    $dis.html('<i class="fa fa-refresh fa-spin"></i>');
    $.ajax({
      type: 'POST',
      url: $manager,
      data: {'aid':$aid,'oid':$uid,'action':'remove','mod':'team'},
      success: function(data) {
        $('.tooltip').remove();
        $dis.html('<i class="fa fa-ban red" data-toggle="tooltip" data-placement="top" aria-hidden="true" title="'+$ln + ', '+ $fn + ' is no longer a member of the alert team"></i>');
        $('[data-toggle="tooltip"]').tooltip();
        $('#member_'+$mid).addClass('strike');
        $('#del_'+$uid).addClass('strike');
        $('#member_'+$mid).html('<span data-toggle="tooltip" data-placement="top" title="'+$ln + ', '+ $fn + ' is no longer a member of the alert team">'+$ln + ', '+ $fn + '</span>');
        $.growlUI("Team Member", "Removed");
      }
    });
    return false;
  });
  /* clear django cache object by cache key and refresh content */
  $('.clear-cache').on('click', function(e){
    e.preventDefault();
    var $dis = $(this);
    var $cid = $dis.attr('data-cid');
    var $target = '#' + $dis.attr('data-target');
    var $html = $dis.html();
    $dis.html('<i class="fa fa-refresh fa-spin"></i>');
    $.ajax({
      type: 'POST',
      url: $clearCacheUrl,
      data: {'cid':$cid},
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
  /* datatables initialization */
  $('.data-table').DataTable({
    dom: 'lfrBtip',
    bFilter: false,
    paging: false,
    info: false,
    buttons: [],
    stripeClasses: []
  });
  $('.sos-matrix').DataTable({
    'lengthMenu': [
      [15], [15]
    ],
    dom: 'lfrBtip',
    buttons: [],
    stripeClasses: [],
    info: false,
    paging: true,
    lengthChange: false,
    searching: true
  });
  $('.faculty-staff').DataTable({
    'lengthMenu': [
      [15], [15]
    ],
    dom: 'lfrBtip',
    buttons: [],
    stripeClasses: [],
    info: false,
    paging: true,
    lengthChange: false,
    searching: true
  });
  var alertTable = $('#data-table').DataTable({
    'lengthMenu': [
      [25, 50, 100, 250, 500, 1000, 2000, -1],
      [25, 50, 100, 250, 500, 1000, 2000, 'All']
    ],
    dom: 'lfrBtip',
    buttons: [
      'csv', 'excel'
    ]
  });
  /* override the submit event for the alert form to handle some things */
  $('form#alert-form').submit(function(){
    // set the value of the student field to email address selected
    // via autocomplete
    $('#autoComplete').val($('#autoComplete').attr('data-email'));
    /* check textarea for just br tag */
    $('textarea').each(function(){
      if (this.value == '<br>') {
          this.value = '';
      }
    });
    // disable submit button after users clicks it
    $(this).children('input[type=submit]').attr('disabled', 'disabled');
  });
});
