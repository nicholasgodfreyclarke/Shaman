DROP TABLE IF EXISTS variable_dependencies;
DROP TABLE IF EXISTS variable_source;

CREATE TABLE variable_dependencies (variable_name TEXT NOT NULL, dependency TEXT);
CREATE TABLE variable_source (variable_name TEXT PRIMARY KEY NOT NULL  UNIQUE , source TEXT, type TEXT);
CREATE INDEX variable_dependencies_idx ON variable_source (variable_name ASC);
