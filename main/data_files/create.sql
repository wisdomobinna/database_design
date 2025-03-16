CREATE TABLE IF NOT EXISTS location (
    locationid SERIAL PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    area VARCHAR(100) NOT NULL,
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    UNIQUE (city, area, latitude, longitude)
);

CREATE TABLE IF NOT EXISTS timeinfo (
    timeid SERIAL PRIMARY KEY,
    crimetime TIMESTAMP NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS crimecategory (
    categoryid SERIAL PRIMARY KEY,
    categoryname VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS crimetype (
    crimetypeid SERIAL PRIMARY KEY,
    crimedesc VARCHAR(100) NOT NULL,
    categoryid INT NOT NULL,
    FOREIGN KEY (categoryid) REFERENCES crimecategory(categoryid) ON DELETE CASCADE,
    UNIQUE (crimedesc, categoryid)
);

CREATE TABLE IF NOT EXISTS premisetype (
    premisid SERIAL PRIMARY KEY,
    premisdesc VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS crime (
    crimeid SERIAL PRIMARY KEY,
    locationid INT NOT NULL,
    timeid INT NOT NULL,
    crimetypeid INT NOT NULL,
    premisid INT NOT NULL,
    arrestmade BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (locationid) REFERENCES location(locationid) ON DELETE CASCADE,
    FOREIGN KEY (timeid) REFERENCES timeinfo(timeid) ON DELETE CASCADE,
    FOREIGN KEY (crimetypeid) REFERENCES crimetype(crimetypeid) ON DELETE CASCADE,
    FOREIGN KEY (premisid) REFERENCES premisetype(premisid) ON DELETE CASCADE,
    UNIQUE (locationid, timeid, crimetypeid, premisid, arrestmade)
);

-- Indexes for Performance
-- CREATE INDEX idx_location_city ON location(city);
-- CREATE INDEX idx_location_area ON location(area);
-- CREATE INDEX idx_timeinfo_date ON timeinfo(crimetime);
-- CREATE INDEX idx_crime_arrest ON crime(arrestmade);
