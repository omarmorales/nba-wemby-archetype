-- Best rookie BPM seasons ever
-- minimum 41 games (half a season) to filter out garbage-time outliers
WITH deduped_advanced AS (
  SELECT DISTINCT ON (player_id, season)
    player,
    player_id,
    season,
    bpm,
    vorp,
    ws,
    g,
    mp
  FROM advanced
  WHERE bpm IS NOT NULL
  ORDER BY player_id, season, g DESC
),
first_seasons AS (
  SELECT
    player_id,
    MIN(season) AS rookie_season
  FROM deduped_advanced
  GROUP BY player_id
),
rookie_bpm AS (
  SELECT
    a.player,
    a.season  AS rookie_season,
    a.bpm,
    a.vorp,
    a.ws,
    a.g,
    a.mp
  FROM deduped_advanced a
  JOIN first_seasons f
    ON a.player_id    = f.player_id
   AND a.season       = f.rookie_season
  WHERE
    a.g  >= 41        -- at least half a season played
    AND a.mp >= 500   -- meaningful minutes played
)
SELECT
  player,
  rookie_season,
  ROUND(bpm::numeric,  1) AS bpm,
  ROUND(vorp::numeric, 1) AS vorp,
  ROUND(ws::numeric,   1) AS ws,
  g
FROM rookie_bpm
ORDER BY bpm DESC
LIMIT 20;