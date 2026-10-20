from ofxparse import OfxParser
import psycopg2


# Conecta ao banco de dados
def conectar_banco():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="unifeob@123"
    )


# Classifica as movimentações por categoria
def classificar_transacao(descricao, valor):
    descricao = (descricao or "").upper()

    categorias = {
        "Alimentação": [
            "SUPERMERCADO", "MERCADO", "PADARIA",
            "RESTAURANTE", "LANCHONETE", "IFOOD"
        ],
        "Moradia": [
            "ENERGIA", "AGUA", "ALUGUEL",
            "GAS", "SABESP", "ELEKTRO"
        ],
        "Transporte": [
            "UBER", "99APP", "POSTO",
            "COMBUSTIVEL", "ESTACIONAMENTO"
        ],
        "Saúde": [
            "FARMACIA", "DROGARIA", "HOSPITAL",
            "CLINICA", "LABORATORIO"
        ],
        "Assinaturas": [
            "NETFLIX", "SPOTIFY", "DISNEY",
            "AMAZON PRIME"
        ],
        "Salário": [
            "SALARIO", "PAGAMENTO SALARIAL",
            "FOLHA DE PAGAMENTO"
        ],
        "Transferência": [
            "PIX", "TED", "DOC", "TRANSFERENCIA"
        ]
    }

    for categoria, palavras in categorias.items():
        if any(palavra in descricao for palavra in palavras):
            return categoria

    if valor > 0:
        return "Outras entradas"

    return "Outras saídas"


# Importa as movimentações do arquivo OFX
def importar_extrato():
    conexao = None
    cursor = None

    try:
        with open("extrato.ofx", "rb") as arquivo:
            ofx = OfxParser.parse(arquivo)

        transacoes = ofx.account.statement.transactions

        conexao = conectar_banco()
        cursor = conexao.cursor()

        novas = 0

        for t in transacoes:
            descricao = t.memo or "Sem descrição"
            categoria = classificar_transacao(
                descricao, t.amount
            )

            # Insere somente movimentações que ainda não existem
            cursor.execute(
                """
                INSERT INTO movimentacoes
                    (data_movimentacao, valor, descricao, categoria)
                SELECT %s, %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM movimentacoes
                    WHERE data_movimentacao = %s
                      AND valor = %s
                      AND descricao = %s
                )
                """,
                (
                    t.date.date(),
                    t.amount,
                    descricao,
                    categoria,
                    t.date.date(),
                    t.amount,
                    descricao
                )
            )

            if cursor.rowcount > 0:
                novas += 1

        # Classifica movimentações antigas sem categoria
        cursor.execute(
            """
            SELECT id, descricao, valor
            FROM movimentacoes
            WHERE categoria IS NULL
            """
        )

        antigas = cursor.fetchall()

        for id_movimentacao, descricao, valor in antigas:
            categoria = classificar_transacao(
                descricao, valor
            )

            cursor.execute(
                """
                UPDATE movimentacoes
                SET categoria = %s
                WHERE id = %s
                """,
                (categoria, id_movimentacao)
            )

        conexao.commit()

        print("\n========== IMPORTAÇÃO ==========")
        print("Importação concluída!")
        print("Transações encontradas:", len(transacoes))
        print("Novas movimentações salvas:", novas)
        print(
            "Movimentações antigas classificadas:",
            len(antigas)
        )

    except FileNotFoundError:
        print("\nArquivo extrato.ofx não encontrado!")
        print("Coloque o arquivo na pasta do projeto.")

    except Exception as erro:
        if conexao:
            conexao.rollback()

        print("\nErro ao importar:", erro)

    finally:
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Lista todas as movimentações cadastradas
def listar_movimentacoes():
    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT id, data_movimentacao, descricao,
                   valor, categoria
            FROM movimentacoes
            ORDER BY data_movimentacao DESC, id DESC
            """
        )

        registros = cursor.fetchall()

        print("\n========== MOVIMENTAÇÕES ==========\n")

        if not registros:
            print("Nenhuma movimentação encontrada.")

        for id_mov, data, descricao, valor, categoria in registros:
            print("-" * 45)
            print("ID:", id_mov)
            print("Data:", data.strftime("%d/%m/%Y"))
            print("Descrição:", descricao)
            print(f"Valor: R$ {valor:.2f}")
            print("Categoria:", categoria or "Sem categoria")

        print("-" * 45)
        print("Total de registros:", len(registros))

    except Exception as erro:
        print("\nErro ao listar movimentações:", erro)

    finally:
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Consulta movimentações por categoria
def consultar_categoria():
    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT DISTINCT categoria
            FROM movimentacoes
            WHERE categoria IS NOT NULL
            ORDER BY categoria
            """
        )

        categorias = [linha[0] for linha in cursor.fetchall()]

        if not categorias:
            print("\nNenhuma categoria encontrada.")
            return

        print("\n========== CATEGORIAS ==========\n")

        for i, categoria in enumerate(categorias, start=1):
            print(f"{i}. {categoria}")

        try:
            escolha = int(input("\nEscolha uma categoria: "))
        except ValueError:
            print("Digite um número válido.")
            return

        if escolha < 1 or escolha > len(categorias):
            print("Opção inválida.")
            return

        categoria_escolhida = categorias[escolha - 1]

        cursor.execute(
            """
            SELECT data_movimentacao, descricao, valor
            FROM movimentacoes
            WHERE categoria = %s
            ORDER BY data_movimentacao DESC
            """,
            (categoria_escolhida,)
        )

        registros = cursor.fetchall()

        print(
            f"\n========== {categoria_escolhida.upper()} ==========\n"
        )

        for data, descricao, valor in registros:
            print(
                f"{data.strftime('%d/%m/%Y')} | "
                f"{descricao} | R$ {valor:.2f}"
            )

        print("\nQuantidade de movimentações:", len(registros))

    except Exception as erro:
        print("\nErro ao consultar categoria:", erro)

    finally:
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Exibe o resumo financeiro das movimentações
def resumo_financeiro():
    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT
                COALESCE(
                    SUM(CASE WHEN valor > 0
                        THEN valor ELSE 0 END), 0
                ),
                COALESCE(
                    SUM(CASE WHEN valor < 0
                        THEN ABS(valor) ELSE 0 END), 0
                ),
                COUNT(*)
            FROM movimentacoes
            """
        )

        entradas, saidas, quantidade = cursor.fetchone()
        saldo = entradas - saidas

        print("\n========== RESUMO FINANCEIRO ==========\n")
        print(f"Total de entradas: R$ {entradas:.2f}")
        print(f"Total de saídas:  R$ {saidas:.2f}")
        print(f"Saldo calculado:  R$ {saldo:.2f}")
        print(f"Movimentações:    {quantidade}")
        print("\n=======================================")

    except Exception as erro:
        print("\nErro ao gerar resumo:", erro)

    finally:
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Pesquisa movimentações pela descrição
def pesquisar_movimentacoes():
    termo = input(
        "\nDigite uma palavra da descrição: "
    ).strip()

    if not termo:
        print("Digite um termo para pesquisar.")
        return

    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT data_movimentacao, descricao, valor, categoria
            FROM movimentacoes
            WHERE descricao ILIKE %s
            ORDER BY data_movimentacao DESC
            """,
            (f"%{termo}%",)
        )

        registros = cursor.fetchall()

        print("\n========== RESULTADO DA PESQUISA ==========\n")

        for data, descricao, valor, categoria in registros:
            print(
                f"{data.strftime('%d/%m/%Y')} | "
                f"{descricao} | R$ {valor:.2f} | "
                f"{categoria or 'Sem categoria'}"
            )

        if not registros:
            print("Nenhuma movimentação encontrada.")

        print("\nTotal de resultados:", len(registros))

    except Exception as erro:
        print("\nErro ao pesquisar movimentações:", erro)

    finally:
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Permite ao usuário alterar a classificação de uma movimentação
def alterar_classificacao():
    conexao = None
    cursor = None

    categorias = [
        "Alimentação",
        "Moradia",
        "Transporte",
        "Saúde",
        "Assinaturas",
        "Salário",
        "Transferência",
        "Outras entradas",
        "Outras saídas"
    ]

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT id, data_movimentacao, descricao,
                   valor, categoria
            FROM movimentacoes
            ORDER BY data_movimentacao DESC, id DESC
            """
        )

        registros = cursor.fetchall()

        print("\n========== ALTERAR CLASSIFICAÇÃO ==========\n")

        if not registros:
            print("Nenhuma movimentação encontrada.")
            return

        # Mostra as movimentações para o usuário escolher
        for id_mov, data, descricao, valor, categoria in registros:
            print("-" * 45)
            print("ID:", id_mov)
            print("Data:", data.strftime("%d/%m/%Y"))
            print("Descrição:", descricao)
            print(f"Valor: R$ {valor:.2f}")
            print("Categoria atual:", categoria or "Sem categoria")

        try:
            id_escolhido = int(
                input("\nDigite o ID da movimentação que deseja alterar: ")
            )
        except ValueError:
            print("Digite um ID numérico válido.")
            return

        # Verifica se a movimentação existe
        cursor.execute(
            """
            SELECT id, categoria
            FROM movimentacoes
            WHERE id = %s
            """,
            (id_escolhido,)
        )

        movimentacao = cursor.fetchone()

        if movimentacao is None:
            print("Movimentação não encontrada.")
            return

        print("\nCategoria atual:", movimentacao[1] or "Sem categoria")
        print("\nEscolha a nova classificação:")

        for i, categoria in enumerate(categorias, start=1):
            print(f"{i}. {categoria}")

        try:
            escolha = int(
                input("\nDigite o número da nova categoria: ")
            )
        except ValueError:
            print("Digite um número válido.")
            return

        if escolha < 1 or escolha > len(categorias):
            print("Opção inválida.")
            return

        nova_categoria = categorias[escolha - 1]

        # Salva a nova classificação no banco
        cursor.execute(
            """
            UPDATE movimentacoes
            SET categoria = %s
            WHERE id = %s
            """,
            (nova_categoria, id_escolhido)
        )

        conexao.commit()

        print("\nClassificação alterada com sucesso!")
        print("Nova categoria:", nova_categoria)

    except Exception as erro:
        if conexao:
            conexao.rollback()

        print("\nErro ao alterar classificação:", erro)

    finally:
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Mostra as opções depois de cada operação
def navegar_apos_resultado():
    while True:
        print("\nO que deseja fazer?")
        print("1. Nova consulta")
        print("2. Voltar à página inicial")
        print("0. Sair do sistema")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            return "consulta"

        elif opcao == "2":
            return "inicio"

        elif opcao == "0":
            return "sair"

        else:
            print("Opção inválida. Tente novamente.")


# Exibe o menu principal e permite navegar pelo sistema
def menu():
    while True:
        print("\n" + "=" * 42)
        print("       SISTEMA DE EXTRATOS OFX")
        print("=" * 42)
        print("1. Importar extrato OFX")
        print("2. Listar movimentações")
        print("3. Consultar por categoria")
        print("4. Ver resumo financeiro")
        print("5. Pesquisar por descrição")
        print("6. Alterar classificação")
        print("0. Sair")
        print("=" * 42)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            print("\nSistema encerrado. Até mais!")
            break

        elif opcao in ["1", "2", "3", "4", "5", "6"]:
            while True:
                if opcao == "1":
                    importar_extrato()

                elif opcao == "2":
                    listar_movimentacoes()

                elif opcao == "3":
                    consultar_categoria()

                elif opcao == "4":
                    resumo_financeiro()

                elif opcao == "5":
                    pesquisar_movimentacoes()

                elif opcao == "6":
                    alterar_classificacao()

                navegacao = navegar_apos_resultado()

                if navegacao == "consulta":
                    # Repete a mesma operação
                    continue

                elif navegacao == "inicio":
                    break

                elif navegacao == "sair":
                    print("\nSistema encerrado. Até mais!")
                    return

        else:
            print("\nOpção inválida. Tente novamente.")


# Inicia o sistema
if __name__ == "__main__":
    menu()