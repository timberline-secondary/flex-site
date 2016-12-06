/**
 * Created by couture on 01/12/16.
 */
var $table = $('#table'),

    $flex1_selection = $('#id_flex_1_event_choice'),
    $flex2_selection = $('#id_flex_2_event_choice'),

    $blockConfirmModal = $('#block-confirmation-modal'),
    $blockConfirmModalTitle = $('#block-confirmation-modal').find('.modal-title'),
    $blockConfirmModalBody = $('#block-confirmation-modal').find('.modal-body'),
    $btnConfirmFlex1 = $('#btn-confirm-flex-1'),
    $btnConfirmFlex2 = $('#btn-confirm-flex-2'),
    $btnCancel = $('#btn-confirm-cancel');

function getIdSelections() {
    console.log("getting selections");
    return $.map($table.bootstrapTable('getSelections'), function (row) {
        return row.id
    });
}

F1_XOR_F2 = 0;
F1_OR_F2 = 1;
F1_AND_F2 = 2;
FLEX1 = "FLEX1"
FLEX2 = "FLEX2"
XOR_HTML = "<p>You can only register for one of this event's blocks.</p>" +
    "<p>Which block do you want to add to your registration form?</p>";
OR_HTML = "<p>You can register for both blocks or just one block for this event. If you want to register for both, " +
    "you can select it a second time.</p>" +
    "<p>Which block do you want to add to your registration form?</p>"
AND_HTML = "<p>This event requires you to attend both Flex 1 and Flex 2.</p>" +
    "<p>Would you like to add this event to your registration form?</p>"
ONE_HTML = "<p>Add this event to your registration form?</p>"
BTN_TEXT_F1 = "Add for Flex 1"
BTN_TEXT_F2 = "Add for Flex 2"
BTN_TEXT_BOTH = "Add for both Flex 1 and Flex 2";

REG_STATUS_CLEAR = "Your registration form is empty.  Click an event below to add it to your form."
REG_STATUS_BOTH = "You registration form is full.  Hit the Save Selections button to register for these events."
REG_STATUS_1_ONLY = "The Flex 2 block is empty on your registration form. Click on one of the available events below."
REG_STATUS_2_ONLY = "The Flex 1 block is empty on your registration form. Click on one of the available events below."


/**
 * Set the prompts and button text for the modal then display it.
 * @param row
 */
function whichFlexModal(row) {
    $btnConfirmFlex1.data("event-id", row.id);
    $btnConfirmFlex2.data("event-id", row.id);
    $blockConfirmModalTitle.text(row.titletext);
    if (row.blockselection == F1_OR_F2) {
        $btnConfirmFlex1.text(BTN_TEXT_F1);
        $btnConfirmFlex2.text(BTN_TEXT_F2);
        $blockConfirmModalBody.html(OR_HTML);
        $btnConfirmFlex2.show();
    }
    else if (row.blockselection == F1_XOR_F2) {
        $btnConfirmFlex1.text(BTN_TEXT_F1);
        $btnConfirmFlex2.text(BTN_TEXT_F2);
        $blockConfirmModalBody.html(XOR_HTML);
        $btnConfirmFlex2.show();
    }
    else if (row.blockselection == F1_AND_F2) {
        $blockConfirmModalBody.html(AND_HTML);
        $btnConfirmFlex1.text(BTN_TEXT_BOTH);
        $btnConfirmFlex2.hide();
    }
    else if (row.blockselection == FLEX1) {
        $blockConfirmModalBody.html(ONE_HTML);
        $btnConfirmFlex1.text(BTN_TEXT_F1);
        $btnConfirmFlex2.hide();
    }
    else if (row.blockselection == FLEX2) {
        $blockConfirmModalBody.html(ONE_HTML);
        $btnConfirmFlex1.text(BTN_TEXT_F2);
        $btnConfirmFlex2.hide();
    }
    else {// shouldn't get here
        console.log("Block selection not understood")
        return;
    }
    $blockConfirmModal.modal();
}

// EVENTS
/**
 * When a row is clicked, open a modal dialog to confirm
 */
$table.bootstrapTable({
    onClickRow: function (row, $element, field) {
        whichFlexModal(row, $element);
    }
});

/**
 * Hide all rows/events that are no longer relevant:
 */
function hideRows() {
    var flex1_id = $flex1_selection.val();
    var flex2_id = $flex2_selection.val();

    var f1 = true;
    var f2 = true;
    if( $flex1_selection.val() == "")
        f1 = false;
    if( $flex2_selection.val() == "")
        f2 = false;

    // console.log("F1 choice: " + flex1_id);
    // console.log("F2 choice: " + flex2_id);

    $rows = $table.find('tbody > tr')

    if(f1 && f2) {
        $rows.hide();
    }
    else if (f1 || f2) {
        $rows.each( function( index, element ) {
            var event_id = $(element).data("uniqueid");
            var row = $table.bootstrapTable('getRowByUniqueId', event_id); // row to use BT conveniences
            var hide = false;
            if( row.blockselection == F1_AND_F2 )
                hide = true;
            else if ( row.blockselection == F1_XOR_F2 && (event_id == flex1_id || event_id == flex2_id) )
                hide = true;
            else if (f1) { //f2
                if (row.blockselection == FLEX1)
                    hide = true
            }
            else { //f2
                if (row.blockselection == FLEX2)
                    hide = true
            }

            if (hide) {
                $table.bootstrapTable('hideRow', {uniqueId: row.id});
                //element.hide(); //JQuery way, easier?
            }
        }); //for each row
    }
    else { // shouldn't get here
        console.log("How was no Flex block selected?")
        return;
    }

    // scroll back to the registrations form
    // $('html, body').animate({
    //     scrollTop: $("#register-prompt").offset().top
    // }, 500);
}

// Listen for the clicked buttons in confirmation modal
// http://stackoverflow.com/questions/28270333/how-do-i-know-which-button-is-click-when-bootstrap-modal-closes
var $buttons = $('#block-confirmation-modal .modal-footer button');


$(function () {
    $buttons.click(function (e) {
        var $target = $(e.target); // Clicked button element

        if ($target.is($btnCancel) )
            return

        var event_id = $target.data("event-id");
        var row = $table.bootstrapTable('getRowByUniqueId', event_id);
        // console.log("clicked for event: " + event_id);

        if (row.blockselection == F1_OR_F2 || row.blockselection == F1_XOR_F2) {
            // Get which confirmation button was pressed button
            if ($target.is($btnConfirmFlex1)) {
                $flex1_selection.val(event_id); // set the form selection
            }
            else if ($target.is($btnConfirmFlex2)) {
                $flex2_selection.val(event_id);
            }
            else { //shouldn't get here
                console.log("unknown button clicked");
                return;
            }
        }
        else if (row.blockselection == F1_AND_F2) {
            $flex1_selection.val(event_id);
            $flex2_selection.val(event_id);

        }
        else if (row.blockselection == FLEX1) {
            $flex1_selection.val(event_id);
        }
        else if (row.blockselection == FLEX2) {
            $flex2_selection.val(event_id);
        }
        else { // shouldn't get here
            console.log("Block selection not understood")
            return;
        }

        hideRows();

    }); // button click
});

// Clear selections:
$('#clear-selections').on('click', function (e) {
    // Reset the event choices
    $flex1_selection.val("");
    $flex2_selection.val("");

    // show all events
    $table.bootstrapTable('getRowsHidden', true);

});

