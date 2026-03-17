WITH player_stats AS (
  SELECT
    p.player,
    p.player_id,
    p.ht_in_in,

    AVG(t.x3p_percent) AS avg_3p_pct,
    SUM(t.blk) / SUM(t.g) AS blk_per_game,
    SUM(t.x3pa) AS total_3pa,
    SUM(t.g) AS total_games

  FROM players p
  JOIN totals t 
    ON p.player_id = t.player_id

  WHERE 
    p.ht_in_in IS NOT NULL
    AND t.season >= 2010

  GROUP BY 
    p.player,
    p.player_id,
    p.ht_in_in

  HAVING 
    SUM(t.x3pa) > 100
    AND SUM(t.g) > 100
)
SELECT * FROM player_stats;