DROP TABLE IF EXISTS administrador;
DROP TABLE IF EXISTS bilhete;
DROP TABLE IF EXISTS codigo;
DROP TABLE IF EXISTS sorteio;
DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS produto;
DROP TABLE IF EXISTS venda;

CREATE TABLE administrador (
  id_admin INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);


CREATE TABLE usuario (
  id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  CPF INTEGER NOT NULL,
  celular INTEGER NOT NULL
);

CREATE TABLE bilhete (
  id_bilhete INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo INTEGER UNIQUE NOT NULL,
  nome TEXT NOT NULL,
  sobrenome TEXT NOT NULL,
  celular TEXT NOT NULL,
  id_sorteio INTEGER NOT NULL,
  FOREIGN KEY (id_sorteio) REFERENCES sorteio(id_sorteio)
);

CREATE TABLE codigo (
  id_codigo INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo INTEGER NOT NULL,
  id_sorteio INTEGER NOT NULL,
  FOREIGN KEY (id_sorteio) REFERENCES sorteio(id_sorteio)
);

CREATE TABLE sorteio (
  id_sorteio INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT UNIQUE NOT NULL,
  data_limite TIMESTAMP NOT NULL,
  realizado BOOLEAN DEFAULT 0,
  id_bilhete_sorteado INTEGER DEFAULT NULL,
  FOREIGN KEY (id_bilhete_sorteado) REFERENCES bilhete(id_bilhete),
  CHECK ((NOT realizado) OR id_bilhete_sorteado)
);

CREATE TABLE produto (
  id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT UNIQUE NOT NULL,
  preco_atual DECIMAL(10,2) NOT NULL,
  ativo BOOLEAN DEFAULT 1
);

CREATE TABLE venda (
  id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
  data_venda TIMESTAMP NOT NULL,
  id_usuario INTEGER NOT NULL,
  id_produto INTEGER NOT NULL,
  preco_venda DECIMAL(10,2) NOT NULL,
  desconto_unitario DECIMAL(10,2) DEFAULT 0,
  quantidade_vendida INTEGER NOT NULL,
  FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
  FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
);