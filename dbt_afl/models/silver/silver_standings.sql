with source as (
    select * from {{ source('bronze', 'standings') }}
)

select
    position
    ,regexp_replace(team, r"\'", '"') as team
    ,pts
    ,regexp_replace(games, r"\'", '"') as games
    ,regexp_replace(points, r"\'", '"') as points
    ,last_5
from
    source