with source as (
    select * from {{ source('bronze', 'standings') }}
)

select
    position
    ,regexp_replace_all(team, r"\'", '"') as team
    ,pts
    ,regexp_replace_all(games, r"\'", '"') as games
    ,regexp_replace_all(points, r"\'", '"') as points
    ,last_5
from
    source