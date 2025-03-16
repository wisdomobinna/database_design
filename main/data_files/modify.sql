INSERT INTO location (city, area, latitude, longitude)
SELECT DISTINCT city,
       area,
       latitude::numeric,
       longitude::numeric
FROM staging_crime
WHERE latitude IS NOT NULL 
  AND longitude IS NOT NULL
ON CONFLICT (city, area, latitude, longitude) DO NOTHING;

INSERT INTO timeinfo (crimetime)
SELECT DISTINCT to_timestamp(date || ' ' || time, 'YYYY-MM-DD HH24:MI:SS')
FROM staging_crime
WHERE date IS NOT NULL 
  AND time IS NOT NULL
ON CONFLICT (crimetime) DO NOTHING;

INSERT INTO crimecategory (categoryname)
SELECT DISTINCT crime_category
FROM staging_crime
ON CONFLICT (categoryname) DO NOTHING;

INSERT INTO premisetype (premisdesc)
SELECT DISTINCT premis_desc
FROM staging_crime
ON CONFLICT (premisdesc) DO NOTHING;

INSERT INTO crimetype (crimedesc, categoryid)
SELECT DISTINCT sc.crime_desc, cc.categoryid
FROM staging_crime sc
JOIN crimecategory cc ON sc.crime_category = cc.categoryname
ON CONFLICT (crimedesc, categoryid) DO NOTHING;

UPDATE staging_crime sc
SET locationid = l.locationid
FROM location l
WHERE l.city = sc.city
  AND TRIM(LOWER(l.area)) = TRIM(LOWER(sc.area));

UPDATE staging_crime sc
SET timeid = t.timeid
FROM timeinfo t
WHERE t.crimetime = to_timestamp(sc.date || ' ' || sc.time, 'YYYY-MM-DD HH24:MI:SS');

UPDATE staging_crime sc
SET crimecategoryid = cc.categoryid
FROM crimecategory cc
WHERE cc.categoryname = sc.crime_category;

UPDATE staging_crime sc
SET crimetypeid = ct.crimetypeid
FROM crimetype ct
WHERE ct.crimedesc = sc.crime_desc;

UPDATE staging_crime sc
SET premisetypeid = pt.premisid
FROM premisetype pt
WHERE pt.premisdesc = sc.premis_desc;

INSERT INTO crime (locationid, timeid, crimecategoryid, crimetypeid, premisetypeid, arrestmade)
SELECT locationid,
       timeid,
       crimecategoryid,
       crimetypeid,
       premisetypeid,
       CASE WHEN arrest = '1' THEN true ELSE false END
FROM staging_crime
WHERE locationid IS NOT NULL
  AND timeid IS NOT NULL
  AND crimecategoryid IS NOT NULL
  AND crimetypeid IS NOT NULL
  AND premisetypeid IS NOT NULL;
