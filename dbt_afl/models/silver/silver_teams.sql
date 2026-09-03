with source as (
    select * from {{ source('bronze', 'teams') }}
)

,raw as (
    select
        id
        ,name
        ,logo
    from
        source
)

select
    *
from
    raw