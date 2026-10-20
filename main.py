from ofxparse import OfxParser

with open("extrato.ofx", "rb") as arquivo:
    ofx = OfxParser.parse(arquivo)

transacoes = ofx.account.statement.transactions

entradas = 0
saidas = 0

print("=" * 50)
print("             EXTRATO BANCÁRIO")
print("=" * 50)

for t in transacoes:
    print(f"Data      : {t.date.strftime('%d/%m/%Y')}")
    print(f"Valor     : R$ {t.amount:.2f}")
    print(f"Descrição : {t.memo}")
    print("-" * 50)

    if t.amount > 0:
        entradas += t.amount
    else:
        saidas += t.amount

saldo = entradas + saidas

print("\nRESUMO FINANCEIRO")
print("=" * 50)
print(f"Quantidade de movimentações: {len(transacoes)}")
print(f"Total de entradas: R$ {entradas:.2f}")
print(f"Total de saídas:   R$ {abs(saidas):.2f}")
print(f"Saldo calculado:   R$ {saldo:.2f}")
print("=" * 50)
