with games as (
    select * from {{ source('silver', 'silver_games') }}
)
,teams as (
    select * from {{ source('silver', 'silver_teams') }}
)
SELECT
	awt.name AS team_name
	,COUNT(*) AS hosting_count
FROM
	games g
	LEFT JOIN teams awt ON g.away_team_id = awt.id
WHERE TRUE
	AND STRING(g.long_status) = 'Finished'
GROUP BY
	awt.name