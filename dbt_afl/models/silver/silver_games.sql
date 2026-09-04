with source as (
    select * from {{ source('bronze', 'games') }}
)

,raw as (
    select
        JSON_EXTRACT(safe.parse_json(regexp_replace(game, r"\'", '"')), "$.id") as game_id
        ,JSON_EXTRACT(safe.parse_json(regexp_replace(league, r"\'", '"')), "$.id") as league_id
        ,date as datetime
        ,timezone
        ,round
        ,week
        ,venue
        ,attendance
        ,safe.parse_json(regexp_replace(status, r"\'", '"')) as status
        ,safe.parse_json(regexp_replace(teams, r"\'", '"')) as teams
        ,safe.parse_json(regexp_replace(scores, r"\'", '"')) as scores
    from
        source
)

select
    *
from
    raw 