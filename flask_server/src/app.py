import json
import random
import re
import uuid

from flask import Flask, jsonify, redirect, render_template, request, url_for
from user_agents import parse

# init random number generator
random.seed()

app = Flask(__name__)
# app.logger.error("test")

from db_handler import DbHandler

db = DbHandler()

from input_validator import InputValidator

input_validator = InputValidator()

domain_duplicated_error = "You already created this domain or the created domain is the same as the well-known domain. Create a different one!"


@app.route(
    "/is_step_finished/user_id/<uuid:user_id>/step_id/<any('step1', 'step2', 'step3', 'step4', 'step5', 'questionnaire'):step_id>"
)
def is_step_finished(user_id, step_id):
    user_id = str(user_id)
    input_validation = input_validator.check_input_user_id(user_id)
    if input_validation["result"] is False:
        return jsonify({
            "server_error": True,
            "server_error_message": input_validation["message"]
        })
    column_name = "finished_" + step_id
    data = db.is_step_finished(user_id, column_name)

    # None means the step has not yet been finished
    if data is None:
        return jsonify({"is_step_finished": False, "server_error": False})
    else:
        return jsonify({"is_step_finished": True, "server_error": False})

@app.route("/log_time", methods=["POST"])
def log_time():
    user_id = request.form["user_id"]
    time_type = request.form["type"]
    time = request.form["time"]

    input_validation = input_validator.check_log_time(user_id, time_type, time)
    if input_validation["result"] is False:
        return jsonify({
            "server_error": True,
            "server_error_message": input_validation["message"]
        })
    # check if time has already been logged
    data = db.get_time(user_id, time_type)
    if data[0] == "0":
        db.log_time(user_id, time_type, time)

    return jsonify({"server_error": False})

@app.route("/set_step_finished", methods=["POST"])
def set_step_finished():
    user_id = request.form["user_id"]
    step_id = request.form["step_id"]
    input_validation = input_validator.check_input_set_step_finished(
        user_id, step_id)
    if input_validation["result"] is False:
        return jsonify({
            "server_error": True,
            "server_error_message": input_validation["message"]
        })
    db.set_step_as_finished(user_id, "finished_" + step_id)

    return jsonify({"finished_step": True, "server_error": False})

@app.route("/is_mobile_user/user_id/<uuid:user_id>")
def is_mobile_user(user_id):
    user_id = str(user_id)
    input_validation = input_validator.check_input_user_id(user_id)
    if input_validation["result"] is False:
        return render_template("bad_request.html")

    data = db.is_mobile_user(user_id)

    # None means the user is not a mobile user
    if data is None:
        return jsonify({"is_mobile_user": False})
    else:
        return jsonify({"is_mobile_user": True})

# request handling for steps

@app.route("/")
def index():
    user_id = str(uuid.uuid4())
    completion_code = str(uuid.uuid4())
    user_agent = parse(request.user_agent.string)
    browser = user_agent.browser.family
    version = user_agent.browser.version_string
    os = user_agent.os.family + " " + user_agent.os.version_string
    is_mobile = user_agent.is_mobile

    db.create_test_person(user_id, completion_code, browser, version, os,
                          is_mobile)

    return render_template("index.html", user_id=user_id)

@app.route("/consent/user_id/<uuid:user_id>")
def consent(user_id):
    user_id = str(user_id)
    input_validation = input_validator.check_input_user_id(user_id)
    if input_validation["result"] is False:
        return render_template("bad_request.html")

    return render_template("consent.html", user_id=user_id)

# request handling for step 1
@app.route("/step1/user_id/<uuid:user_id>")
def step1(user_id):
    user_id = str(user_id)
    input_validation = input_validator.check_input_user_id(user_id)
    if input_validation["result"] is False:
        return render_template("bad_request.html")
    last_unfinished_step = input_validator.check_last_unfinished_step(user_id, "step1")
    if last_unfinished_step["result"] is True:
        return redirect(url_for(last_unfinished_step["current_step"], user_id=user_id))

    counter = db.get_count("step1", user_id)[0]
    already_created_domains = [
        elem[0] for elem in db.get_already_created_domains_step1(user_id)
    ]

    return render_template(
        "step1.html",
        user_id=user_id,
        next_step="step2",
        counter=counter,
        already_created_domains=already_created_domains)


@app.route("/step1/get_ref_domain")
def step1_get_ref_domain():
    data = db.get_ref_domain()

    return jsonify({"ref_domain": data[1]})


@app.route("/step1/result", methods=["POST"])
def step1_result():
    user_id = request.form["user_id"]
    ref_domain = request.form["reference_domain"]
    created_domain = request.form["created_domain"]
    elapsed_time = request.form["elapsed_time"]
    domain_position = request.form["domain_position"]

    input_validation = input_validator.check_input_step1_result(
        user_id, ref_domain, created_domain, elapsed_time, domain_position)
    if input_validation["result"] is False:
        return jsonify({
            "server_error": True,
            "server_error_message": input_validation["message"]
        })

    data = db.check_duplicated_domain_step1(user_id, created_domain)
    if data is None:
        is_domain_created = db.is_domain_created(created_domain)
        if is_domain_created is None:
            # domain has not been created before
            db.insert_into_created_domains(ref_domain, created_domain)
        db.insert_into_step1(user_id, created_domain, elapsed_time, domain_position)
        return jsonify({"server_error": False})
    else:
        return jsonify({
            "server_error": True,
            "server_error_message": domain_duplicated_error
        })


# request handling for step 2


@app.route("/step2/user_id/<uuid:user_id>")
def step2(user_id):
    user_id = str(user_id)
    input_validation = input_validator.check_input_user_id(user_id)
    if input_validation["result"] is False:
        return render_template("bad_request.html")
    last_unfinished_step = input_validator.check_last_unfinished_step(user_id, "step2")
    if last_unfinished_step["result"] is True:
        return redirect(url_for(last_unfinished_step["current_step"], user_id=user_id))
    counter = db.get_count("step2", user_id)[0]
    already_created_domains = [
        elem[0] for elem in db.get_already_created_domains("step2", user_id)
    ]

    return render_template(
        "step2.html",
        user_id=user_id,
        next_step="step3",
        counter=counter,
        already_created_domains=already_created_domains)


@app.route("/step2/get_ref_domain")
def step2_get_ref_domain():
    data = db.get_ref_domain()

    return jsonify({"ref_domain": data[1]})


@app.route("/step2/result", methods=["POST"])
def step2_result():
    user_id = request.form["user_id"]
    ref_domain = request.form["reference_domain"]
    squatting_technique = request.form["squatting_technique"]
    squatting_technique_infos = request.form["squatting_technique_infos"]
    created_domain = request.form["created_domain"]
    elapsed_time = request.form["elapsed_time"]
    domain_position = request.form["domain_position"]
    squatting_techniques_order = request.form["squatting_techniques_order"]

    input_validation = input_validator.check_input_step2_result(user_id, ref_domain, squatting_technique,\
                                                                squatting_technique_infos, created_domain,\
                                                                elapsed_time, domain_position,\
                                                                squatting_techniques_order)
    if input_validation["result"] is False:
        return jsonify({
            "server_error": True,
            "server_error_message": input_validation["message"]
        })

    data = db.check_duplicated_domain("step2", user_id, created_domain)
    # None means the same domain has not been already created by this user
    if data is None:
        db.insert_into_step2(user_id, ref_domain, squatting_technique,\
                             squatting_technique_infos, created_domain,\
                             elapsed_time, domain_position,\
                             squatting_techniques_order)
        return jsonify({"server_error": False})
    else:
        return jsonify({
            "server_error": True,
            "server_error_message": domain_duplicated_error
        })


# request handling for step 3


@app.route("/step3/user_id/<uuid:user_id>")
def step3(user_id):
    user_id = str(user_id)
    input_validation = input_validator.check_input_user_id(user_id)
    if input_validation["result"] is False:
        return render_template("bad_request.html")
    last_unfinished_step = input_validator.check_last_unfinished_step(user_id, "step3")
    if last_unfinished_step["result"] is True:
        return redirect(url_for(last_unfinished_step["current_step"], user_id=user_id))

    return render_template("step3.html", user_id=user_id, next_step="step4")


@app.route("/step3/next_domain/user_id/<uuid:user_id>")
def step3_next_domain(user_id):
    user_id = str(user_id)
    input_validation = input_validator.check_input_user_id(user_id)
    if input_validation["result"] is False:
        return jsonify({
            "server_error": True,
            "server_error_message": input_validation["message"]
        })
    data = {"domains_available": True}

    rated_domains_count = db.get_step3_rated_domains_count(user_id)
    step1_domain = db.get_step1_domain(user_id, 5)
    ref_domain = db.get_ref_domain_step3(user_id)
    phishing_domain = db.get_phishing_domain(user_id)

    if step1_domain is None and ref_domain is None and phishing_domain is None:
        # we have more phishing domains available than users are supposed to rate
        # so that this is rather a backup plan if something goes wrong
        data["domains_available"] = False
    else:
        data["count"] = rated_domains_count
        data["server_error"] = False
        random_number = random.randrange(10)
        if random_number > 1 and random_number <= 6 and step1_domain is not None:
            data["next_domain"] = step1_domain[2]
            data["id"] = step1_domain[0]
            data["type"] = "step1"
        elif random_number > 6 and random_number <= 8 and ref_domain is not None:
            data["next_domain"] = ref_domain[1]
            data["id"] = ref_domain[0]
            data["type"] = "ref_domain"
        else:
            data["next_domain"] = phishing_domain[1]
            data["id"] = phishing_domain[0]
            data["type"] = "phishing_domain"

    return jsonify(data)


@app.route("/step3/result", methods=["POST"])
def step3_result():
    user_id = request.form["user_id"]
    rated_domain = request.form["rated_domain"]
    type = request.form["type"]
    elapsed_time = request.form["elapsed_time"]
    rating = request.form["rating"]
    domain_position = request.form["domain_position"]

    input_validation = input_validator.check_input_step3_result(
        user_id, rated_domain, type, elapsed_time, rating, domain_position)
    if input_validation["result"] is False:
        return jsonify({
            "server_error": True,
            "server_error_message": input_validation["message"]
        })

    db.insert_into_step3(user_id, rated_domain, type, elapsed_time, rating, domain_position)

    return jsonify({"finished_step": True, "server_error": False})


# request handling for step 4
@app.route("/step4/user_id/<uuid:user_id>")
def step4(user_id):
    user_id = str(user_id)
    input_validation = input_validator.check_input_user_id(user_id)
    if input_validation["result"] is False:
        return render_template("bad_request.html")
    last_unfinished_step = input_validator.check_last_unfinished_step(user_id, "step4")
    if last_unfinished_step["result"] is True:
        return redirect(url_for(last_unfinished_step["current_step"], user_id=user_id))
    counter = db.get_count("step4", user_id)[0]
    already_created_domains = [
        elem[0] for elem in db.get_already_created_domains("step4", user_id)
    ]

    return render_template(
        "step4.html",
        user_id=user_id,
        next_step="step5",
        counter=counter,
        already_created_domains=already_created_domains)


@app.route("/step4/result", methods=["POST"])
def step4_result():
    user_id = request.form["user_id"]
    created_domain = request.form["created_domain"]
    elapsed_time = request.form["elapsed_time"]
    domain_position = request.form["domain_position"]

    input_validation = input_validator.check_input_step4_result(
        user_id, created_domain, elapsed_time, domain_position)
    if input_validation["result"] is False:
        return jsonify({
            "server_error": True,
            "server_error_message": input_validation["message"]
        })

    data = db.check_duplicated_domain("step4", user_id, created_domain)
    if data is None:
        db.insert_into_step4(user_id, created_domain, elapsed_time, domain_position)
        return jsonify({"server_error": False})
    else:
        return jsonify({
            "server_error": True,
            "server_error_message": domain_duplicated_error
        })


# request handling for step 5
@app.route("/step5/user_id/<uuid:user_id>")
def step5(user_id):
    user_id = str(user_id)
    input_validation = input_validator.check_input_user_id(user_id)
    if input_validation["result"] is False:
        return render_template("bad_request.html")
    last_unfinished_step = input_validator.check_last_unfinished_step(user_id, "step5")
    if last_unfinished_step["result"] is True:
        return redirect(url_for(last_unfinished_step["current_step"], user_id=user_id))

    counter = db.get_count("step5", user_id)[0]

    number_of_legit_domains = random.randrange(3) + 1
    domains = []

    # select legitimate domains
    for domain in db.get_legitimate_domains(number_of_legit_domains):
        domains.append((domain[1], "legitimate", "legitimate_domain"))

    # select domains from step 1
    for domain in db.get_step1_domains_for_step5(user_id,
                                                 10 - number_of_legit_domains):
        domains.append((domain[0], "not_legitimate", "step1_domain"))

    if len(domains) < 10:
        # select phishtank domains if not enough domains from step 1
        number_of_domains = 10 - len(domains)
        for domain in db.get_phishing_domains(number_of_domains):
            domains.append((domain[0], "not_legitimate", "phishing_domain"))

    # randomize order of domains so that legitimate domains are not always displayed first
    random.shuffle(domains)

    return render_template(
        "step5.html",
        user_id=user_id,
        next_step="questionnaire",
        counter=counter,
        domains=domains)


@app.route("/step5/result", methods=["POST"])
def step5_result():
    user_id = request.form["user_id"]
    selected_domains = request.form["selected_domains"]
    elapsed_time = request.form["elapsed_time"]
    counter = request.form["counter"]

    input_validation = input_validator.check_input_step5_result(
        user_id, selected_domains, elapsed_time, counter)
    if input_validation["result"] is False:
        return jsonify({
            "server_error": True,
            "server_error_message": input_validation["message"]
        })

    db.insert_into_step5(user_id, selected_domains, elapsed_time, counter)
    return jsonify({"inserted": True, "server_error": False})

# request handling for questionnaire


@app.route("/questionnaire/user_id/<uuid:user_id>")
def questionnaire(user_id):
    user_id = str(user_id)
    input_validation = input_validator.check_input_user_id(user_id)
    if input_validation["result"] is False:
        return render_template("bad_request.html")
    last_unfinished_step = input_validator.check_last_unfinished_step(user_id, "questionnaire")
    if last_unfinished_step["result"] is True:
        return redirect(url_for(last_unfinished_step["current_step"], user_id=user_id))

    countries = [elem[0] for elem in db.get_countries()]

    return render_template("questionnaire.html", user_id=user_id, countries=countries)


@app.route("/questionnaire/results", methods=["POST"])
def questionnaire_results():
    user_id = request.form["user_id"]
    age = request.form["age"]
    gender_current = request.form["gender_current"]
    education = request.form["education"]
    origin = request.form["origin"]
    f1 = request.form["f1"]
    f2 = request.form["f2"]
    f3 = request.form["f3"]
    f4 = request.form["f4"]
    f5 = request.form["f5"]
    f6 = request.form["f6"]
    f7 = request.form["f7"]
    f8 = request.form["f8"]
    f9 = request.form["f9"]
    f10 = request.form["f10"]
    f11 = request.form["f11"]
    f12 = request.form["f12"]
    f13 = request.form["f13"]
    f14 = request.form["f14"]
    f15 = request.form["f15"]
    f16 = request.form["f16"]
    attention_test1 = request.form["attention_test1"]
    attention_test2 = request.form["attention_test2"]

    input_validation = input_validator.check_input_questionnaire_result(user_id, age,\
                                         gender_current, education, origin,\
                                         f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12,\
                                         f13, f14, f15, f16,\
                                         attention_test1, attention_test2)
    if input_validation["result"] is False:
        return jsonify({
            "server_error": True,
            "server_error_message": input_validation["message"]
        })

    response = {"already_inserted": False, "server_error": False}
    questionnaire_inserted_count = db.check_questionnaire_inserted(user_id)[0]
    if questionnaire_inserted_count > 0:
        response["already_inserted"] = True
    else:
        db.insert_into_questionnaire(user_id, age, gender_current, education, origin,\
                                     f1, f2, f3, f4, f5, f6, f7, f8, f9, f10,\
                                     f11, f12, f13, f14, f15, f16,\
                                     attention_test1, attention_test2)
        db.set_step_as_finished(user_id, "finished_questionnaire")

    return jsonify(response)


# request handling for final notes


@app.route("/final_notes/user_id/<uuid:user_id>")
def final_notes(user_id):
    user_id = str(user_id)
    input_validation = input_validator.check_input_user_id(user_id)
    if input_validation["result"] is False:
        return render_template("bad_request.html")
    last_unfinished_step = input_validator.check_last_unfinished_step(user_id, "final_notes")
    if last_unfinished_step["result"] is True:
        return redirect(url_for(last_unfinished_step["current_step"], user_id=user_id))
    data = db.get_completion_code(user_id)

    completion_code = "-1"
    # set completion code to actual value if all five steps and the questionnaire have been finished
    if data[7] == 1 and data[8] == 1 and data[9] == 1 and data[
            10] == 1 and data[11] == 1 and data[12] == 1:
        completion_code = data[2]
    has_provided_feedback = data[27] != ""

    return render_template("final_notes.html", user_id=user_id, finished_step1=str(data[7]), finished_step2=str(data[8]),\
                           finished_step3=str(data[9]), finished_step4=str(data[10]), finished_step5=str(data[11]),\
                           finished_questionnaire=str(data[12]), completion_code=completion_code,\
                           has_provided_feedback=has_provided_feedback)

@app.route("/final_notes/feedback", methods=["POST"])
def final_notes_feedback():
    user_id = request.form["user_id"]
    feedback = request.form["feedback"]

    input_validation = input_validator.check_input_final_notes_feedback(user_id, feedback)
    if input_validation["result"] is False:
        return jsonify({
            "server_error": True,
            "server_error_message": input_validation["message"]
        })

    db.insert_feedback(user_id, feedback)

    return jsonify({
            "server_error": False
        })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
