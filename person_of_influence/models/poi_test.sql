select 
    dt,
    count(*) as num_rows
from {{ source('person_of_influence', 'poi_stage') }} 
group by dt
order by dt