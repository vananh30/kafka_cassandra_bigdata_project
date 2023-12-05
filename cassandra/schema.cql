CREATE TABLE weatherreport (
  forecastdate TIMESTAMP,
  location TEXT,
  description TEXT,
  temp FLOAT,
  feels_like FLOAT,
  temp_min FLOAT,
  temp_max FLOAT,
  pressure FLOAT,
  humidity FLOAT,
  wind FLOAT,
  sunrise BIGINT,
  sunset BIGINT,
  PRIMARY KEY (location, forecastdate)
);

CREATE TABLE fakerdata (
  name TEXT,
  gender TEXT,
  address TEXT,
  year TEXT,
  email TEXT,
  phone_number TEXT,
  job TEXT,
  company TEXT,
  country TEXT,
  city TEXT,
  date_time TEXT,
  credit_card_number TEXT,
  PRIMARY KEY (name, phone_number)
);


CREATE TABLE wikipediadata (
    id BIGINT,
    type TEXT,
    title TEXT,
    timestamp TIMESTAMP,
    user TEXT,
    bot BOOLEAN,
    length_old INT,
    length_new INT,
    revision_old INT,
    revision_new INT,
    PRIMARY KEY (id)
);