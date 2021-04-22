var is_step_finished = function(user_id, step_id) {
    $.ajax({
        "type": "GET",
        "url": "/is_step_finished/user_id/" + user_id + "/step_id/" + step_id,
        "success": function(data) {
            if (data["server_error"] == true) {
                $("#server_error_message").html(data["server_error_message"]);
                $("#server_error").css("display", "block");
            } else if (data["is_step_finished"] == true) {
                if ($("#start").length) {
                    $("#start").remove();
                }
                // remove experiment div
                $("#experiment").remove();
                // set continue link visible
                $("#continue").css("display", "block");
                $("#continue_info").html("You already finished this step!");
            }
        }
    });
}

var logTime = function(user_id, type) {
    current_time = (new Date()).getTime();
    $.ajax({
        "type": "POST",
        "url": "/log_time",
        "data": {"user_id": user_id, "type": type, "time": current_time},
        "success": function(data) {
            if (data["server_error"] == true) {
                $("#server_error_message").html(data["server_error_message"]);
                $("#server_error").css("display", "block");
            }
        }
    });
}

var startExperiment = function() {
    // remove start button div
    $("#start").remove();
    // set experiment visible
    $("#experiment").css("display", "block");
    // set last_click to current time
    last_click = (new Date()).getTime();

    return last_click;
}

var finish = function(user_id, step_id) {
    $("#experiment").remove();
    $("#start").remove();
    // log time to calculate how long it took to finish the step
    logTime(user_id, step_id + "_end_time");

    // send message to server that step has been finished
    $.ajax({
        "type": "POST",
        "url": "/set_step_finished",
        "data": {"user_id": user_id, "step_id": step_id},
        "success": function(data) {
            if (data["server_error"] == true) {
                $("#server_error_message").html(data["server_error_message"]);
                $("#server_error").css("display", "block");
            } else {
                // set continue link visible
                $("#continue").css("display", "block");
            }
        }
    });
}

function addRemoveClasses(elem, addClasses, removeClasses) {
    elem.removeClass(removeClasses).addClass(addClasses);
}

function handleDropDownMenu(arrowNormal, arrowDown, dropDownElem, triggerOnParent) {
    if ($(arrowNormal) == null) {
        return;
    }

    var openMenu = function () {
        // hide self
        addRemoveClasses($(arrowNormal), "hidden", "inline-block");

        // show down arrow
        addRemoveClasses($(arrowDown), "inline-block", "hidden");

        addRemoveClasses($(dropDownElem), null, "hidden");
    };

    var closeMenu = function () {
        // hide self
        addRemoveClasses($(arrowDown), "hidden", "inline-block");

        // show down arrow
        addRemoveClasses($(arrowNormal), "inline-block", "hidden");

        addRemoveClasses($(dropDownElem), "hidden", null);
    };

    if (triggerOnParent) {
        // trigger when we click on parent container
        var parentElem = $(arrowNormal).parent();

        var open = false;
        var hover = parentElem.attr('class') != null 
            && parentElem.attr('class').split(" ").includes("hover_highlight_color");

        parentElem.click(function () {
            if (open) {
                closeMenu();
                open = false;
                if (hover) {
                    $(this).addClass("hover_highlight_color");
                }
            } else {
                openMenu();
                open = true;
                if (hover) {
                    $(this).removeClass("hover_highlight_color");
                }
            }
        });

    } else {
        // directly on arrow elements
        $(arrowNormal).click(openMenu);
        $(arrowDown).click(closeMenu);    
    }
}

function handleProgressBar() {
    // strike through everything before current step
    var foundStepMarker = false;
    $("#progress_bar").find(".label").each(function () {
        // detect current step marker and abort
        if ($(this).find("i").length > 0) {
            foundStepMarker = true;
        }
        if (foundStepMarker) {
            return;
        }

        $(this).addClass("strike_through");
    });
}

// ============================================================================
// Ready function common for all pages
// ============================================================================
$(document).ready(function () {
    // wire up drop down
    handleDropDownMenu("#created_arrow_left", "#created_arrow_down", "#already_created", true);
    handleDropDownMenu("#requirements_arrow_left", "#requirements_arrow_down", "#domain_creation_requirements", true);

    handleProgressBar();
});
