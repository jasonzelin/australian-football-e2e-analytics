with source as (
    select * from {{ source('bronze', 'players') }}
)

,raw as (
    select
        id
        ,name
    from
        source
)

select
    *
from
    raw