$(document).ready(function() {
    var user_id = $("div#user_id").text();
    var last_click = 0;
    var finished = false;
    var type = "";
    var domain = "";
    var counter = 0;

    logTime(user_id, "step3_start_time");

    var getNextDomain = function() {
        $.ajax({
            "type": "GET",
            "url": "/step3/next_domain/user_id/" + user_id,
            "success": function(data) {
                if (data["server_error"] == true) {
                    $("#server_error_message").html(data["server_error_message"]);
                    $("#server_error").css("display", "block");
                } else {
                    if (data["domains_available"] == false) {
                        finish(user_id, "step3");
                    } else {
                        type = data["type"];
                        counter = parseInt(data["count"], 10);
                        $("#counter").html(counter);
                        // display domain when request was successful
                        if (counter >= 30 && !finished) {
                            finish(user_id, "step3");
                        } else {
                            $("#domain").html(data["next_domain"]);
                            domain = data["next_domain"]
                            $("#start").css("display", "inline-block");
                        }
                    }
                }
            }
        })
    }

    var sendResult = function(rating, elapsed_time, domain_position) {
        $.ajax({
            "type": "POST",
            "url": "/step3/result",
            "data": {"user_id": user_id,
                     "rated_domain": domain,
                     "type": type,
                     "elapsed_time": elapsed_time,
                     "rating": rating,
                     "domain_position": domain_position},
            "success": function(data) {
                if (data["server_error"] == true) {
                    $("#server_error_message").html(data["server_error_message"]);
                    $("#server_error").css("display", "block");
                } else {
            	    getNextDomain();
                }
            }
        });
    }

    is_step_finished(user_id, "step3");

    // get first domain
    getNextDomain();

    $("#start").click(function() {
        last_click = startExperiment();
    });

    $("#rate_1, #rate_2, #rate_3, #rate_4, #rate_5").click(function() {
    	rating = $(this).attr("id").split("_")[1];
        now = (new Date()).getTime();
        elapsed_time = now - last_click;
        last_click = now;
        domain_position = counter + 1;
        
        sendResult(rating, elapsed_time, domain_position);
    	$("#dropdown_content_domain_rating").toggle();
    });
});
