with source as (
    select * from {{ source('bronze', 'seasons') }}
)

,raw as (
    select
        `0` as season_id
    from
        source
)

select
    *
from
    raw