import os
import sys

import pymysql

class DbHandler:
    def __init__(self):
        self.host = os.environ["MYSQL_HOST"]
        self.user = os.environ["MYSQL_USER"]
        self.password = os.environ["MYSQL_PASSWORD"]
        self.database = os.environ["MYSQL_DATABASE"]

    def open_connection(self):
        return pymysql.connect(self.host, self.user, self.password, self.database)

    def insert_data(self, sql):
        conn = None
        try:
            conn = self.open_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql)
                conn.commit()
                cursor.close()
        finally:
            if conn is not None:
                conn.close()

    def update_data(self, sql):
        conn = None
        try:
            conn = self.open_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql)
                conn.commit()
                cursor.close()
        finally:
            if conn is not None:
                conn.close()

    def select_one_item(self, sql):
        conn = None
        try:
            conn = self.open_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchone()
                cursor.close()

                return data
        finally:
            if conn is not None:
                conn.close()

    def select_multiple_items(self, sql):
        conn = None
        try:
            conn = self.open_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchall()
                cursor.close()

                return data
        finally:
            if conn is not None:
                conn.close()

    def get_participant(self, user_id):
        sql = "SELECT * FROM test_persons WHERE user_id='" + user_id + "'"
        
        return self.select_one_item(sql)

    def is_step_finished(self, user_id, column_name):
        sql = "SELECT * FROM test_persons WHERE user_id='" + user_id + "' AND " + column_name + "='1'"
        
        return self.select_one_item(sql)

    def get_time(self, user_id, time_type):
        sql = "SELECT " + time_type + " FROM test_persons WHERE user_id='" + user_id + "';"

        return self.select_one_item(sql)

    def log_time(self, user_id, time_type, time):
        sql = "UPDATE test_persons SET " + time_type + " = " + str(time) + " WHERE user_id='" + user_id + "';"
        self.update_data(sql)

    def set_step_as_finished(self, user_id, column_name):
        sql = "UPDATE test_persons SET " + column_name + " = True WHERE user_id='" + user_id + "';"
        self.update_data(sql)

    def is_mobile_user(self, user_id):
        sql = "SELECT * FROM test_persons WHERE user_id='" + user_id + "' AND is_mobile = '1'"

        return self.select_one_item(sql)

    def create_test_person(self, user_id, completion_code, browser, version, os, is_mobile):
        sql = "INSERT INTO test_persons (user_id, completion_code, os, browser, version, is_mobile, finished_step1,\
                                         finished_step2, finished_step3, finished_step4, finished_step5, finished_questionnaire,\
                                         experiment_start_time, experiment_end_time, step1_start_time, step1_end_time,\
                                         step2_start_time, step2_end_time, step3_start_time, step3_end_time,\
                                         step4_start_time, step4_end_time, step5_start_time, step5_end_time,\
                                         questionnaire_start_time, questionnaire_end_time, feedback)\
               VALUES\
                    ('" + user_id + "', '" + completion_code + "','" + os + "','" + browser + "','" + version + "'," + str(is_mobile) +\
                      ", False, False, False, False, False, False, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '');"
        self.insert_data(sql)

    def get_legitimate_domains(self, number_of_domains):
        sql = "SELECT * FROM test_domains WHERE classification=False ORDER BY RAND() LIMIT " + str(number_of_domains) + ";"

        return self.select_multiple_items(sql)

    def get_ref_domain(self):
        sql = "SELECT * FROM reference_domains ORDER BY RAND() LIMIT 1;"

        return self.select_one_item(sql)

    def get_all_test_domains(self):
        sql = "SELECT domain FROM test_domains;"

        return self.select_multiple_items(sql)

    def get_all_ref_domains(self):
        sql = "SELECT domain from reference_domains;"

        return self.select_multiple_items(sql)

    def get_already_created_domains(self, step_id, user_id):
        sql = "SELECT domain FROM " + step_id + " WHERE test_person_id=\
               (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "');"

        return self.select_multiple_items(sql)

    def get_count(self, step_id, user_id):
        sql = "SELECT COUNT(*) as count FROM " + step_id + " WHERE test_person_id=\
               (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "');"
        
        return self.select_one_item(sql)

    def check_duplicated_domain(self, step_id, user_id, created_domain):
        sql = "SELECT * FROM " + step_id + " WHERE test_person_id=\
               (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')\
               AND domain='" + created_domain + "';"

        return self.select_one_item(sql)

    def get_already_created_domains_step1(self, user_id):
        sql = "SELECT created_domains.domain FROM created_domains, step1 WHERE step1.test_person_id=\
               (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "') AND\
               created_domains.created_domain_id = step1.created_domain_id;"

        return self.select_multiple_items(sql)

    def check_duplicated_domain_step1(self, user_id, created_domain):
        sql = "SELECT created_domains.domain FROM created_domains, step1 WHERE\
               step1.test_person_id = (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "') AND\
               created_domains.domain = '" + created_domain + "' AND\
               created_domains.created_domain_id = step1.created_domain_id;"

        return self.select_one_item(sql)

    def is_domain_created(self, created_domain):
        sql = "SELECT * FROM created_domains WHERE domain = '" + created_domain + "';"

        return self.select_one_item(sql)

    def insert_into_created_domains(self, ref_domain, created_domain):
        sql = "INSERT INTO created_domains (reference_domain_id, domain, number_of_ratings) VALUES\
               ((SELECT reference_domain_id FROM reference_domains WHERE domain='" + ref_domain + "')," +\
               "'" + created_domain + "',0);"
        self.insert_data(sql)

    def insert_into_step1(self, user_id, created_domain, elapsed_time, domain_position):
        sql = "INSERT INTO step1 (test_person_id, created_domain_id, elapsed_time, domain_position) VALUES\
               ((SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "'),\
                (SELECT created_domain_id FROM created_domains WHERE domain='" + created_domain + "')," +\
                elapsed_time + "," + domain_position + ");"
        self.insert_data(sql)

    def get_all_step1_domains(self):
        sql = "SELECT domain FROM created_domains;"

        return self.select_multiple_items(sql)

    def get_step1_domains_for_step5(self, user_id, number_of_domains):
        sql = "SELECT domain FROM created_domains\
               WHERE domain != 'no_participation' AND\
                     created_domain_id NOT IN (SELECT created_domain_id FROM step1\
                                               WHERE test_person_id = (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "'))\
               ORDER BY RAND() LIMIT " + str(number_of_domains) + ";"

        return self.select_multiple_items(sql)

    def insert_into_step2(self, user_id, ref_domain, squatting_technique, squatting_technique_infos, created_domain, elapsed_time, domain_position, squatting_techniques_order):
        sql = "INSERT INTO step2 (test_person_id, reference_domain_id, squatting_technique, squatting_technique_infos, domain, elapsed_time, domain_position, squatting_techniques_order) VALUES\
               ((SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "'),\
                (SELECT reference_domain_id FROM reference_domains WHERE domain='" + ref_domain + "')," +\
                "'" + squatting_technique + "'," +\
                "'" + squatting_technique_infos + "'," +\
                "'" + created_domain + "'," +\
                elapsed_time + "," +\
                domain_position + "," +\
                "'" + squatting_techniques_order + "');"
        self.insert_data(sql)

    def get_all_step2_domains(self):
        sql = "SELECT domain FROM step2;"

        return self.select_multiple_items(sql)

    def get_step3_rated_domains_count(self, user_id):
        sql = "SELECT COUNT(*) as count FROM step3_step1_created_domains WHERE test_person_id=\
               (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')"
        step1_created_domains_count = self.select_one_item(sql)[0]

        sql = "SELECT COUNT(*) as count FROM step3_ref_domains WHERE test_person_id=\
               (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')"
        step3_ref_domains_count = self.select_one_item(sql)[0]

        sql = "SELECT COUNT(*) as count FROM step3_phishing_domains WHERE test_person_id=\
               (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')"
        step3_phishing_domains_count = self.select_one_item(sql)[0]

        return step1_created_domains_count + step3_ref_domains_count + step3_phishing_domains_count

    def get_step1_domain(self, user_id, rating_threshold):
        sql = "SELECT * FROM created_domains WHERE\
                   domain != 'no_participation' AND\
                   number_of_ratings < '" + str(rating_threshold) + "' AND\
                   created_domain_id NOT IN (SELECT created_domain_id FROM step1 WHERE\
                                             test_person_id = (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')) AND\
                   created_domain_id NOT IN (SELECT created_domain_id FROM step3_step1_created_domains\
                                             WHERE test_person_id = (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "'))\
               ORDER BY RAND() LIMIT 1;"
        step1_domain = self.select_one_item(sql)

        if step1_domain is None:
            sql = "SELECT * FROM created_domains WHERE\
                       domain != 'no_participation' AND\
                       created_domain_id NOT IN (SELECT created_domain_id FROM step1 WHERE\
                                                 test_person_id = (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')) AND\
                       created_domain_id NOT IN (SELECT created_domain_id FROM step3_step1_created_domains\
                                                 WHERE test_person_id=(SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "'))\
                   ORDER BY RAND() LIMIT 1;"
            step1_domain = self.select_one_item(sql)

        return step1_domain

    def get_step2_domain(self, user_id):
        sql = "SELECT * FROM step2 WHERE\
                   step2.test_person_id != (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')\
                   AND domain NOT IN (SELECT domain FROM step3\
                                        WHERE step2.test_person_id=(SELECT test_person_id FROM test_persons\
                                                                    WHERE user_id='" + user_id + "')\
                                       )\
               ORDER BY RAND() LIMIT 1;"

        return self.select_one_item(sql)

    def get_ref_domain_step3(self, user_id):
        sql = "SELECT * FROM reference_domains WHERE reference_domains.reference_domain_id NOT IN\
                  (SELECT reference_domain_id FROM step3_ref_domains WHERE test_person_id=\
                     (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')\
                  )\
               ORDER BY RAND() LIMIT 1;"

        return self.select_one_item(sql)

    def get_phishing_domain(self, user_id):
        sql = "SELECT * FROM test_domains WHERE classification=1 AND test_domains.test_domain_id NOT IN\
                  (SELECT test_domain_id FROM step3_phishing_domains WHERE test_person_id=\
                     (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')\
                  )\
               ORDER BY RAND() LIMIT 1;"

        return self.select_one_item(sql)

    def insert_into_step3(self, user_id, rated_domain, type, elapsed_time, rating, domain_position):
        if type == "step1":
            # insert data into step3 table
            sql = "INSERT INTO step3_step1_created_domains (test_person_id, created_domain_id, elapsed_time, rating, domain_position) VALUES (\
                   (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "'), +\
                   (SELECT created_domain_id FROM created_domains WHERE domain ='" + rated_domain + "'), +\
                   '" + elapsed_time + "','" + rating + "','" + domain_position + "');"
            self.insert_data(sql)

            # update rating counter in created_domains table
            sql = "UPDATE created_domains SET number_of_ratings = number_of_ratings + 1 WHERE domain = '" + rated_domain + "';"
            self.insert_data(sql)
        elif type == "ref_domain":
            # insert data into step3 table
            sql = "INSERT INTO step3_ref_domains (test_person_id, reference_domain_id, elapsed_time, rating, domain_position) VALUES (\
                   (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "'), +\
                   (SELECT reference_domain_id FROM reference_domains WHERE domain ='" + rated_domain + "'), +\
                   '" + elapsed_time + "','" + rating + "','" + domain_position + "');"
            self.insert_data(sql)
        elif type == "phishing_domain":
            # insert data into step3 table
            sql = "INSERT INTO step3_phishing_domains (test_person_id, test_domain_id, elapsed_time, rating, domain_position) VALUES (\
                   (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "'), +\
                   (SELECT test_domain_id FROM test_domains WHERE domain ='" + rated_domain + "'), +\
                   '" + elapsed_time + "','" + rating + "','" + domain_position + "');"
            self.insert_data(sql)

    def insert_into_step4(self, user_id, created_domain, elapsed_time, domain_position):
        sql = "INSERT INTO step4 (test_person_id, domain, elapsed_time, domain_position) VALUES\
               ((SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')," +\
                "'" + created_domain + "'," +\
                elapsed_time + "," + domain_position + ");"
        self.insert_data(sql)

    def get_phishing_domains(self, number_of_domains):
        sql = "SELECT domain FROM test_domains WHERE classification=1 ORDER BY RAND() LIMIT " + str(number_of_domains) + ";"

        return self.select_multiple_items(sql)

    def insert_into_step5(self, user_id, selected_domains, elapsed_time, counter):
        step5_domain_query = "(SELECT step5_domain_id FROM step5_domains WHERE\
                               step5_domains.test_person_id=(SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "') AND\
                               step5_domains.domain_position=<position> AND\
                               step5_domains.counter=" + counter +")"

        position = 1
        for selected_domain in selected_domains.split(";"):
            splitted_selection = selected_domain.split(",")

            # create new entry in step5_domains
            sql = "INSERT INTO step5_domains(test_person_id, selected, domain_position, counter) VALUES\
                   ((SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')," +\
                   "'" + splitted_selection[1] + "'," +\
                   str(position) + "," +\
                   counter + ");"
            self.insert_data(sql)

            # insert domain in step5 domain tables depending on type
            if splitted_selection[3] == "step1_domain":
                sql = "INSERT INTO step5_step1_created_domains(step5_domain_id, created_domain_id) VALUES\
                       ( LAST_INSERT_ID(),\
                        (SELECT created_domain_id FROM created_domains WHERE domain ='" + splitted_selection[0] + "'));"
                self.insert_data(sql)
            elif splitted_selection[3] == "legitimate_domain":
                sql = "INSERT INTO step5_legitimate_domains(step5_domain_id, test_domain_id) VALUES\
                       (LAST_INSERT_ID(),\
                        (SELECT test_domain_id FROM test_domains WHERE domain ='" + splitted_selection[0] + "'));"
                self.insert_data(sql)
            elif splitted_selection[3] == "phishing_domain":
                sql = "INSERT INTO step5_phishing_domains(step5_domain_id, test_domain_id) VALUES\
                       (LAST_INSERT_ID(),\
                        (SELECT test_domain_id FROM test_domains WHERE domain ='" + splitted_selection[0] + "'));"
                self.insert_data(sql)

            position += 1

        # insert results into step5 table
        sql = "INSERT INTO step5 (test_person_id, domain1, domain2, domain3, domain4, domain5,\
                                  domain6, domain7, domain8, domain9, domain10, elapsed_time, counter) VALUES\
               ((SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')," +\
                step5_domain_query.replace("<position>", "1") + "," +\
                step5_domain_query.replace("<position>", "2") + "," +\
                step5_domain_query.replace("<position>", "3") + "," +\
                step5_domain_query.replace("<position>", "4") + "," +\
                step5_domain_query.replace("<position>", "5") + "," +\
                step5_domain_query.replace("<position>", "6") + "," +\
                step5_domain_query.replace("<position>", "7") + "," +\
                step5_domain_query.replace("<position>", "8") + "," +\
                step5_domain_query.replace("<position>", "9") + "," +\
                step5_domain_query.replace("<position>", "10") + "," +\
                elapsed_time + "," +\
                counter + ");"
        self.insert_data(sql)

    def check_questionnaire_inserted(self, user_id):
        sql = "SELECT COUNT(*) as count FROM questionnaire WHERE test_person_id=\
               (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "');"

        return self.select_one_item(sql)

    def get_countries(self):
        sql = "SELECT country FROM countries;"

        return self.select_multiple_items(sql)

    def insert_into_questionnaire(self, user_id, age, gender_current, education, origin,\
                                  f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16, attention_test1, attention_test2):
        sql = "INSERT INTO questionnaire (test_person_id, age, gender_current, education, origin_id, f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16, attention_test1, attention_test2)\
               VALUES (\
               (SELECT test_person_id FROM test_persons WHERE user_id='" + user_id + "')," +\
                "'" + age + "','" + gender_current + "','" + education + "'," +\
                "(SELECT country_id FROM countries WHERE country='" + origin + "')," +\
                "'" + f1 + "','" + f2 + "','" + f3 + "','" + f4 + "','" + f5 + "','" + f6 + "','" + f7 + "','" +\
                f8 + "','" + f9 + "','" + f10 + "','" + f11 + "','" + f12 + "','" + f13 + "','" +\
                f14 + "','" + f15 + "','" + f16 + "','" + attention_test1 + "','" + attention_test2 + "');"
        self.insert_data(sql)

    def get_completion_code(self, user_id):
        sql = "SELECT * FROM test_persons WHERE user_id='" + user_id + "';"

        return self.select_one_item(sql)

    def insert_feedback(self, user_id, feedback):
        sql = "UPDATE test_persons SET feedback = '" + feedback + "' WHERE user_id='" + user_id + "';"
        self.update_data(sql)
