WITH vendas_usuario AS (
	SELECT id_venda, data_venda, usuario.id_usuario, id_produto, preco_venda, desconto_unitario, quantidade_vendida FROM usuario
	LEFT JOIN venda
	ON usuario.id_usuario = venda.id_usuario
),
vendas_sorteio AS (
    SELECT sorteio.nome AS nome_sorteio, sorteio.id_sorteio AS id_sorteio, vendas_usuario.id_usuario AS id_usuario, SUM(preco_venda * quantidade_vendida) AS [total_comprado]
    FROM sorteio 
    LEFT JOIN vendas_usuario 
    WHERE data_limite > date("now") AND data_inicial < date("now")
    AND ((data_venda > data_inicial AND data_venda < data_limite) OR data_venda IS NULL)
	AND id_usuario = ?
    GROUP BY nome_sorteio
),
vendas_convertidas AS (
    SELECT id_usuario, sorteio.id_sorteio AS id_sorteio, sorteio.nome AS nome_sorteio, valor_por_bilhete,SUM(valor_por_bilhete) AS valor_convertido
    FROM sorteio
    INNER JOIN bilhete 
    ON bilhete.id_sorteio = sorteio.id_sorteio
	WHERE id_usuario = ?
    GROUP BY nome_sorteio

),
tabela_usuario AS (
SELECT vendas_sorteio.nome_sorteio,vendas_sorteio.id_sorteio, vendas_sorteio.id_usuario,total_comprado,valor_convertido
FROM vendas_sorteio
LEFT JOIN vendas_convertidas
ON vendas_sorteio.id_sorteio = vendas_convertidas.id_sorteio AND vendas_sorteio.id_usuario = vendas_convertidas.id_usuario
)
SELECT id_usuario, sorteio.id_sorteio, nome_sorteio,data_limite,COALESCE(total_comprado,0) AS total_comprado, valor_por_bilhete, COALESCE(valor_convertido,0) AS valor_convertido,
	CASE 
		WHEN total_comprado - COALESCE(valor_convertido,0) > valor_por_bilhete  THEN 1
		ELSE 0
	END AS pode_depositar
FROM tabela_usuario
FULL JOIN sorteio
ON sorteio.id_sorteio = tabela_usuario.id_sorteio