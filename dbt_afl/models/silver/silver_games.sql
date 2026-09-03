with source as (
    select * from {{ source('bronze', 'games') }}
)

,raw as (
    select
        game::json_extract_scalar('$.game_id') as game_id
        ,league::json_extract_scalar('$.league_id') as league_id
        ,date::datetime as datetime
        ,timezone
        ,round
        ,week
        ,venue
        ,attendance
        ,regex_replace_all(status, r"\'", '"') as status
        ,regex_replace_all(teams, r"\'", '"') as teams
        ,regex_replace_all(scores, r"\'", '"') as scores
    from
        source
)

select
    *
from
    raw 