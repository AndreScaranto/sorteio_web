# sorteio_web
Sistema Web para Gerenciar e Operacionalizar um Sorteio.


## Como rodar
- Certifique-se de ter o Python instalado no computador. Se não estiver instalado, acesse : [Download do Python](https://www.python.org/downloads/)
- Abra um Windows PowerShell (pesquise na barra de início)
- No terminal PowerShell aberto, execute o comando 'python --version' para verificar se o python está instalado corretamente - ele deve responder com "Python 3.12.6" ou com qualquer que seja a versão atual do Python no seu computador
- faça o download ou o clone do repositório do aplicativo em alguma pasta local no computador
- no terminal PowerShell, navegue até a pasta local do aplicativo usando o comando 'cd *' em que * é o diretório / pasta que se deseja acessar
- uma vez na pasta raiz "sorteio_web" ou "sorteio_web-main", execute o comando 'ambiente\scripts\activate.bat' para ativar o ambiente de instalação de pacotes local, que contem o Flask e as demais dependências necessárias para rodar o aplicativo
- depois execute 'flask --app flaskr run --debug' que vai rodar o aplicativo no computador local
- agora basta abrir um navegador e acessar o endereço local em que o Flask estará rodando: [http://127.0.0.1:5000](http://127.0.0.1:5000)