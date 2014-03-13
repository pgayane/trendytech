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

CREATE UNIQUE INDEX id_idx ON repository(id);

alter table repository
    add size integer,
    add stargazers_count integer,
    add watchers_count integer,
    add subscribers_count integer,
    add forks_count integer,
    add open_issues_count integer;

CREATE INDEX username_idx ON repository(username);


select username from repository order by username limit 100