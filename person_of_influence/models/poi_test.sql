select 
    dt,
    count(*) as num_rows
from poi_stage
group by dt
order by dt