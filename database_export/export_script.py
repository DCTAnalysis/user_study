import os
import sys

import pymysql

host = os.environ["MYSQL_HOST"]
user = os.environ["MYSQL_USER"]
password = os.environ["MYSQL_PASSWORD"]
database = os.environ["MYSQL_DATABASE"]

def execute_query(sql):
    csv_data = []
    
    conn = None
    try:
        conn = pymysql.connect(host, user, password, database)
        with conn.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
        for row in data:
            csv_data.append(",".join([str(elem).strip().replace(",", "_").replace(" ", "_").replace("\n", "_") for elem in row]))
    finally:
        if conn is not None:
            conn.close()

    return csv_data

def save_to_csv(table_name, headline, csv_data):
    with open("database_export/exported_files/" + table_name + ".csv", "w+") as f:
        f.write(headline + "\n")
        f.write("\n".join(sorted(csv_data)))

def evaluate_attention_questions():
    sql = "SELECT test_persons.user_id, attention_test1, attention_test2\
           FROM questionnaire, test_persons\
           WHERE questionnaire.test_person_id = test_persons.test_person_id"
    csv_data = execute_query(sql)
    user_id_attention_mapping = {}
    for line in csv_data:
        splitted_line = line.split(",")
        if splitted_line[1] == "never" and splitted_line[2] != "never":
            user_id_attention_mapping[splitted_line[0]] = "true"
        else:
            user_id_attention_mapping[splitted_line[0]] = "false"

    return user_id_attention_mapping

def export_test_persons():
    statistics_query = "SELECT <operator>(step3_step1_created_domains.<field>)\
                        FROM step3_step1_created_domains, step1, created_domains\
                        WHERE test_persons.test_person_id = step1.test_person_id AND\
                              step1.created_domain_id = created_domains.created_domain_id AND\
                              created_domains.created_domain_id = step3_step1_created_domains.created_domain_id"
    sql = "SELECT user_id, completion_code, os, browser, version, is_mobile, finished_step1, finished_step2,\
                  finished_step3, finished_step4, finished_step5, finished_questionnaire,\
                  (" + statistics_query.replace("<operator>", "COUNT").replace("<field>", "rating") + ") AS number_of_received_ratings,\
                  (" + statistics_query.replace("<operator>", "MIN").replace("<field>", "rating") + ") AS min_rating,\
                  (" + statistics_query.replace("<operator>", "MAX").replace("<field>", "rating") + ") AS max_rating,\
                  (" + statistics_query.replace("<operator>", "AVG").replace("<field>", "rating") + ") AS avg_rating,\
                  (" + statistics_query.replace("<operator>", "STDDEV").replace("<field>", "rating") + ") AS stddev_rating,\
                  (" + statistics_query.replace("<operator>", "MIN").replace("<field>", "elapsed_time") + ") AS min_rating_time,\
                  (" + statistics_query.replace("<operator>", "MAX").replace("<field>", "elapsed_time") + ") AS max_rating_tima,\
                  (" + statistics_query.replace("<operator>", "AVG").replace("<field>", "elapsed_time") + ") AS avg_rating_time,\
                  (" + statistics_query.replace("<operator>", "STDDEV").replace("<field>", "elapsed_time") + ") AS stddev_rating_time,\
                  feedback\
           FROM test_persons"
    csv_data = execute_query(sql)
    user_id_attention_mapping = evaluate_attention_questions()
    csv_data_copy = []
    for elem in csv_data:
        user_id = elem[:elem.index(",")]
        if user_id in user_id_attention_mapping:
            csv_data_copy.append(elem + "," + user_id_attention_mapping[user_id])
        else:
            csv_data_copy.append(elem + ",none")
    csv_data = csv_data_copy

    save_to_csv("test_persons", "user_id,completion_code,os,browser,version,is_mobile,finished_step1,finished_step2,finished_step3,finished_step4,finished_step5,finished_questionnaire,number_of_received_ratings,min_rating,max_rating,avg_rating,stddev_rating,min_rating_time,max_rating_time,avg_rating_time,stddev_rating_time,feedback,attention_success", csv_data)

def export_created_domains():
    statistics_query = "SELECT <operator>(step3_step1_created_domains.<field>)\
                        FROM step3_step1_created_domains\
                        WHERE created_domains.created_domain_id = step3_step1_created_domains.created_domain_id"
    sql = "SELECT reference_domains.domain, created_domains.domain, created_domains.number_of_ratings,\
                  (SELECT COUNT(*) FROM step1 WHERE step1.created_domain_id = created_domains.created_domain_id),\
                  (" + statistics_query.replace("<operator>", "MIN").replace("<field>", "rating") + ") AS min_rating,\
                  (" + statistics_query.replace("<operator>", "MAX").replace("<field>", "rating") + ") AS max_rating,\
                  (" + statistics_query.replace("<operator>", "AVG").replace("<field>", "rating") + ") AS avg_rating,\
                  (" + statistics_query.replace("<operator>", "STDDEV").replace("<field>", "rating") + ") AS stddev_rating,\
                  (" + statistics_query.replace("<operator>", "MIN").replace("<field>", "elapsed_time") + ") AS min_rating_time,\
                  (" + statistics_query.replace("<operator>", "MAX").replace("<field>", "elapsed_time") + ") AS max_rating_time,\
                  (" + statistics_query.replace("<operator>", "AVG").replace("<field>", "elapsed_time") + ") AS avg_rating_time,\
                  (" + statistics_query.replace("<operator>", "STDDEV").replace("<field>", "elapsed_time") + ") AS stddev_rating_time\
           FROM created_domains, reference_domains\
           WHERE created_domains.reference_domain_id = reference_domains.reference_domain_id"
    csv_data = execute_query(sql)
    save_to_csv("created_domains", "reference_domain,created_domain,number_of_ratings,number_of_creations,min_rating,max_rating,avg_rating,stddev_rating,min_rating_time,max_rating_time,avg_rating_time,stddev_rating_time", csv_data)

def export_step1():
    statistics_query = "SELECT <operator>(step3_step1_created_domains.<field>)\
                        FROM step3_step1_created_domains\
                        WHERE step1.created_domain_id = step3_step1_created_domains.created_domain_id"
    sql = "SELECT test_persons.user_id, step1.domain_position, created_domains.domain, reference_domains.domain, step1.elapsed_time, created_domains.number_of_ratings,\
                  (SELECT COUNT(*) FROM step1 WHERE step1.created_domain_id = created_domains.created_domain_id),\
                  (" + statistics_query.replace("<operator>", "MIN").replace("<field>", "rating") + ") AS min_rating,\
                  (" + statistics_query.replace("<operator>", "MAX").replace("<field>", "rating") + ") AS max_rating,\
                  (" + statistics_query.replace("<operator>", "AVG").replace("<field>", "rating") + ") AS avg_rating,\
                  (" + statistics_query.replace("<operator>", "STDDEV").replace("<field>", "rating") + ") AS stddev_rating,\
                  (" + statistics_query.replace("<operator>", "MIN").replace("<field>", "elapsed_time") + ") AS min_rating_time,\
                  (" + statistics_query.replace("<operator>", "MAX").replace("<field>", "elapsed_time") + ") AS max_rating_time,\
                  (" + statistics_query.replace("<operator>", "AVG").replace("<field>", "elapsed_time") + ") AS avg_rating_time,\
                  (" + statistics_query.replace("<operator>", "STDDEV").replace("<field>", "elapsed_time") + ") AS stddev_rating_time\
           FROM test_persons, step1, created_domains, reference_domains\
           WHERE step1.created_domain_id = created_domains.created_domain_id AND\
                 step1.test_person_id = test_persons.test_person_id AND\
                 created_domains.reference_domain_id = reference_domains.reference_domain_id"
    csv_data = execute_query(sql)
    save_to_csv("step1", "user_id,domain_position,created_domain,reference_domain,elapsed_time,number_of_ratings,number_of_creations,min_rating,max_rating,avg_rating,stddev_rating,min_rating_time,max_rating_time,avg_rating_time,stddev_rating_time", csv_data)

def export_step2():
    sql = "SELECT test_persons.user_id, step2.domain_position, step2.domain, reference_domains.domain, step2.elapsed_time, step2.squatting_technique,\
                  step2.squatting_technique_infos, step2.squatting_techniques_order\
           FROM step2, test_persons, reference_domains\
           WHERE step2.test_person_id = test_persons.test_person_id AND\
                 step2.reference_domain_id = reference_domains.reference_domain_id"
    csv_data = execute_query(sql)
    save_to_csv("step2", "user_id,domain_position,created_domain,reference_domain,elapsed_time,squatting_technique,squatting_technique_infos,squatting_techniques_order", csv_data)

def export_step3_step1_created():
    sql = "SELECT test_persons.user_id, step3_step1_created_domains.domain_position, created_domains.domain, step3_step1_created_domains.elapsed_time, step3_step1_created_domains.rating\
           FROM step3_step1_created_domains, test_persons, created_domains\
           WHERE step3_step1_created_domains.test_person_id = test_persons.test_person_id AND\
                 step3_step1_created_domains.created_domain_id = created_domains.created_domain_id"
    csv_data = execute_query(sql)
    csv_data = [elem + ",step1_created" for elem in csv_data]

    return csv_data

def export_step3_ref_domains():
    sql = "SELECT test_persons.user_id, step3_ref_domains.domain_position, reference_domains.domain, step3_ref_domains.elapsed_time, step3_ref_domains.rating\
           FROM step3_ref_domains, test_persons, reference_domains\
           WHERE step3_ref_domains.test_person_id = test_persons.test_person_id AND\
                 step3_ref_domains.reference_domain_id = reference_domains.reference_domain_id"
    csv_data = execute_query(sql)
    csv_data = [elem + ",reference_domain" for elem in csv_data]

    return csv_data

def export_step3_phishing_domains():
    sql = "SELECT test_persons.user_id, step3_phishing_domains.domain_position, test_domains.domain, step3_phishing_domains.elapsed_time, step3_phishing_domains.rating\
           FROM step3_phishing_domains, test_persons, test_domains\
           WHERE step3_phishing_domains.test_person_id = test_persons.test_person_id AND\
                 step3_phishing_domains.test_domain_id = test_domains.test_domain_id"
    csv_data = execute_query(sql)
    csv_data = [elem + ",phishing_domain" for elem in csv_data]

    return csv_data

def export_step3():
    step1_created = export_step3_step1_created()
    ref_domains = export_step3_ref_domains()
    phishing_domains = export_step3_phishing_domains()

    csv_data = step1_created + ref_domains + phishing_domains
    save_to_csv("step3", "user_id,domain_position,rated_domain,elapsed_time,rating,type", csv_data)

def export_step4():
    sql = "SELECT test_persons.user_id, step4.domain_position, step4.domain, step4.elapsed_time\
           FROM step4, test_persons\
           WHERE step4.test_person_id = test_persons.test_person_id"
    csv_data = execute_query(sql)
    save_to_csv("step4", "user_id,domain_position,created_domain,elapsed_time", csv_data)

def create_step5_dict(csv_data):
    temp_data = {}
    for line in csv_data:
        splitted_line = line.split(",")
        temp_data[splitted_line[0]] = ",".join(splitted_line[1:])

    return temp_data

def export_step5_step1_created():
    sql = "SELECT step5_step1_created_domains.step5_domain_id, created_domains.domain, step5_domains.selected, step5_domains.domain_position\
           FROM step5_domains, step5_step1_created_domains, created_domains\
           WHERE step5_step1_created_domains.step5_domain_id = step5_domains.step5_domain_id AND\
                 step5_step1_created_domains.created_domain_id = created_domains.created_domain_id"
    csv_data = execute_query(sql)

    return create_step5_dict(csv_data)

def export_step5_legitimate_domains():
    sql = "SELECT step5_legitimate_domains.step5_domain_id, test_domains.domain, step5_domains.selected, step5_domains.domain_position\
           FROM step5_domains, step5_legitimate_domains, test_domains\
           WHERE step5_legitimate_domains.step5_domain_id = step5_domains.step5_domain_id AND\
                 step5_legitimate_domains.test_domain_id = test_domains.test_domain_id"
    csv_data = execute_query(sql)

    return create_step5_dict(csv_data)

def export_step5_phishing_domains():
    sql = "SELECT step5_phishing_domains.step5_domain_id, test_domains.domain, step5_domains.selected, step5_domains.domain_position\
           FROM step5_domains, step5_phishing_domains, test_domains\
           WHERE step5_phishing_domains.step5_domain_id = step5_domains.step5_domain_id AND\
                 step5_phishing_domains.test_domain_id = test_domains.test_domain_id"
    csv_data = execute_query(sql)

    return create_step5_dict(csv_data)

def export_step5():
    sql = "SELECT test_persons.user_id, domain1, domain2, domain3, domain4, domain5, domain6, domain7, domain8, domain9, domain10, elapsed_time, counter\
           FROM step5, test_persons\
           WHERE step5.test_person_id = test_persons.test_person_id"
    temp_data = execute_query(sql)

    step5_step1_created_domains = export_step5_step1_created()
    step5_legitimate_domains = export_step5_legitimate_domains()
    step5_phishing_domains = export_step5_phishing_domains()

    csv_data = []
    for line in temp_data:
        splitted_line = line.split(",")
        current_line = splitted_line[0] + "," + splitted_line[-1] + "," + splitted_line[-2]
        for domain_id in splitted_line[1:-2]:
            if domain_id in step5_step1_created_domains:
                current_line += "," + step5_step1_created_domains[domain_id] + ",step1_created"
            elif domain_id in step5_legitimate_domains:
                current_line += "," + step5_legitimate_domains[domain_id] + ",legitimate"
            elif domain_id in step5_phishing_domains:
                current_line += "," + step5_phishing_domains[domain_id] + ",phishing"

        csv_data.append(current_line)

    save_to_csv("step5", "user_id,counter,elapsed_time,domain1,domain1.selected,domain1.domain_position,domain1.type,domain2,domain2.selected,domain2.domain_position,domain2.type,domain3,domain3.selected,domain3.domain_position,domain3.type,,domain4,domain4.selected,domain4.domain_position,domain4.type,domain5,domain5.selected,domain5.domain_position,domain5.type,domain6,domain6.selected,domain6.domain_position,domain6.type,domain7,domain7.selected,domain7.domain_position,domain7.type,domain8,domain8.selected,domain8.domain_position,domain8.type,domain9,domain9.selected,domain9.domain_position,domain9.type,domain10,domain10.selected,domain10.domain_position,domain10.type", csv_data)

def export_questionnaire():
    sql = "SELECT test_persons.user_id, questionnaire.age, questionnaire.gender_current, questionnaire.education, countries.country, questionnaire.f1, questionnaire.f2, questionnaire.f3, questionnaire.f4, questionnaire.f5, questionnaire.f6, questionnaire.f7, questionnaire.f8, questionnaire.f9, questionnaire.f10, questionnaire.f11, questionnaire.f12, questionnaire.f13, questionnaire.f14, questionnaire.f15, questionnaire.f16, questionnaire.attention_test1, questionnaire.attention_test2\
           FROM questionnaire, test_persons, countries\
           WHERE questionnaire.test_person_id = test_persons.test_person_id AND\
                 questionnaire.origin_id = countries.country_id"
    csv_data = execute_query(sql)
    save_to_csv("questionnaire", "user_id,age,gender,education,country,f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,attention_test1,attention_test2", csv_data)

export_test_persons()
export_created_domains()
export_step1()
export_step2()
export_step3()
export_step4()
export_step5()
export_questionnaire()