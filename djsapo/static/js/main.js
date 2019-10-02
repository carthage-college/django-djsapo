// Opera 8.0+
var isOpera = (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;
// Firefox 1.0+
var isFirefox = typeof InstallTrigger !== 'undefined';
// Safari 3.0+ "[object HTMLElementConstructor]"
var isSafari = /constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!window['safari'] || (typeof safari !== 'undefined' && safari.pushNotification));
// Internet Explorer 6-11
var isIE = /*@cc_on!@*/false || !!document.documentMode;
// Edge 20+
var isEdge = !isIE && !!window.StyleMedia;
// Chrome 1 - 71
var isChrome = !!window.chrome && (!!window.chrome.webstore || !!window.chrome.runtime);
// Blink engine detection
var isBlink = (isChrome || isOpera) && !!window.CSS;

if (isFirefox==false && isChrome==false && isOpera==false && isSafari==false) {
    alert('Please use the FireFox, Chrome, Safari 12+, or Opera Browser');
}

/*
var output = 'Detecting browsers by ducktyping:<hr>';
output += 'isFirefox: ' + isFirefox + '<br>';
output += 'isChrome: ' + isChrome + '<br>';
output += 'isSafari: ' + isSafari + '<br>';
output += 'isOpera: ' + isOpera + '<br>';
output += 'isIE: ' + isIE + '<br>';
output += 'isEdge: ' + isEdge + '<br>';
output += 'isBlink: ' + isBlink + '<br>';
//document.body.innerHTML = output;
console.log(output);
*/

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
  /* print page */
  $('#print').click(function() {
    window.print();
    return false;
  });
  /* datepicker */
  $('#id_interaction_date').datepicker({
    firstDay:1,
    maxDate: new Date,
    changeFirstDay:false,
    dateFormat:'yy-mm-dd',
    buttonImage:'//www.carthage.edu/themes/shared/img/ico/calendar.gif',
    showOn:'both',
    buttonImageOnly:true
  });
  /* wysiwyg for textarea fields */
  var $trumBowygDict = {
    btns: [
      ['formatting'], ['strong', 'em', 'del'], ['link'],
      ['unorderedList', 'orderedList'], ['horizontalRule'], ['viewHTML'],
    ],
    tagsToRemove: ['script', 'link'], urlProtocol: true,
    removeformatPasted: true, semantic: true, autogrow: true, resetCss: true
  };
  /* limit alert details textareas to 250 words */
  var maxWords = 250;
  var maxAlert = false;
  $('textarea').trumbowyg($trumBowygDict).on('tbwchange', function(e){
    var $this, wordcount;
    $this = $(this);
    //wordcount = $this.val().split(/\b[\s,\.-:;]*/).length;
    wordcount = $this.val().split(" ").length;
    //var length = maxLength - $(this).val().length;
    $('#' + $this.attr('name')).text(maxWords - wordcount);
    if (wordcount > maxWords && maxAlert == false) {
      alert('Please limit your text\nto fewer than 250 words')
      maxAlert = true;
      $('#' + $this.attr('name')).parent().css({'color':'red','font-weight':'bold'});
      //$(this).trumbowyg('disable');
      //e.preventDefault();
    }
    if (wordcount < maxWords) {
      $('#' + $this.attr('name')).parent().css({'color':'#212529','font-weight':'normal'});
    }
  });
  /* fancy picker for select fields */
  $('#id_relationship').selectpicker();
  $('#id_category').selectpicker();
  $('#students-toggle').change(function() {
    this.form.submit();
  });
  /* modal form for textarea data */
  $(document).on('click','.text-update', function (e) {
    var $dis = $(this);
    var $oid = $dis.attr('data-oid');
    var $mod = $dis.attr('data-mod');
    var $fld = $dis.attr('data-fld');
    if ($mod == 'comment') {
        header = 'follow-up';
    } else {
        header = $mod.replace(/_/g, ' ');;
    }
    if ($oid && $mod) {
      $.ajax({
        url: $manager,
        type: 'post',
        data: {'aid':$aid,'action':'fetch','mod':$mod,'oid':$oid,'name':$fld},
        success: function(data){
          // Add response in Modal body
          $('#id_oid').val(data['id']);
          $('#id_fld').val($fld);
          $('#id_body').val(data['msg']);
          $('#textModalHeader').text('Update ' + header);
          // Display Modal
          $('#id_body').trumbowyg('destroy');
          $('#textModal').modal('show');
          $('#id_body').trumbowyg($trumBowygDict);
        }
      });
    } else {
        if ($mod == 'comment') {
          $('#id_oid').val(0);
          $('#id_fld').val('');
          $('#id_body').val('');
          $('#textModalHeader').text('New ' + header);
          // Display Modal
          $('#id_body').trumbowyg('destroy');
          $('#textModal').modal('show');
          $('#id_body').trumbowyg($trumBowygDict);
        }
    }
    $('#id_mod').val($mod);
  });
  $('#textModal').submit(function(e){
    e.preventDefault();
    var $body = $('#id_body').val();
    var $oid = $('#id_oid').val();
    var $mod = $('#id_mod').val();
    var $fld = $('#id_fld').val();
    $.ajax({
      type: 'POST',
      url: $manager,
      data: {'aid':$aid,'value':$body,'mod':$mod,'oid':$oid,'name':$fld},
      cache: false,
      beforeSend: function(){
        $('#textModal').modal('hide');
      },
      success: function(data){
        if (data['id']) {
          $id = ''
          if ($fld) {
            $id = $fld + '_'
          }
          $('#oid_' + $id + data['id']).replaceWith(data['msg']);
        } else {
          $('#comments-list').prepend(data['msg']);
        }
        $('#id_body').val('');
        $('.modal-backdrop').remove();
      },
      error: function(data){
        //console.log(data);
        $.growlUI($mod + " Form", "Error");
      }
    });
    return false;
  });
  $('#textModal').on('shown.bs.modal', function () {
    $('#id_body').focus();
  })
  $('#textModal').on('hidden.bs.modal', function () {
    $('#id_body').trumbowyg('destroy');
    $('#id_body').trumbowyg($trumBowygDict);
  });
  /* function to update a name/value pair for models */
  $('.set-val').on('change', function(e) {
    e.preventDefault();

    var $dis = $(this);
    var $name = $dis.attr('name');
    var $value = $dis.val();
    var $data = {'aid':$aid,'value':$value,'name':$name,'mod':'concern','oid':0};
    $.ajax({
      type: 'POST',
      url: $manager,
      data: $data,
      cache: false,
      beforeSend: function(){
        spinner.spin(target);
      },
      success: function(data) {
        spinner.stop(target);
        $.growlUI('Success', "Data saved.");
      },
      error: function(data) {
        spinner.stop(target);
        $.growlUI('Error', data);
      }
    });
    return false;
  });
  $(".alert-status").click(function () {
    $.ajax({
      type: "POST",
      url: $manager,
      data: {'aid':$aid,'value':'Closure suggested','name':'status','mod':'concern','oid':0},
      cache: false,
      beforeSend: function(){
        spinner.spin(target);
      },
      success: function(data) {
        spinner.stop(target);
        $.growlUI("Concern Status", data['msg']);
        $('#alertStatus').hide();
        $('#id_status option[value="Closure suggested"]').attr('selected','selected');
        $('#id_status').text('Closure suggested');
        //$('.bootstrap-select .filter-option').text(text);
        $('.selectpicker').selectpicker('refresh');
      },
      error: function(data) {
        spinner.stop(target);
        $.growlUI('Error', data);
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
          $.growlUI("Success", "Data saved");
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
          $.growlUI("Success", "Data saved");
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
        $dis.html('<i class="fa fa-ban red" data-toggle="tooltip" data-placement="top" aria-hidden="true" title="'+$ln + ', '+ $fn + ' is no longer a member of the team"></i>');
        $('[data-toggle="tooltip"]').tooltip();
        $('#member_'+$mid).addClass('strike');
        $('#del_'+$uid).addClass('strike');
        $('#member_'+$mid).html('<span data-toggle="tooltip" data-placement="top" title="'+$ln + ', '+ $fn + ' is no longer a member of the team">'+$ln + ', '+ $fn + '</span>');
        $.growlUI("Success", "Data saved");
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
    stripeClasses: [],
    order: [[ 1, 'asc' ]]
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
  /* team manager sortables */
  $('#matrix-table').sortable({
      group: {
          name:'matrix',
          pull:['team']
      },
      animation: 150,
      sort: false
  });
  $('#team-members').sortable({
      group: {
          name: 'team',
          put: ['matrix','facstaff'],
          pull: ['matrix','facstaff']
      },
      animation: 150,
      sort: false,
      filter: '.strike', // is not draggable
      onAdd: function (evt) {
          $('#team-members tr .dataTables_empty').hide();
          $data = evt['item']['firstElementChild']['dataset'];
          $uid = $data['uid'];
          $lastName = $data['last_name'];
          $firstName = $data['first_name'];
          $uidDom = $('[data-uid="' + $uid + '"]');
          var $mid = null;
          $.ajax({
            type: "POST",
            url: $manager,
            data: {"aid":$aid,"oid":$uid,"action":"add","mod":"team"},
            beforeSend: function(){
              spinner.spin(target);
            },
            success: function(data) {
              spinner.stop(target);
              $mid=data['id']
              $('#del_' + $uid).prepend('<td class="text-center"><a href="#" class="remove-member" data-uid="'+$uid+'" data-mid="'+$mid+'" data-last_name="'+$lastName+'" data-first_name="'+$firstName+'"><i class="fa fa-times red blue-tooltip" data-toggle="tooltip" data-placement="top" aria-hidden="true" title="Remove from the team"></i></a></td>');
              $.growlUI("Member Status", data['msg']);
              return true;
            },
            error: function(data) {
              spinner.stop(target);
              $.growlUI("Team Member", "Error");
              return false;
            }
          });
      }
  });
  $('#faculty-staff').sortable({
      group: {
          name: 'facstaff'
      },
      animation: 150,
      sort: false,
      filter: '.dataTables_empty' // is not draggable
  });
  $('#confirm-delete').on('show.bs.modal', function(e) {
    $(this).find('.btn-ok').attr('href', $(e.relatedTarget).data('href'));
    $('.object-title').text( $(e.relatedTarget).data('title') );
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
