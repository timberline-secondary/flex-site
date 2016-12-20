function WednesdaysOnly(date) {
  var day = date.getDay();
  if (day == 3) //Wednesday = 3
    return [true]
  else
    return [false]
}

$(document).ready(function () {
  $('#datepicker').datepicker({
    dateFormat: 'yy-mm-dd',
    showOtherMonths: true,
    selectOtherMonths: true,
    onSelect: function (dateText, inst) {
      $('#filter_form').submit(); // <-- SUBMIT
    },
    beforeShowDay: WednesdaysOnly,

  });
});