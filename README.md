# ProjetoOFX

O ProjetoOFX é um sistema desenvolvido em Python para importar extratos bancários no formato OFX, armazenar as movimentações em um banco de dados PostgreSQL e facilitar a consulta dessas informações diretamente pelo terminal.

O projeto automatiza a leitura dos extratos e organiza as transações financeiras, permitindo consultar entradas, saídas e categorias. Além disso, o usuário pode alterar manualmente a classificação de uma movimentação quando a categoria atribuída automaticamente não estiver correta.

## Como funciona

O sistema lê o arquivo `extrato.ofx` utilizando a biblioteca `ofxparse` e recupera a data, o valor e a descrição de cada movimentação.

Cada transação recebe inicialmente uma categoria com base nas palavras encontradas em sua descrição. Por exemplo, uma movimentação que contém “SUPERMERCADO” pode ser classificada como Alimentação, enquanto uma que contém “NETFLIX” pode ser classificada como Assinaturas.

Os dados são armazenados no PostgreSQL, utilizando a biblioteca `psycopg2` para realizar a comunicação entre Python e banco de dados.

O sistema também verifica se uma movimentação já existe antes de inseri-la, evitando a duplicação de registros com a mesma data, valor e descrição durante a importação.

Caso uma transação receba uma categoria incorreta, o usuário pode acessar a opção de alteração de classificação e escolher manualmente a categoria desejada.

## Funcionalidades

- **Importar extrato OFX:** lê o arquivo e salva as novas movimentações no banco de dados.
- **Listar movimentações:** exibe os registros cadastrados, incluindo data, descrição, valor e categoria.
- **Consultar por categoria:** permite visualizar as movimentações de uma categoria específica.
- **Ver resumo financeiro:** apresenta o total de entradas, o total de saídas, o saldo calculado e a quantidade de movimentações.
- **Pesquisar por descrição:** procura transações utilizando uma palavra ou trecho da descrição.
- **Alterar classificação:** permite selecionar uma movimentação cadastrada e modificar manualmente sua categoria.
- **Sair:** encerra a execução do programa.

## Navegação do sistema

Ao executar o arquivo `mainVs2.py`, o sistema apresenta um menu interativo no terminal, com as opções disponíveis:

```text
========================================
       SISTEMA DE EXTRATOS OFX
========================================
1. Importar extrato OFX
2. Listar movimentações
3. Consultar por categoria
4. Ver resumo financeiro
5. Pesquisar por descrição
6. Alterar classificação
7. Sair
========================================
```

### Como funciona a navegação

O usuário navega pelo sistema digitando o número correspondente à opção desejada e pressionando `Enter`.

1. **Importar extrato OFX:** realiza a leitura do arquivo OFX e importa as movimentações para o banco de dados.
2. **Listar movimentações:** apresenta as transações financeiras já cadastradas.
3. **Consultar por categoria:** permite consultar as transações de acordo com a categoria.
4. **Ver resumo financeiro:** apresenta os totais calculados a partir das movimentações registradas.
5. **Pesquisar por descrição:** localiza transações por meio de palavras ou trechos presentes na descrição.
6. **Alterar classificação:** permite escolher uma movimentação pelo seu identificador e selecionar uma nova categoria para ela.
7. **Sair:** encerra o programa.

Após realizar uma operação, o usuário pode continuar utilizando o menu para executar outras funcionalidades sem precisar iniciar o programa novamente.

## Tecnologias utilizadas

- **Python:** linguagem utilizada para desenvolver a aplicação.
- **PostgreSQL:** banco de dados utilizado para armazenar as movimentações financeiras.
- **Psycopg2:** biblioteca responsável pela comunicação entre Python e PostgreSQL.
- **Ofxparse:** biblioteca utilizada para interpretar os arquivos OFX.
- **DBeaver:** ferramenta utilizada para visualizar e consultar os dados do banco.

## Estrutura do banco de dados

As movimentações são armazenadas na tabela `movimentacoes`, com os seguintes campos:

| Campo | Finalidade |
|---|---|
| `id` | Identifica cada registro |
| `data_movimentacao` | Armazena a data da transação |
| `valor` | Armazena o valor da movimentação |
| `descricao` | Guarda a descrição encontrada no extrato |
| `categoria` | Armazena a classificação atribuída ou definida pelo usuário |

## Como executar o projeto

### 1. Preparar o ambiente

É necessário ter Python e PostgreSQL instalados. O DBeaver pode ser utilizado para visualizar os dados e executar comandos SQL.

Na pasta do projeto, crie o ambiente virtual:

```bash
python -m venv venv
```

Ative o ambiente virtual no Windows:

```bash
venv\Scripts\activate
```

Instale as bibliotecas utilizadas:

```bash
python -m pip install ofxparse psycopg2-binary
```

### 2. Configurar o banco de dados

No PostgreSQL, crie a tabela utilizada pelo programa:

```sql
CREATE TABLE IF NOT EXISTS movimentacoes (
    id SERIAL PRIMARY KEY,
    data_movimentacao DATE,
    valor NUMERIC(15, 2),
    descricao VARCHAR(255),
    categoria VARCHAR(100)
);
```

Se a tabela já existir sem a coluna `categoria`, adicione-a:

```sql
ALTER TABLE movimentacoes
ADD COLUMN IF NOT EXISTS categoria VARCHAR(100);
```

Confira os dados de conexão no arquivo `mainVs2.py` e ajuste o usuário, a senha e o banco de dados conforme sua instalação.

### 3. Adicionar o extrato

Coloque o arquivo OFX na mesma pasta do arquivo `mainVs2.py`, com o nome:

```text
extrato.ofx
```

Verifique se o nome do arquivo corresponde ao caminho definido no código.

### 4. Iniciar o programa

Com o ambiente virtual ativado, execute:

```bash
python mainVs2.py
```

O menu será exibido no terminal. Digite o número da opção desejada e pressione `Enter` para executar a funcionalidade.

## Observações

- A classificação automática das movimentações é feita por palavras-chave definidas no código. Descrições diferentes das previstas podem não receber a categoria esperada.
- A classificação de uma movimentação pode ser alterada manualmente pelo usuário.
- A verificação de duplicatas considera data, valor e descrição. Duas transações legítimas com esses mesmos dados podem ser interpretadas como duplicadas.
- O resumo financeiro considera valores positivos como entradas e valores negativos como saídas.
- As credenciais do PostgreSQL devem ser protegidas e não devem ser publicadas em um repositório público.
- Extratos bancários podem conter informações financeiras pessoais. Utilize arquivos de teste ou anonimizados ao compartilhar o projeto publicamente.

## Autor

**Isadora Cabral dos Santos** — RA 25001227
