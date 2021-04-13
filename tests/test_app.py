import json
import unittest

from app import app
from db_handler import DbHandler

class FlaskAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # create a connection to test database
        self.db = DbHandler()
        # create a test client
        self.app = app.test_client()
        # propagate exceptions to the test client
        self.app.testing = True
        # default pre-configured user
        self.user_id = "aaa10022-38b0-4a1a-95af-776f35aa2b8f"

    def tearDown(self):
        pass

    def test_is_step_finished(self):
        for step_id in ["step1", "step2", "step3", "step4", "step5", "questionnaire"]:
            # default user who has not finished a step
            result = self.app.get("/is_step_finished/user_id/" + self.user_id + "/step_id/" + step_id)
            self.assertEqual(result.status_code, 200)
            result_data = json.loads(result.get_data(as_text=True))
            self.assertEqual(result_data["is_step_finished"], False)

            # user who has finished all steps
            result = self.app.get("/is_step_finished/user_id/a206adfb-1ff8-4c73-bdf0-fdc8ddc9df39/step_id/" + step_id)
            self.assertEqual(result.status_code, 200)
            result_data = json.loads(result.get_data(as_text=True))
            self.assertEqual(result_data["is_step_finished"], True)

    def test_set_step_finished(self):
        # test with user who has not finished a step and is not used anywhere else
        data = {"user_id": "b6ab0f21-b755-4855-b16e-e528dd0798ad", "step_id": "xxx"}
        for step_id in ["step1", "step2", "step3", "step4", "step5"]:
            data["step_id"] = step_id
            result = self.app.post("/set_step_finished", data=data)
            self.assertEqual(result.status_code, 200)
            result_data = json.loads(result.get_data(as_text=True))
            self.assertEqual(result_data["server_error"], False)
            self.assertEqual(result_data["finished_step"], True)

    def test_index(self):
        result = self.app.get("/")
        self.assertEqual(result.status_code, 200)

    def test_step1(self):
        result = self.app.get("/step1/user_id/" + self.user_id)
        self.assertEqual(result.status_code, 200)

    def test_step1_get_ref_domain(self):
        result = self.app.get("/step1/get_ref_domain")
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertIsInstance(result_data["ref_domain"], str)

    def test_step1_result(self):
        data = {"user_id": self.user_id, "reference_domain": "google.com",\
                "created_domain": "gogle.com", "elapsed_time": 1000,\
                "domain_position": 1}
        result = self.app.post("/step1/result", data=data)
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_data["server_error"], False)

        # try to insert the same domain again and expect domain duplicated error
        result = self.app.post("/step1/result", data=data)
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_data["server_error"], True)

    def test_step2(self):
        result = self.app.get("/step2/user_id/" + self.user_id)
        self.assertEqual(result.status_code, 200)

    def test_step2_get_ref_domain(self):
        result = self.app.get("/step2/get_ref_domain")
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertIsInstance(result_data["ref_domain"], str)

    def test_step2_result(self):
        data = {"user_id": self.user_id, "reference_domain": "google.com",\
                "squatting_technique": "wrong_tld", "squatting_technique_infos": "",\
                "created_domain": "google.de", "elapsed_time": 1000,\
                "domain_position": 1,\
                "squatting_techniques_order": "wrong_tld,homograph,typosquatting,combosquatting,subdomain"}
        result = self.app.post("/step2/result", data=data)
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_data["server_error"], False)

        # try to insert the same domain again and expect domain duplicated error
        result = self.app.post("/step2/result", data=data)
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_data["server_error"], True)

    def test_step3(self):
        result = self.app.get("/step3/user_id/" + self.user_id)
        self.assertEqual(result.status_code, 200)

    def test_step3_next_domain(self):
        result = self.app.get("/step3/next_domain/user_id/" + self.user_id)
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertEqual(int(result_data["count"]), 0)
        self.assertIn(result_data["type"], ["step1", "ref_domain", "phishing_domain"])

    def test_step3_result(self):
        data = {"user_id": self.user_id, "rated_domain": "google.com",\
                "type": "ref_domain", "elapsed_time": 1000,\
                "rating": "1", "domain_position": 1}
        result = self.app.post("step3/result", data=data)
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_data["finished_step"], True)

    def test_step4(self):
        result = self.app.get("/step4/user_id/" + self.user_id)
        self.assertEqual(result.status_code, 200)

    def test_step4_result(self):
        data = {"user_id": self.user_id, "created_domain": "test.com",\
                "elapsed_time": 1000, "domain_position": 1}
        result = self.app.post("/step4/result", data=data)
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_data["server_error"], False)

        # try to insert the same domain again and expect domain duplicated error
        result = self.app.post("/step4/result", data=data)
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_data["server_error"], True)

    def test_step5(self):
        result = self.app.get("/step5/user_id/" + self.user_id)
        self.assertEqual(result.status_code, 200)

    def test_step5_result(self):
        data = {"user_id": self.user_id,\
                "selected_domains": "jpmorganchaseonlinebankingverification.typeform.com,False,False,phishing_domain;\
                                     drive.google.cnc-style.de,True,False,phishing_domain;\
                                     paypal.me,False,True,legitimate_domain;\
                                     ssl-google-com-seured.strengthgrind.com,False,False,phishing_domain;\
                                     dropboxforum.com,False,True,legitimate_domain;\
                                     www.yahoo.accountservices.ververoom.com,True,False,phishing_domain;\
                                     document-share-docusign-mess.classicalschoolathome.com,False,False,phishing_domain;\
                                     linkedin.com.marinyaki.com.au,False,False,phishing_domain;\
                                     www.instagram-verified.com,False,False,phishing_domain;\
                                     netflixptt.com,False,False,phishing_domain\
                                     ",\
                "elapsed_time": 1000,
                "counter": 1}
        result = self.app.post("/step5/result", data=data)
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_data["inserted"], True)

    def test_questionnaire(self):
        result = self.app.get("/questionnaire/user_id/" + self.user_id)
        self.assertEqual(result.status_code, 200)

    def test_questionnaire_results(self):
        data = {"user_id": self.user_id, "age": "18_25", "gender_current": "male", "education": "bachelor",\
                "origin": "Australia", "f1": "never", "f2": "never", "f3": "never", "f4": "never", "f5": "never",\
                "f6": "never",  "f7": "never", "f8": "never", "f9": "never", "f10": "never", "f11": "never",\
                "f12": "never", "f13": "never", "f14": "never", "f15": "never", "f16": "never",\
                "attention_test1": "never", "attention_test2": "never"}
        result = self.app.post("/questionnaire/results", data=data)
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_data["already_inserted"], False)

        # try to insert the questionnaire results a second time and expect already inserted error
        result = self.app.post("/questionnaire/results", data=data)
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_data["already_inserted"], True)

    def test_final_notes(self):
        result = self.app.get("/final_notes/user_id/" + self.user_id)
        self.assertEqual(result.status_code, 200)