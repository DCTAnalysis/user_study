$(document).ready(function() {
    var user_id = $("div#user_id").text();
    var error = false;

    logTime(user_id, "questionnaire_start_time");

    $.ajax({
        "type": "GET",
        "url": "/is_step_finished/user_id/" + user_id + "/step_id/questionnaire",
        "success": function(data) {
            if (data["server_error"] == true) {
                $("#server_error_message").html(data["server_error_message"]);
                $("#server_error").css("display", "block");
            } else {
                if (data["is_step_finished"] == true) {
                    $("#server_error_message").html("You already answered the questionnaire");
                    $("#server_error").css("display", "block");
                    // set continue link visible
                    $("#continue").css("display", "block");
                    // set send questionnaire wrapper invisible
                    $("#send_questionnaire_wrapper").css("display", "none");
                    $("#questionnaire").remove();
                    document.getElementById("continue").scrollIntoView();
                }
            }
        }
    });

    $("#origin_selection_button").click(function() {
        // display/hide dropdown menu for domain selection
        $("#dropdown_content_origin").toggle();
    });

    $("#dropdown_content_origin a").click(function() {
        // get selected country
        country = $(this).html();

        // remove dropdown menu and replace it with the selected domain
        $("#dropdown_content_origin").toggle();
        $("#selected_country").html(country);
    });

    var getValue = function(identifier) {
        $("#" + identifier + " p").removeClass("red");
        var value = $("input[name='" + identifier + "']:checked").val();
        if (typeof(value) === "undefined") {
            error = true;
            $("#" + identifier + " p").addClass("red");
        }

        return value;
    }

    var sendResults = function(data) {
        $.ajax({
            "type": "POST",
            "url": "/questionnaire/results",
            "data": data,
            "success": function(data) {
                if (data["server_error"] == true) {
                    $("#server_error_message").html(data["server_error_message"]);
                    $("#server_error").css("display", "block");
                } else {
                    if (data["already_inserted"] == true) {
                        $("#server_error_message").html("You already answered the questionnaire");
                        $("#server_error").css("display", "block");
                    } else {
                        logTime(user_id, "questionnaire_end_time");
                        // set continue link visible
                        $("#continue").css("display", "block");
                        // set questions invisible
                        $("#questionnaire").css("display", "none");
                        // set server error invisible
                        $("#server_error").css("display", "none");
                        // set send questionnaire wrapper invisible
                        $("#send_questionnaire_wrapper").css("display", "none");
                    }
                }
            }
        });
    }

    $("#send_questionnaire").click(function() {
        // error would stay true if we don't reset it
        // every time the button is clicked
        error = false;
        $("#origin p").removeClass("red");
        origin = $("#selected_country").html();
        if (origin == "Click to select a country") {
            error = true;
            $("#origin p").addClass("red");
        }

        // get radio button's values
        data = {"user_id":         user_id,
                "age":             getValue("age"),
                "gender_current":  getValue("current_gender"),
                "education":       getValue("education"),
                "origin":          origin,
                "f1":              getValue("f1"),
                "f2":              getValue("f2"),
                "f3":              getValue("f3"),
                "f4":              getValue("f4"),
                "f5":              getValue("f5"),
                "f6":              getValue("f6"),
                "f7":              getValue("f7"),
                "f8":              getValue("f8"),
                "f9":              getValue("f9"),
                "f10":             getValue("f10"),
                "f11":             getValue("f11"),
                "f12":             getValue("f12"),
                "f13":             getValue("f13"),
                "f14":             getValue("f14"),
                "f15":             getValue("f15"),
                "f16":             getValue("f16"),
                "attention_test1": getValue("attention_test1"),
                "attention_test2": getValue("attention_test2")};

        if (error) {
            // display error message when values are missing
            $("#server_error_message").html("Missing answers! Please answer the red marked questions.");
            $("#server_error").css("display", "block");
        } else {
            // send answers to server
            sendResults(data);
        }
    });
});