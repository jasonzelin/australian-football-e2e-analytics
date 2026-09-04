with games as (
    select * from {{ source('silver', 'silver_games') }}
)
,teams as (
    select * from {{ source('silver', 'silver_teams') }}
)
SELECT
	ht.name AS team_name
	,COUNT(*) AS hosting_count
FROM
	games g
	LEFT JOIN teams ht ON g.home_team_id = ht.id
WHERE TRUE
	AND STRING(g.long_status) = 'Finished'
GROUP BY
	ht.name
ORDER BY
	COUNT(*) DESC