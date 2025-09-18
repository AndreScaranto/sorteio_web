DROP TABLE IF EXISTS administrador;
DROP TABLE IF EXISTS bilhete;
DROP TABLE IF EXISTS codigo;
DROP TABLE IF EXISTS sorteio;

CREATE TABLE administrador (
  id_admin INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
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