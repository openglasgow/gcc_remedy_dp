SELECT date_trunc('day', call_opened_date) "day", 
       host_department, 
       call_topic_category_1, 
       call_topic_category_2, 
       call_topic_category_3, 
       count(*)
FROM remedy_cases 
WHERE call_opened_date >= '2018-01-04' 
AND call_opened_date < '2018-01-05' group by call_topic_category_1, call_topic_category_2, call_topic_category_3, day, host_department order by host_department asc;