with source as (
    select * from {{ source('bronze', 'leagues') }}
)

,raw as (
    select
        id
        ,name
        ,logo
        ,season
        ,start::date as start_date
        ,end::date as end_date
        ,current
    from
        source
)

select
    *
from
    raw