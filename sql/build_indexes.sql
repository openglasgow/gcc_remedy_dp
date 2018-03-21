-- Indexes on columns

-- Date columns
CREATE INDEX est_response_date_idx ON remedy_cases(est_resp_date);
CREATE INDEX date_1st_contact_made_idx ON remedy_cases(date_1st_contact_made);
CREATE INDEX date_paid_idx ON remedy_cases(date_paid);
CREATE INDEX call_opened_date_time_idx ON remedy_cases(call_opened_date_time);
CREATE INDEX call_closed_date_time_idx ON remedy_cases(call_closed_date_time);
CREATE INDEX call_opened_time_idx ON remedy_cases(call_opened_time);
CREATE INDEX call_closed_time_idx ON remedy_cases(call_closed_time);
CREATE INDEX date_time_last_modified_idx ON remedy_cases(date_time_last_modified);
CREATE INDEX date_time_sla_warning_idx ON remedy_cases(date_time_sla_warning);
CREATE INDEX date_time_sla_violation_idx ON remedy_cases(date_time_sla_violation);
CREATE INDEX date_time_manual_closed_idx ON remedy_cases(date_time_manual_closed);
CREATE INDEX original_create_time_idx ON remedy_cases(original_create_time);

-- Request ID
CREATE INDEX call_id_idx ON remedy_cases(call_id);

-- Categories
CREATE INDEX call_topic_category_1_idx ON remedy_cases(call_topic_category_1);
CREATE INDEX call_topic_category_2_idx ON remedy_cases(call_topic_category_2);
CREATE INDEX call_topic_category_3_idx ON remedy_cases(call_topic_category_3);

-- Client info
CREATE INDEX uprn_idx ON remedy_cases(uprn);
CREATE INDEX caller_title_idx ON remedy_cases(caller_title);
CREATE INDEX caller_first_name_idx ON remedy_cases(caller_first_name);
CREATE INDEX caller_second_name_idx ON remedy_cases(caller_second_name);
