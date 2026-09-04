with source as (
    select * from {{ source('bronze', 'games') }}
)

,raw as (
    select
        LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(game, r"\'", '"')), "$.id")) as game_id
        ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(league, r"\'", '"')), "$.id")) as league_id
        ,DATETIME(SAFE_CAST(date AS TIMESTAMP)) as datetime
        ,timezone
        ,round
        ,week
        ,venue
        ,attendance
        ,JSON_EXTRACT(safe.parse_json(regexp_replace(status, r"\'", '"')), '$.long') as long_status
        ,JSON_EXTRACT(safe.parse_json(regexp_replace(status, r"\'", '"')), '$.short') as short_status
        ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(teams, r"\'", '"')), "$.home.id")) as home_team_id
        ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(teams, r"\'", '"')), "$.away.id")) as away_team_id
        ,JSON_EXTRACT(safe.parse_json(regexp_replace(scores, r"\'", '"')), "$.home") as home_scores
        ,JSON_EXTRACT(safe.parse_json(regexp_replace(scores, r"\'", '"')), "$.away") as away_scores
    from
        source
)

select
    *
from
    raw 