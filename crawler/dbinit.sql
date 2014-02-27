DROP TABLE IF EXISTS repository;

CREATE TABLE repository (
id INTEGER,
full_name VARCHAR,
languages_url VARCHAR,
creation_date DATE
);

DROP TABLE IF EXISTS languages;
CREATE TABLE languages(
    id INTEGER,
    lang VARCHAR,
    lines INTEGER
);