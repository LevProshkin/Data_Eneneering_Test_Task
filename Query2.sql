--List all unique email domains present in the database.
SELECT DISTINCT 
    SPLIT_PART(email, '@', 2) AS email_domain
FROM 
    generated_users
ORDER BY 
    email_domain; 