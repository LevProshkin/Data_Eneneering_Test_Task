--Delete records where the email domain is not from a specific list(e.g., keep only emails from `gmail.com`, `yahoo.com`, and `example.com`)
DELETE FROM 
	generated_users
WHERE 
	SPLIT_PART(email, '@', 2) NOT IN ('gmail.com', 'yahoo.com', 'example.com');
SELECT*FROM generated_users;