WITH vendas_sorteio AS (
SELECT sorteio.nome AS nome_sorteio, sorteio.id_sorteio AS agregado_id_sorteio, *, SUM(preco_venda * quantidade_vendida) AS [total_comprado]
FROM sorteio 
CROSS JOIN venda 
WHERE data_limite > "2026-05-01" AND data_inicial < "2026-05-01"
AND data_venda > data_inicial AND data_venda < data_limite
GROUP BY nome_sorteio,id_usuario
)
WITH 


ON bilhete.id_sorteio = agregado_id_sorteio