import os
import uuid

from db_handler import DbHandler

class InputValidator:
    def __init__(self):
        self.db = DbHandler()

    # internal methods to check validity of inputs
    def _is_user_id_valid(self, user_id):
        # check if user id is a valid UUIDv4
        try:
            uuid_obj = uuid.UUID(user_id, version=4)
        except ValueError:
            return False

        # check if UUID object is the same as the input string
        if str(uuid_obj) != user_id:
            return False

        # check if we have a participant for the input user id
        data = self.db.get_participant(user_id)
        if data is None:
            return False

        return True

    def _is_ref_domain_valid(self, ref_domain):
        ref_domains = [elem[0] for elem in self.db.get_all_ref_domains()]
        if ref_domain in ref_domains:
            return True
    
        return False

    def _is_created_domain_valid(self, created_domain):
        # check if special characters are in created domain
        if any([char in created_domain for char in ["_", "<", ">", "&", "'", "\"", "=", "[", "]", "(", ")", "%", "$", "?", "#", "*", "+", "/", " ", ",", ";", ":"]]):
            return False
    
        return True

    def _is_valid_integer(self, test_string):
        try: 
            int(test_string)
            return True
        except ValueError:
            return False

    def _is_rated_domain_valid(self, rated_domain):
        test_domains = [elem[0] for elem in self.db.get_all_test_domains()]
        if rated_domain in test_domains:
            return True
    
        ref_domains = [elem[0] for elem in self.db.get_all_ref_domains()]
        if rated_domain in ref_domains:
            return True
    
        step1_domains = [elem[0] for elem in self.db.get_all_step1_domains()]
        if rated_domain in step1_domains:
            return True
    
        return False

    def check_input_user_id(self, user_id):
        if self._is_user_id_valid(user_id) is False:
            return {"result": False, "message": "Invalid user ID!"}

        return {"result": True, "message": ""}

    def check_last_unfinished_step(self, user_id, step_id):
        if os.environ["CHECK_LAST_UNFINISHED_STEP"] == "1":
            data = self.db.get_participant(user_id)
            current_step = "step1"
            if data[7] == 1:
                current_step = "step2"
            if data[8] == 1:
                current_step = "step3"
            if data[9] == 1:
                current_step = "step4"
            if data[10] == 1:
                current_step = "step5"
            if data[11] == 1:
                current_step = "questionnaire"
            if data[12] == 1:
                current_step = "final_notes"

            if current_step != step_id:
                return {"result": True, "current_step": current_step}
        else:
            return {"result": False, "current_step": "test"}

        return {"result": False, "current_step": ""}

    def check_log_time(self, user_id, time_type, time):
        valid_time_types = ["experiment_start_time", "experiment_end_time",\
                            "step1_start_time", "step1_end_time",\
                            "step2_start_time", "step2_end_time",\
                            "step3_start_time", "step3_end_time",\
                            "step4_start_time", "step4_end_time",\
                            "step5_start_time", "step5_end_time",\
                            "questionnaire_start_time", "questionnaire_end_time"]
        if self._is_user_id_valid(user_id) is False:
            return {"result": False, "message": "Invalid user ID!"}
        if time_type not in valid_time_types:
            return {"result": False, "message": "Invalid time type!"}
        if self._is_valid_integer(time) is False:
            return {"result": False, "message": "Invalid current time!"}

        return {"result": True, "message": ""}

    def check_input_set_step_finished(self, user_id, step_id):
        if self._is_user_id_valid(user_id) is False:
            return {"result": False, "message": "Invalid user ID!"}
        if step_id not in ["step1", "step2", "step3", "step4", "step5"]:
            return {"result": False, "message": "Invalid step ID!"}

        return {"result": True, "message": ""}

    def check_input_step1_result(self, user_id, ref_domain, created_domain, elapsed_time, domain_position):
        if self.db.get_count("step1", user_id)[0] >= 10:
            return {"result": False, "message": "Already created maximum number of domains!"}
        if self.db.is_step_finished(user_id, "finished_step1") is not None:
            return {"result": False, "message": "Step is already finished!"}
        if self._is_user_id_valid(user_id) is False:
            return {"result": False, "message": "Invalid user ID!"}
        if self._is_ref_domain_valid(ref_domain) is False:
            return {"result": False, "message": "Invalid reference domain!"}
        if self._is_created_domain_valid(created_domain) is False:
            return {"result": False, "message": "Invalid created domain!"}
        if self._is_valid_integer(elapsed_time) is False:
            return {"result": False, "message": "Invalid elapsed time!"}
        if self._is_valid_integer(domain_position) is False:
            return {"result": False, "message": "Invalid domain position!"}

        return {"result": True, "message": ""}

    def check_input_step2_result(self, user_id, ref_domain, squatting_technique, squatting_technique_infos,\
                                 created_domain, elapsed_time, domain_position, squatting_techniques_order):
        valid_squatting_techniques = ["wrong_tld", "homograph", "typosquatting", "combosquatting", "subdomain"]
        valid_squatting_technique_infos = ["", "prepend_www", "omit_character", "duplicate_character",\
                                           "swap_characters", "replace_qwerty", "none_before_none_behind",\
                                           "term_before_none_behind", "chars_before_none_behind",\
                                           "none_before_term_behind", "none_before_chars_behind",\
                                           "term_before_term_behind", "chars_before_chars_behind",\
                                           "chars_before_term_behind", "term_before_chars_behind"]

        if self.db.get_count("step2", user_id)[0] >= 10:
            return {"result": False, "message": "Already created maximum number of domains!"}
        if self.db.is_step_finished(user_id, "finished_step2") is not None:
            return {"result": False, "message": "Step is already finished!"}
        if self._is_user_id_valid(user_id) is False:
            return {"result": False, "message": "Invalid user ID!"}
        if self._is_ref_domain_valid(ref_domain) is False:
            return {"result": False, "message": "Invalid reference domain!"}
        if squatting_technique not in valid_squatting_techniques:
            return {"result": False, "message": "Invalid squatting technique!"}
        if squatting_technique_infos not in valid_squatting_technique_infos:
            return {"result": False, "message": "Invalid squatting technique infos!"}
        if self._is_created_domain_valid(created_domain) is False:
            return {"result": False, "message": "Invalid created domain!"}
        if self._is_valid_integer(elapsed_time) is False:
            return {"result": False, "message": "Invalid elapsed time!"}
        if self._is_valid_integer(domain_position) is False:
            return {"result": False, "message": "Invalid domain position!"}
        if set(squatting_techniques_order.split(",")) != set(valid_squatting_techniques):
            return {"result": False, "message": "Invalid order of squatting techniques!"}

        return {"result": True, "message": ""}

    def check_input_step3_result(self, user_id, rated_domain, type, elapsed_time, rating, domain_position):
        if self.db.get_step3_rated_domains_count(user_id) >= 30:
            return {"result": False, "message": "Already created maximum number of domains!"}
        if self.db.is_step_finished(user_id, "finished_step3") is not None:
            return {"result": False, "message": "Step is already finished!"}
        if self._is_user_id_valid(user_id) is False:
            return {"result": False, "message": "Invalid user ID!"}
        if self._is_rated_domain_valid(rated_domain) is False:
            return {"result": False, "message": "Invalid rated domain!"}
        if type not in ["step1", "ref_domain", "phishing_domain"]:
            return {"result": False, "message": "Invalid domain type!"}
        if self._is_valid_integer(elapsed_time) is False:
            return {"result": False, "message": "Invalid elapsed time!"}
        if rating not in ["1", "2", "3", "4", "5"]:
            return {"result": False, "message": "Invalid rating!"}
        if int(domain_position) < 1 or int(domain_position) > 30:
            return {"result": False, "message": "Invalid domain position!"}

        return {"result": True, "message": ""}

    def check_input_step4_result(self, user_id, created_domain, elapsed_time, domain_position):
        if self.db.get_count("step4", user_id)[0] >= 10:
            return {"result": False, "message": "Already created maximum number of domains!"}
        if self.db.is_step_finished(user_id, "finished_step4") is not None:
            return {"result": False, "message": "Step is already finished!"}
        if self._is_user_id_valid(user_id) is False:
            return {"result": False, "message": "Invalid user ID!"}
        if self._is_created_domain_valid(created_domain) is False:
            return {"result": False, "message": "Invalid created domain!"}
        if self._is_valid_integer(elapsed_time) is False:
            return {"result": False, "message": "Invalid elapsed time!"}
        if self._is_valid_integer(domain_position) is False:
            return {"result": False, "message": "Invalid domain position!"}

        return {"result": True, "message": ""}

    def check_input_step5_result(self, user_id, selected_domains, elapsed_time, counter):
        if self.db.get_count("step5", user_id)[0] >= 10:
            return {"result": False, "message": "Already created maximum number of domains!"}
        if self.db.is_step_finished(user_id, "finished_step5") is not None:
            return {"result": False, "message": "Step is already finished!"}
        if self._is_user_id_valid(user_id) is False:
            return {"result": False, "message": "Invalid user ID!"}
        if selected_domains.count(",") != 30 or selected_domains.count(";") != 9:
            return {"result": False, "message": "Invalid selected domains!"}
        if self._is_valid_integer(elapsed_time) is False:
            return {"result": False, "message": "Invalid elapsed time!"}
        if self._is_valid_integer(counter) is False:
            return {"result": False, "message": "Invalid counter!"}
        
        return {"result": True, "message": ""}

    def check_input_questionnaire_result(self, user_id, age, gender_current, education, origin,\
                                         f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12,\
                                         f13, f14, f15, f16, attention_test1, attention_test2):
        countries = [elem[0] for elem in self.db.get_countries()]
        if self._is_user_id_valid(user_id) is False:
            return {"result": False, "message": "Invalid user ID!"}
        if age not in ["18_25", "26_35", "36_45", "46_55", "over_55", "not_answer"]:
            return {"result": False, "message": "Invalid age!"}
        if gender_current not in ["male", "female", "non_binary", "transgender", "other", "not_answer"]:
            return {"result": False, "message": "Invalid current gender!"}
        if education not in ["less_high_school", "high_school", "associate", "no_degree",\
                             "bachelor", "master", "over_master", "not_answer"]:
            return {"result": False, "message": "Invalid education!"}
        if origin not in countries:
            return {"result": False, "message": "Invalid origin!"}
    
        sebis_valid_answers = ["never", "rarely", "sometimes", "often", "always"]
        if f1 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f1!"}
        if f2 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f2!"}
        if f3 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f3!"}
        if f4 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f4!"}
        if f5 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f5!"}
        if f6 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f6!"}
        if f7 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f7!"}
        if f8 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f8!"}
        if f9 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f9!"}
        if f10 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f10!"}
        if f11 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f11!"}
        if f12 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f12!"}
        if f13 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f13!"}
        if f14 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f14!"}
        if f15 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f15!"}
        if f16 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid f16!"}
    
        if attention_test1 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid attention 1!"}
        if attention_test2 not in sebis_valid_answers:
            return {"result": False, "message": "Invalid attention 2!"}

        return {"result": True, "message": ""}

    def check_input_final_notes_feedback(self, user_id, feedback):
        if self._is_user_id_valid(user_id) is False:
            return {"result": False, "message": "Invalid user ID!"}
        if len(feedback) > 500:
            feedback_length = len(feedback) - 500
            return {"result": False, "message": "Feedback is " + str(feedback_length) + " characters too long!"}
        if any([char in feedback for char in ["<", ">", "&", "'", "\"", "=", "(", ")", "%", "$", "?", "#", "*", "+", "/"]]):
            return {"result": False, "message": "Not allowed characters used!"}

        return {"result": True, "message": ""}