$(document).ready(function() {
	var user_id = $("div#user_id").text();
	var last_click;

    logTime(user_id, "step4_start_time");

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
        if (created_domain != "" && checkForSpecialCharacters(created_domain) == false) {
            $("#domain_creation_label").css("display", "inline-block");
            $("#created_domain_label").html($("#created_domain").val());
        } else {
            $("#domain_creation_label").css("display", "none");
        }
    }

    var send_result = function(user_id, last_click) {
        created_domain = $("#created_domain").val();
        now = (new Date()).getTime();
        elapsed_time = now - last_click;
        domain_position = parseInt($("#counter").html()) + 1

        $.ajax({
            "type": "POST",
            "url": "/step4/result",
            "data": {"user_id": user_id,
                     "created_domain": created_domain,
                     "elapsed_time": elapsed_time,
                     "domain_position": domain_position},
            "success": function(data) {
                if (data["server_error"] == true) {
                    $("#server_error_message").html(data["server_error_message"]);
                    $("#server_error").css("display", "block");
                } else {            
                    // link to same page
                    window.location.href = "/step4/user_id/" + user_id;
                }
            }
        });
    }

    is_step_finished(user_id, "step4");

    counter = parseInt($("#counter").html())
    if (counter == 10) {
        finish(user_id, "step4");
    } else {
        $("#start").css("display", "inline-block");
    }

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
