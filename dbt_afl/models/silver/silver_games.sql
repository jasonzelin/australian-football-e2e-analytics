with source as (
    select * from {{ source('bronze', 'games') }}
)

,raw as (
    select
        safe.parse_json(regexp_replace(game, r"\'", '"')) as game_id
        ,safe.parse_json(regexp_replace(league, r"\'", '"')) as league_id
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