/**
 * Created by couture on 22/12/16.
 */

$(document).ready(function () {

    var $modal = $('#keypadEntryModal');
    var $numberField = $("#studentNumberField");
    var $confirmBtn = $("#keypadEnter");
    var $results = $("#keypadResult");

    function resetKeyInput() {
      $numberField.focus();
      $numberField.val("");
      $numberField.val("99");
    }

    $modal.on('shown.bs.modal', function () {
        resetKeyInput();
    });

    // Bind "Enter" key to the submit button:
    $numberField.keyup(function (event) {
        if (event.keyCode == 13) {
            $confirmBtn.click();
        }
    });

    // When the enter button is click (via enter key also) set absent to false on form for that student
    $confirmBtn.click(function (e) {
        var studentNumber = $numberField.val();
        resetKeyInput();

        // find the row that contains the student number
        var $row = $("#attendance-form td").filter(function () {
            return $(this).text() == studentNumber;
        }).parent();

        if ($row.length > 0) { //found the row
            // untick the absent checkbox
            var $absentBox = $row.find("td:first-child input");
            $absentBox.prop('checked', false);

            var first = $row.find("td.attendance-first-name").html();
            var last = $row.find("td.attendance-last-name").html();
            var icon = "<i class='fa fa-2x fa-check text-success'></i>";
            var results = icon + " " + first + " " + last;

        }
        else {
            icon = "<i class='fa fa-2x fa-close text-danger'></i>"
            results = icon + " " + studentNumber + " not registered ";
        }
        $results.html(results);

    });
});