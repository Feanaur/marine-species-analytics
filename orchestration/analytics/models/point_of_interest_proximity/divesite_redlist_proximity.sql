{{ config(materialized='table') }}

WITH dive_site_redlist_occurrences AS (
    SELECT 
        d.title,  
        o.eventdate,
        o.species,
        o.individualcount,
        ST_Distance(o.geography,  d.geography) AS distance_to_dive_site,
        ROW_NUMBER() OVER (PARTITION BY o.eventdate ORDER BY ST_Distance(o.geography, d.geography)) as proximity_rank,
        o.geography
    FROM {{ ref('stg_redlist_occurences') }} o
    CROSS JOIN {{ ref('divesites') }} d  
    WHERE ST_DWithin(o.geography, d.geography, {{ env_var('PROXIMITY_METERS') }}) and o.eventdate >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {{ env_var('AGGREGATION_WINDOW_DAYS') }} DAY)
)

SELECT *
FROM dive_site_redlist_occurrences
WHERE proximity_rank = 1