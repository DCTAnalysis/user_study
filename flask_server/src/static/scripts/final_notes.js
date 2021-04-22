$(document).ready(function() {
    var user_id = $("div#user_id").text();

    logTime(user_id, "experiment_end_time");

    var send_feedback = function(user_id) {
        feedback = $("#feedback").val();

        $.ajax({
            "type": "POST",
            "url": "/final_notes/feedback",
            "data": {"user_id": user_id,
                     "feedback": feedback},
            "success": function(data) {
                if (data["server_error"] == true) {
                    $("#server_error_message").html(data["server_error_message"]);
                    $("#server_error").css("display", "block");
                } else {
                    $("#server_success").css("display", "block");
                    $("#feedback_wrapper").css("display", "none");
                }
            }
        });
    }

    $("#send_feedback").click(function() {
        if ($("#feedback").val().length > 0) {
            send_feedback(user_id);
        }
    });
});
