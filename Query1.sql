--Retrieve the count of users who signed up on each day.
SELECT 
    DATE(signup_date) AS signup_day,
    COUNT(*) AS user_count
FROM 
    generated_users
GROUP BY 
    signup_day
ORDER BY 
    signup_day;