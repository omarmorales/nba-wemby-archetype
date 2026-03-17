WITH player_stats AS (
  SELECT
    p.player,
    p.ht_in_in,

    AVG(t.x3p_percent) AS avg_3p_pct,
    SUM(t.blk) / SUM(t.g) AS blk_per_game,
    SUM(t.pts) / SUM(t.g) AS pts_per_game

  FROM players p
  JOIN totals t 
    ON p.player_id = t.player_id

  WHERE 
    p.ht_in_in IS NOT NULL

  GROUP BY p.player, p.ht_in_in
),

filtered AS (
  SELECT *
  FROM player_stats
  WHERE player IN (
    'Victor Wembanyama',
    'Hakeem Olajuwon',
    'David Robinson',
    'Shaquille O''Neal',
    'Kareem Abdul-Jabbar',
    'Dirk Nowitzki',
    'Kristaps Porzingis',
    'Karl-Anthony Towns',
    'Chet Holmgren'
  )
)

SELECT
  player,
  ROUND((ht_in_in * 2.54 / 100)::numeric, 2) AS height_m,
  ROUND(avg_3p_pct::numeric, 3) AS avg_3p_pct,
  ROUND(blk_per_game::numeric, 2) AS blk_per_game,
  ROUND(pts_per_game::numeric, 1) AS pts_per_game

FROM filtered
ORDER BY height_m DESC;