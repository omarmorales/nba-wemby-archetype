-- Career per-game averages for all players
-- using 50 games minimum (not 200) so recent players like Wemby qualify
-- averaged across all seasons weighted by games played
WITH deduped_totals AS (
  SELECT DISTINCT ON (player_id, season)
    player,
    player_id,
    season,
    pts,
    blk,
    g
  FROM totals
  ORDER BY player_id, season, g DESC
),
career_stats AS (
  SELECT
    player,
    player_id,
    SUM(pts)::numeric AS total_pts,
    SUM(blk)::numeric AS total_blk,
    SUM(g)            AS total_games
  FROM deduped_totals
  GROUP BY player, player_id
  HAVING SUM(g) >= 50
),
per_game AS (
  SELECT
    player,
    player_id,
    ROUND(total_pts / total_games, 2) AS pts_per_game,
    ROUND(total_blk / total_games, 2) AS blk_per_game
  FROM career_stats
)
SELECT *
FROM per_game
WHERE pts_per_game IS NOT NULL
  AND blk_per_game IS NOT NULL
ORDER BY blk_per_game DESC;