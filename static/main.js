// js
$('.ui.sidebar').sidebar();

$('.ui.modal').modal();

$('.ui.accordion').accordion();

$('.ui.dropdown').dropdown();

$('.message .close')
  .on('click', function() {
    $(this)
      .closest('.message')
      .transition('fade')
    ;
  })
;