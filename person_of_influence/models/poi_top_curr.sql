-- get current top POIs
SELECT 
    name,
    num_cats,
    best_cat_rnk
FROM {{ source('person_of_influence', 'poi_hist') }} 
WHERE   
    dt = (select max(dt) from poi_hist)
    and 
    (
        num_cats >= 2
        or best_cat_rnk <=50
    )