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
