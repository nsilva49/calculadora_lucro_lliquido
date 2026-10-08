# Calculadora de Lucro Líquido

Aplicação desktop em Python (Tkinter) que calcula o resultado de uma operação de compra e venda de produtos.

## O que faz
- Calcula receita, custo total, lucro líquido e margem de lucro.
- Salva os produtos em uma tabela.
- Mostra um gráfico de barras (Matplotlib) com custo total e lucro líquido.

## Regras de cálculo
- Receita = preço de venda (unid.) x quantidade
- Custo total = preço de compra (unid.) x quantidade + frete (total) + custos adicionais (total)
- Lucro líquido = receita - custo total
- Margem = lucro líquido / receita x 100

## Como rodar
```
python -m pip install -r requirements.txt
python app.py
```

## Tecnologias
Python, Tkinter, Matplotlib, Pillow.

Projeto de estudo.
