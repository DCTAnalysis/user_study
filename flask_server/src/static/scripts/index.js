$(document).ready(function() {
	var user_id = $("div#user_id").text();

	// check if user is using a mobile device and display continue link only if not
    $.ajax({
        "type": "GET",
        "url": "/is_mobile_user/user_id/" + user_id,
        "success": function(data) {
        	if (data["is_mobile_user"] == false) {
        		$("#continue_to_consent").css("display", "block");
        	} else {
        		$("#mobile_device_message").css("display", "block");
        	}
        }
    });
});
