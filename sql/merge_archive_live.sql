-- Merges the records from ArchiveCase to LiveCase

-- To check
select live.week, live_count, archive_count from (select date_trunc('week', call_opened_date_time) "week", count(*) live_count from remedy_test group by week order by week desc) as live
inner join (select date_trunc('week', original_create_time) "week", count(*) archive_count from archive_test group by week order by week desc) as archive on archive.week=live.week;

-- Create newtable with all the columns from LiveCase then add Archive Case different columns
select * into merged_cases from archive_cases;

-- Add columns to remedy_cases;
alter table merged_cases
  ADD COLUMN property_type varchar, 
  ADD COLUMN agency_ref varchar, 
  ADD COLUMN service_add_post_code varchar, 
  ADD COLUMN niv_grading varchar, 
  ADD COLUMN opt_out_reason varchar, 
  ADD COLUMN other_reason varchar, 
  ADD COLUMN calendar_code varchar, 
  ADD COLUMN dangerous_defect varchar, 
  ADD COLUMN avoiding_action varchar, 
  ADD COLUMN care_group varchar, 
  ADD COLUMN make varchar, 
  ADD COLUMN permit_zone varchar, 
  ADD COLUMN vrm varchar, 
  ADD COLUMN request_printed varchar, 
  ADD COLUMN mcs_call_assignment varchar, 
  ADD COLUMN opening_hours varchar, 
  ADD COLUMN contact_mobile varchar, 
  ADD COLUMN product_type varchar, 
  ADD COLUMN summary varchar;

-- Insert updated archive cases that have been closed
INSERT INTO merged_cases
  SELECT * FROM archive_test;

-- Copy orignal create time to call_opened_date_time
UPDATE merged_cases SET call_opened_date_time = original_create_time;

-- move updated archive cases into remedy_cases
INSERT INTO merged_cases (property_type, agency_ref, assignment_officer, call_id, call_type, assigned_to, last_log_entry, bulk_uplift_date, est_resp_date, est_resp_date_bst, pan, pen, cust_sat_call_back, route, caller_type, date_1st_contact_made, date_1st_contact_made_bst, date_paid, date_paid_bst, eps_closure_code, agent_login_id, issue_count, ward, ward_no__decoded_from_ward_name_, ward_no__directly_from_database_, host_department, priority, ralf_priority, call_topic, call_topic_category_1, call_topic_category_2, call_topic_category_3, call_summary, caller_geographic_location, caller_name, details, location_description, call_agent, call_opened_date, call_opened_date_bst, call_opened_date_time, call_opened_time, call_opened_date_time_bst, call_opened_time_bst, call_closed_date, call_closed_date_bst, call_closed_date_time, call_closed_date_time_bst, call_resolved, call_resolved_bst, sla_status, source_information, transfer_type, service_add_email_address, service_add_name_num, service_add_phone, contact_add_town, service_address, service_add_post_code, request_status, usrn, date_time_last_modified, date_time_last_modified_bst, date_time_sla_warning, date_time_sla_warning_bst, date_time_sla_violation, date_time_sla_violation_bst, last_modified_by, service_request_log, date_time_manual_closed, date_time_manual_closed_bst, refusal_list, foi_closure_code, lay_assessors_pin_no, charge_code, item_quantity, invoice_address, manual_closed___system_closed_date, closure_code, complaint_justified, private_individual, business, media, academic, charity__lobby_or_campaign, msp__med__mp_or_peers, other_groups, applicant_ethnic_origin, disability_info, other_communication_method, neighbourhood_code, cpp_code, chcp_code, tag_id, surface_type, meterage_quantity, repair_type, time_taken, utility, payment_authorised_received, niv_grading, contact_premise_no, contact_premise_name, uprn, opt_out_reason, other_reason, calendar_code, number_completed, dangerous_defect, avoiding_action, caller_title, caller_first_name, caller_second_name, status_code , care_group, make, permit_zone, vrm, request_printed, mcs_call_assignment, opening_hours, contact_mobile, product_type, summary)
  SELECT                  property_type, agency_ref, assignment_officer, call_id, call_type, assigned_to, last_log_entry, bulk_uplift_date, est_resp_date, est_resp_date_bst, pan, pen, cust_sat_call_back, route, caller_type, date_1st_contact_made, date_1st_contact_made_bst, date_paid, date_paid_bst, eps_closure_code, agent_login_id, issue_count, ward, ward_no__decoded_from_ward_name_, ward_no__directly_from_database_, host_department, priority, ralf_priority, call_topic, call_topic_category_1, call_topic_category_2, call_topic_category_3, call_summary, caller_geographic_location, caller_name, details, location_description, call_agent, call_opened_date, call_opened_date_bst, call_opened_date_time, call_opened_time, call_opened_date_time_bst, call_opened_time_bst, call_closed_date, call_closed_date_bst, call_closed_date_time, call_closed_date_time_bst, call_resolved, call_resolved_bst, sla_status, source_information, transfer_type, service_add_email_address, service_add_name_num, service_add_phone, contact_add_town, service_address, service_add_post_code, request_status, usrn, date_time_last_modified, date_time_last_modified_bst, date_time_sla_warning, date_time_sla_warning_bst, date_time_sla_violation, date_time_sla_violation_bst, last_modified_by, service_request_log, date_time_manual_closed, date_time_manual_closed_bst, refusal_list, foi_closure_code, lay_assessors_pin_no, charge_code, item_quantity, invoice_address, manual_closed___system_closed_date, closure_code, complaint_justified, private_individual, business, media, academic, charity__lobby_or_campaign, msp__med__mp_or_peers, other_groups, applicant_ethnic_origin, disability_info, other_communication_method, neighbourhood_code, cpp_code, chcp_code, tag_id, surface_type, meterage_quantity, repair_type, time_taken, utility, payment_authorised_received, niv_grading, contact_premise_no, contact_premise_name, uprn, opt_out_reason, other_reason, calendar_code, number_completed, dangerous_defect, avoiding_action, caller_title, caller_first_name, caller_second_name, status_code , care_group, make, permit_zone, vrm, request_printed, mcs_call_assignment, opening_hours, contact_mobile, product_type, summary
  FROM remedy_test;



-- Check against remedy_cases
select merged.month, merged_count, remedy_count from (select date_trunc('month', call_opened_date_time) "month", count(*) merged_count from merged_cases group by month order by month desc) as merged
INNER JOIN (select date_trunc('month', call_opened_date_time) "month", count(*) remedy_count from remedy_cases group by month order by month desc) as remedy on merged.month=remedy.month;




