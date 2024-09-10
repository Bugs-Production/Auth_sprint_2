-- Создание схемы
CREATE SCHEMA IF NOT EXISTS content;

-- Создание таблиц
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid NOT NULL, 
    film_work_id uuid NOT NULL,
    created timestamp with time zone
);
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role TEXT NOT NULL,
    created timestamp with time zone
);

-- Создание индексов на уникальность
CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_idx ON content.person_film_work (film_work_id, person_id, role);
CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre_idx ON content.genre_film_work (genre_id, film_work_id);

-- Создание индексов на оптимизацию JOIN-запросов
CREATE INDEX IF NOT EXISTS genre_film_work_genre_id_idx ON content.genre_film_work (genre_id);
CREATE INDEX IF NOT EXISTS genre_film_work_film_work_id_idx ON content.genre_film_work (film_work_id);
CREATE INDEX IF NOT EXISTS person_film_work_person_id_idx ON content.person_film_work (person_id);
CREATE INDEX IF NOT EXISTS person_film_work_film_work_id_idx ON content.person_film_work (film_work_id);
