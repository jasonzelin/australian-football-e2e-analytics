with source as (
    select * from {{ source('bronze', 'leagues') }}
)

,raw as (
    select
        id
        ,name
        ,logo
        ,season
        ,safe_cast(`start` as date) as start_date
        ,safe_cast(`end` as date) as end_date
        ,`current`
    from
        source
)

select
    *
from
    raw