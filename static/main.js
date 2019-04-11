// js
$('.ui.sidebar').sidebar('toggle');

$('.ui.modal').modal();

$('.ui.accordion').accordion();

$('.ui.dropdown').dropdown();

$('.bars-btn').click(function() {
  $('.ui.sidebar').sidebar('toggle');
});

$('.message .close')
  .on('click', function() {
    $(this)
      .closest('.message')
      .transition('fade')
    ;
  })
;