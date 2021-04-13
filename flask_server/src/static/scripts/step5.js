$(document).ready(function() {
    var user_id = $("div#user_id").text();
    var last_click;

    var send_result = function(user_id, selected_domains, elapsed_time, counter) {
        $.ajax({
            "type": "POST",
            "url": "/step5/result",
            "data": {"user_id": user_id,
                     "selected_domains": selected_domains,
                     "elapsed_time": elapsed_time,
                     "counter": counter},
            "success": function(data) {
                if (data["server_error"] == true) {
                    $("#server_error_message").html(data["server_error_message"]);
                    $("#server_error").css("display", "block");
                } else {            
                    if (data["inserted"] == true) {
                        // link to same page
                        window.location.href = "/step5/user_id/" + user_id;
                    }
                }
            }
        });
    }

    is_step_finished(user_id, "step5");

    counter = parseInt($("#counter").html());
    if (counter == 10) {
        finish(user_id, "step5");
    } else {
        $("#start").css("display", "inline-block");
    }

    $("#start").click(function() {
        last_click = startExperiment();
    });

    $("#experiment > .label").click(function() {
        if ($(this).hasClass("selected")) {
            $(this).removeClass("selected");
            $(this).css("text-decoration", "none");
        } else {
            $(this).addClass("selected");
            $(this).css("text-decoration", "underline");
        }
    });

    $("#send_domains").click(function() {
        now = (new Date()).getTime();
        elapsed_time = now - last_click;
        last_click = now;

        selected_domains = []
        selected_counter = 0
        $("#experiment").find(".label").each(function(index) {
            selected = "False";
            if ($(this).attr("class").includes("selected")) {
                selected = "True";
                selected_counter++;
            }
            legitimate = "True";
            if ($(this).attr("class").includes("not_legitimate")) {
                legitimate = "False";
            }
            type = "legitimate_domain";
            if ($(this).attr("class").includes("step1_domain")) {
                type = "step1_domain";
            } else if ($(this).attr("class").includes("phishing_domain")) {
                type = "phishing_domain";
            }
            selected_domains.push($(this).html() + "," + selected + "," + legitimate + "," + type)
        });

        counter = parseInt($("#counter").html()) + 1;
        send_result(user_id, selected_domains.join(";"), elapsed_time, counter);
    });
});
