--Find the user(s) with the most common email domain
SELECT * 
FROM generated_users
WHERE 
	domain =
	(
	SELECT
		domain
	FROM 
		generated_users
	GROUP BY 
		domain
	HAVING 
		COUNT(domain) = 
		(
		SELECT
			COUNT(domain)
		FROM 
			generated_users
		GROUP BY 
			domain
		ORDER BY
			1 DESC
		LIMIT 1
		)	
	);