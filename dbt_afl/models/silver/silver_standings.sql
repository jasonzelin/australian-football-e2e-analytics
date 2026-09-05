with source as (
    select * from {{ source('bronze', 'standings') }}
)

select
    position
    ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(team, r"\'", '"')), "$.id")) as team_id
    ,pts
    ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(games, r"\'", '"')), "$.played")) as played_games
    ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(games, r"\'", '"')), "$.win")) as win_games
    ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(games, r"\'", '"')), "$.drawn")) as drawn_games
    ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(games, r"\'", '"')), "$.lost")) as lost_games
    ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(points, r"\'", '"')), '$.for')) as for_points
    ,LAX_INT64(JSON_EXTRACT(safe.parse_json(regexp_replace(points, r"\'", '"')), '$.against')) as against_points
    ,last_5
from
    source