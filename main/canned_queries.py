from django.db import connection

canned_queries = {}

def register_query(func):
    """Decorator to save to canned_queries."""
    canned_queries[func.__name__] = func
    return func


# def execute_query(query):
#     with connection.cursor() as cursor:
#         cursor.execute(query)
#         results = cursor.fetchall()
#         columns = [col[0] for col in cursor.description]
#     return results, columns


# 1. Monthly Crime Trends in Both Cities
@register_query
def monthly_trends():
    query="""
        SELECT 
            l.city,
            EXTRACT(MONTH FROM t.crimetime) AS month,
            COUNT(*) AS crime_count
        FROM crime c
        JOIN location l ON c.locationid = l.locationid
        JOIN timeinfo t ON c.timeid = t.timeid
        GROUP BY l.city, month
        ORDER BY month, l.city;
    """
    chart_type = "bar"
    return query, chart_type

# 2. Most Common Types of Crime by City
@register_query
def common_crime():
    query="""
        SELECT 
            l.city,
            cc.categoryname,
            COUNT(*) AS count_crimes
        FROM crime c
        JOIN location l ON c.locationid = l.locationid
        JOIN crimetype ct ON c.crimetypeid = ct.crimetypeid
        JOIN crimecategory cc ON ct.categoryid = cc.categoryid
        GROUP BY l.city, cc.categoryname
        ORDER BY cc.categoryname, l.city;
    """
    chart_type = "bar"
    return query, chart_type

# 3. Peak Hours
@register_query
def peak_hours():
    query="""
        SELECT 
            EXTRACT(HOUR FROM t.crimetime) AS hour,
            COUNT(*) AS crime_count
        FROM crime c
        JOIN timeinfo t ON c.timeid = t.timeid
        GROUP BY hour
        ORDER BY hour;
    """
    chart_type = "bar"
    return query, chart_type

# 4. Peak Days
@register_query
def peak_days():
    query="""
        SELECT 
            to_char(t.crimetime, 'Day') AS day_of_week,
            COUNT(*) AS crime_count
        FROM crime c
        JOIN timeinfo t ON c.timeid = t.timeid
        GROUP BY EXTRACT(DOW FROM t.crimetime), day_of_week
        ORDER BY EXTRACT(DOW FROM t.crimetime);
    """
    chart_type = "bar"
    return query, chart_type

# 5. Geographical Crime Hotspots (Chicago)
@register_query
def hotspots_chicago():
    query="""
        SELECT 
            latitude,
            longitude
        FROM location
        WHERE city = 'Chicago'
    """
    chart_type = "heatmap"
    return query, chart_type

# 6. Geographical Crime Hotspots (LA)
@register_query
def hotspots_la():
    query="""
        SELECT 
            latitude,
            longitude
        FROM location
        WHERE city = 'LA'
        GROUP BY latitude, longitude
    """
    chart_type = "heatmap"
    return query, chart_type

# 7. Year-over-Year Crime Rate Changes
@register_query
def yoy_crime():
    query="""
        WITH yearly AS (
            SELECT 
              EXTRACT(YEAR FROM t.crimetime) AS year,
              COUNT(*) AS crime_count
            FROM crime c
            JOIN timeinfo t ON c.timeid = t.timeid
            GROUP BY year
            ORDER BY year
          )
          SELECT 
              year,
              crime_count,
              LAG(crime_count) OVER (ORDER BY year) AS previous_year_count,
              ROUND(100.0 * (crime_count - LAG(crime_count) OVER (ORDER BY year)) / NULLIF(LAG(crime_count) OVER (ORDER BY year), 0), 2) AS percent_change
          FROM yearly;
    """
    chart_type = "bar"
    return query, chart_type

# 8. Crime Distribution (Chicago)
@register_query
def crime_distribution_chicago():
    query = """
        SELECT 
            ct.crimedesc,
            COUNT(*) AS crime_count,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS crime_percentage
        FROM crime c
        JOIN location l ON c.locationid = l.locationid
        JOIN crimetype ct ON c.crimetypeid = ct.crimetypeid
        WHERE l.city = 'Chicago'
        GROUP BY ct.crimedesc
        ORDER BY crime_count DESC;
    """
    chart_type = "pie"
    return query, chart_type

# 9. Crime Distribution (Los Angeles)
@register_query
def crime_distribution_la():
    query = """
        SELECT 
            ct.crimedesc,
            COUNT(*) AS crime_count,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS crime_percentage
        FROM crime c
        JOIN location l ON c.locationid = l.locationid
        JOIN crimetype ct ON c.crimetypeid = ct.crimetypeid
        WHERE l.city = 'LA'
        GROUP BY ct.crimedesc
        ORDER BY crime_count DESC;
    """
    chart_type = "pie"
    return query, chart_type

# 10. Seasonal Crime Pattern
@register_query
def crime_season():
    query="""
        SELECT 
          season,
          COUNT(*) AS crime_count
        FROM (
          SELECT 
            CASE 
              WHEN EXTRACT(MONTH FROM t.crimetime) IN (3,4,5) THEN 'Spring'
              WHEN EXTRACT(MONTH FROM t.crimetime) IN (6,7,8) THEN 'Summer'
              WHEN EXTRACT(MONTH FROM t.crimetime) IN (9,10,11) THEN 'Fall'
              WHEN EXTRACT(MONTH FROM t.crimetime) IN (12,1,2) THEN 'Winter'
            END AS season
          FROM crime c
          JOIN timeinfo t ON c.timeid = t.timeid
          -- Optionally add a WHERE clause to filter by a specific year or range
        ) sub
        GROUP BY season
        ORDER BY
          CASE 
            WHEN season = 'Winter' THEN 1
            WHEN season = 'Spring' THEN 2
            WHEN season = 'Summer' THEN 3
            WHEN season = 'Fall' THEN 4
          END;
    """
    chart_type = "bar"
    return query, chart_type

# 11. Crime Distribution by Premise Type
@register_query
def crime_distribution_premise():
    query="""
        SELECT 
            pt.premisdesc, 
            COUNT(*) AS crime_count
        FROM crime c
        JOIN premisetype pt ON c.premisid = pt.premisid
        GROUP BY pt.premisdesc
        ORDER BY crime_count DESC;
    """
    chart_type = "pie"
    return query, chart_type

# 12. 
# @register_query
# def ():
#     query="""

#     """
#     chart_type = "bar"
#     return query, chart_type