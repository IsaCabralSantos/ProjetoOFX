# ProjetoOFX

O ProjetoOFX é um sistema desenvolvido em Python para importar extratos bancários no formato OFX, salvar as movimentações em um banco de dados PostgreSQL e facilitar a consulta dessas informações diretamente pelo terminal.

A ideia do projeto é automatizar o processo de leitura do extrato e organizar as transações financeiras para que seja possível consultar entradas, saídas e categorias sem precisar analisar o arquivo manualmente.

## Como funciona

O sistema lê o arquivo `extrato.ofx` utilizando a biblioteca `ofxparse` e recupera a data, o valor e a descrição de cada movimentação.

Depois da leitura, cada transação recebe uma categoria com base nas palavras encontradas em sua descrição. Por exemplo, uma movimentação cuja descrição contém “SUPERMERCADO” pode ser classificada como Alimentação, enquanto uma que contém “NETFLIX” pode ser classificada como Assinaturas.

Os dados são armazenados no PostgreSQL, utilizando a biblioteca `psycopg2` para realizar a comunicação entre o Python e o banco de dados.

O sistema também verifica se uma movimentação já existe antes de inseri-la, evitando que a importação do mesmo extrato adicione novamente os registros que correspondem à mesma data, valor e descrição.

## Funcionalidades

O programa possui um menu interativo no terminal com as seguintes opções:

- **Importar extrato OFX:** lê o arquivo e salva as novas movimentações no banco de dados.
- **Listar movimentações:** exibe os registros cadastrados, incluindo data, descrição, valor e categoria.
- **Consultar por categoria:** permite selecionar uma categoria e visualizar as movimentações correspondentes.
- **Ver resumo financeiro:** calcula o total de entradas, o total de saídas, o saldo calculado e a quantidade de movimentações.
- **Pesquisar por descrição:** procura transações utilizando uma palavra ou trecho da descrição.
- **Navegar pelo sistema:** depois de cada operação, permite fazer uma nova consulta, voltar ao menu inicial ou encerrar o programa.

Durante a importação, o sistema também identifica movimentações antigas que ainda estão sem categoria e tenta classificá-las automaticamente.

## Tecnologias utilizadas

- Python
- PostgreSQL
- Psycopg2
- Ofxparse
- DBeaver

## Estrutura do banco de dados

As movimentações são armazenadas na tabela `movimentacoes`, com os seguintes campos:

| Campo | Finalidade |
|---|---|
| `id` | Identifica cada registro |
| `data_movimentacao` | Armazena a data da transação |
| `valor` | Armazena o valor da movimentação |
| `descricao` | Guarda a descrição encontrada no extrato |
| `categoria` | Armazena a classificação atribuída pelo sistema |

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

Coloque o arquivo OFX na mesma pasta do `mainVs2.py`, com o nome:

```text
extrato.ofx
```

### 4. Iniciar o programa

Com o ambiente virtual ativado, execute:

```bash
python mainVs2.py
```

O menu será exibido no terminal. Basta digitar o número da opção desejada e seguir as instruções apresentadas.

## Observações

- A classificação é feita por palavras-chave definidas no código. Descrições diferentes das previstas podem ser classificadas como outras entradas ou outras saídas.
- A verificação de duplicatas considera data, valor e descrição. Duas transações legítimas com esses mesmos dados podem ser interpretadas como duplicadas.
- O resumo financeiro considera valores positivos como entradas e valores negativos como saídas.
- As credenciais do PostgreSQL e os extratos bancários devem ser protegidos e não devem ser publicados em um repositório público.

## Autor

Isadora Cabral dos Santos - RA 25001227