SELECT DISTINCT p_name,dog_name
FROM (	SELECT dw.email, p_name ,min(d.dog_age) as MIN_AGE
		FROM ((Dog_Walker as dw JOIN Person as p ON dw.email=p.email) JOIN Taking_Dogs AS td ON dw.email=td.email) JOIN Dogs AS d ON td.dog_id=d.dog_id
		GROUP BY dw.email, p_name
		HAVING min(d.dog_age)) as t
        JOIN Taking_Dogs AS td ON t.email=td.email JOIN Dogs AS d ON td.dog_id=d.dog_id
WHERE min_age=dog_age
ORDER BY p_name ASC;