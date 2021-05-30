$(document).ready(function() {
	var user_id = $("div#user_id").text();
	var last_click;

    logTime(user_id, "step1_start_time");

    // selection of reference domain
    var get_ref_domain = function(user_id) {
        $.ajax({
            "type": "GET",
            "url": "/step1/get_ref_domain",
            "success": function(data) {
                domain = data["ref_domain"];
                $("#selected_domain").html(data["ref_domain"]);
                counter = parseInt($("#counter").html())
                if (counter == 10) {
                    finish(user_id, "step1");
                } else {
                    $("#start").css("display", "inline-block");
                }
            }
        });
    }

    var checkForSpecialCharacters = function(created_domain) {
        specialChars = ["_", "<", ">", "&", "'", "\"", "=", "(", ")", "[", "]", "%", "$", "?", "#", "*", "+", "/", ",", ";", ":"];
        for (var i = 0; i < specialChars.length; i++) {
            if (created_domain.indexOf(specialChars[i]) > -1) {
                return true;
            }
        }

        return false;
    }

    var handle_created_domain = function() {
        created_domain = $("#created_domain").val();
        ref_domain = $("#selected_domain").html();
        if (created_domain == "I do not want to participate" ||
            (created_domain != "" &&
            created_domain.indexOf(" ") == -1 &&
            created_domain.indexOf(".") > -1 &&
            created_domain.indexOf("..") == -1 &&
            created_domain.charAt(0) != "." &&
            created_domain.charAt(created_domain.length - 1) != "." &&
            created_domain.charAt(0) != "-" &&
            created_domain.charAt(created_domain.length - 1) != "-" &&
            created_domain != ref_domain &&
            checkForSpecialCharacters(created_domain) == false)) {
            $("#domain_creation_label").css("display", "inline-block");
            $("#created_domain_label").html($("#created_domain").val());
        } else {
            $("#domain_creation_label").css("display", "none");
        }
    }

    var send_result = function(user_id, last_click) {
        created_domain = $("#created_domain").val();
        reference_domain = $("#selected_domain").html();
        now = (new Date()).getTime();
        elapsed_time = now - last_click;
        domain_position = parseInt($("#counter").html()) + 1;

        $.ajax({
            "type": "POST",
            "url": "/step1/result",
            "data": {"user_id": user_id,
                     "reference_domain": reference_domain,
                     "created_domain": created_domain,
                     "elapsed_time": elapsed_time,
                     "domain_position": domain_position},
            "success": function(data) {
                if (data["server_error"] == true) {
                    if ("no_participation" in data && data["no_participation"] == true) {
                        $("#experiment").remove();
                    }
                    $("#server_error_message").html(data["server_error_message"]);
                    $("#server_error").css("display", "block");
                } else {            
                    // link to same page
                    window.location.href = "/step1/user_id/" + user_id;
                }
            }
        });
    }

    $('#already_created ul li').each(function() {
        if ($(this).text() === "no_participation") {
            $("#start").remove();
            $("#experiment").remove();
        }
    });

    is_step_finished(user_id, "step1");

    get_ref_domain(user_id);

    $("#start").click(function() {
        last_click = startExperiment();
    });

    $("#created_domain").on("keyup", function() {
    	handle_created_domain();
    });

    $("#next_domain").click(function() {
    	send_result(user_id, last_click);
    });
});
