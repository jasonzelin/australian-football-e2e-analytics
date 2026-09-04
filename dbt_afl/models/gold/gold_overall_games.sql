with games as (
    select * from {{ source('silver', 'silver_games') }}
)
,teams as (
    select * from {{ source('silver', 'silver_teams') }}
)
SELECT
	g.* EXCEPT(home_team_id, away_team_id, home_scores, away_scores)
	,JSON_EXTRACT(g.home_scores, '$.score') AS home_score
	,JSON_EXTRACT(g.away_scores, '$.score') AS away_score
	,ht.name AS home_team_name
	,awt.name AS away_team_name
FROM
	games g
	LEFT JOIN teams ht ON g.home_team_id = ht.id
	LEFT JOIN teams awt ON g.away_team_id = awt.id
WHERE TRUE
	AND STRING(g.long_status) = 'Finished'