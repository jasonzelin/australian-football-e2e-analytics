with source as (
    select * from {{ source('bronze', 'standings') }}
)

select
    position
    ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(team, r"\'", '"')), "$.id")) as team_id
    ,pts
    ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(games, r"\'", '"')), "$.id")) as games_id
    ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(points, r"\'", '"')), "$.id")) as points_id
    ,last_5
from
    source