-- dedup: for traded players keep the row with most games (season total)
WITH deduped_advanced AS (
  SELECT DISTINCT ON (player_id, season)
    player,
    player_id,
    season,
    per,
    ws,
    bpm,
    vorp,
    ws_48,
    g
  FROM advanced
  ORDER BY player_id, season, g DESC
),
deduped_totals AS (
  SELECT DISTINCT ON (player_id, season)
    player_id,
    season,
    pts,
    trb,
    ast,
    blk,
    g
  FROM totals
  ORDER BY player_id, season, g DESC
),
first_seasons AS (
  SELECT
    player_id,
    MIN(season) AS rookie_season
  FROM deduped_advanced
  GROUP BY player_id
),
rookie_advanced AS (
  SELECT
    a.player,
    a.player_id,
    a.season,
    a.per,
    a.ws,
    a.bpm,
    a.vorp,
    a.ws_48
  FROM deduped_advanced a
  JOIN first_seasons f
    ON a.player_id = f.player_id
   AND a.season    = f.rookie_season
),
rookie_totals AS (
  SELECT
    t.player_id,
    SUM(t.pts)::numeric / NULLIF(SUM(t.g), 0) AS pts_per_game,
    SUM(t.trb)::numeric / NULLIF(SUM(t.g), 0) AS reb_per_game,
    SUM(t.ast)::numeric / NULLIF(SUM(t.g), 0) AS ast_per_game,
    SUM(t.blk)::numeric / NULLIF(SUM(t.g), 0) AS blk_per_game
  FROM deduped_totals t
  JOIN first_seasons f
    ON t.player_id = f.player_id
   AND t.season    = f.rookie_season
  GROUP BY t.player_id
)
SELECT
  a.player,
  a.season                                    AS rookie_season,
  ROUND(a.per::numeric,      2)               AS per,
  ROUND(a.ws::numeric,       2)               AS win_shares,
  ROUND(a.bpm::numeric,      2)               AS bpm,
  ROUND(a.vorp::numeric,     2)               AS vorp,
  ROUND(a.ws_48::numeric,    3)               AS ws_48,
  ROUND(t.pts_per_game::numeric, 1)           AS pts_per_game,
  ROUND(t.reb_per_game::numeric, 1)           AS reb_per_game,
  ROUND(t.ast_per_game::numeric, 1)           AS ast_per_game,
  ROUND(t.blk_per_game::numeric, 1)           AS blk_per_game
FROM rookie_advanced a
JOIN rookie_totals t ON a.player_id = t.player_id
WHERE a.player IN (
  'Victor Wembanyama',
  'LeBron James',
  'Tim Duncan',
  'Shaquille O''Neal',
  'Kareem Abdul-Jabbar',
  'Kevin Durant',
  'Giannis Antetokounmpo',
  'David Robinson'
)
ORDER BY a.bpm DESC;