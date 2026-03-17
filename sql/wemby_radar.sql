WITH player_stats AS (
  SELECT
    p.player,
    p.ht_in_in,

    SUM(t.pts) / SUM(t.g) AS pts_per_game,
    AVG(t.x3p_percent) AS avg_3p_pct,
    SUM(t.blk) / SUM(t.g) AS blk_per_game

  FROM players p
  JOIN totals t 
    ON p.player_id = t.player_id

  GROUP BY p.player, p.ht_in_in
),

filtered AS (
  SELECT *
  FROM player_stats
  WHERE player IN (
    'Victor Wembanyama',
    'Chet Holmgren',
    'Kristaps Porzingis',
    'Dirk Nowitzki',
    'Hakeem Olajuwon'
  )
)

SELECT * FROM filtered;