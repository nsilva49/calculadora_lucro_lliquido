"""
Calculadora de Lucro Líquido
----------------------------
Aplicação desktop em Python (Tkinter) para calcular o resultado de uma operação
de compra e venda de produtos.

Regras de cálculo (valem para toda a operação):
    receita      = preço de venda (unid.) x quantidade
    custo total  = preço de compra (unid.) x quantidade + frete (total) + custos adicionais (total)
    lucro        = receita - custo total
    margem       = lucro / receita x 100

Os produtos salvos aparecem na tabela e no gráfico de barras (Matplotlib).

Como rodar:
    python -m pip install -r requirements.txt
    python app.py

Os ícones são opcionais. Se quiser usá-los, coloque os arquivos .png na pasta "icons".
"""

import math
import os
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------------------------------------------------------------------
# Cores
# ----------------------------------------------------------------------
co0 = "#2e2d2b"   # preta
co1 = "#feffff"   # branca
co2 = "#4fa882"   # verde (lucro positivo)
co3 = "#38576b"   # azul acinzentado (custo)
co4 = "#403d3d"   # letra
co6 = "#038cfc"   # azul
co9 = "#e9edf5"   # cinza claro (fundo dos painéis)
co13 = "#FF0000"  # vermelho (prejuízo)
co14 = "#00008b"  # azul escuro

# ----------------------------------------------------------------------
# Caminhos (relativos à pasta do projeto, funcionam em qualquer computador)
# ----------------------------------------------------------------------
PASTA = os.path.dirname(os.path.abspath(__file__))
ICONES = os.path.join(PASTA, "icons")


# ----------------------------------------------------------------------
# Funções de cálculo e formatação (não dependem da interface)
# ----------------------------------------------------------------------
def numero(texto, campo, obrigatorio=True):
    """Converte o texto digitado em número. Aceita '12,50' e '12.50'."""
    texto = texto.strip().replace("R$", "").replace(" ", "")
    if texto == "":
        if obrigatorio:
            raise ValueError(f'Preencha o campo "{campo}".')
        return 0.0
    if "," in texto:  # formato brasileiro: 1.234,56
        texto = texto.replace(".", "").replace(",", ".")
    try:
        valor = float(texto)
    except ValueError:
        raise ValueError(f'O campo "{campo}" precisa ser um número (ex.: 12,50).') from None
    if not math.isfinite(valor):
        raise ValueError(f'O campo "{campo}" precisa ser um número (ex.: 12,50).')
    if valor < 0:
        raise ValueError(f'O campo "{campo}" não pode ser negativo.')
    return valor


def calcular_operacao(compra, venda, frete, custos_adicionais, quantidade):
    """Retorna receita, custo total, lucro líquido e margem de lucro (%)."""
    receita = venda * quantidade
    custo_total = compra * quantidade + frete + custos_adicionais
    lucro = receita - custo_total
    margem = (lucro / receita * 100) if receita > 0 else 0.0
    return receita, custo_total, lucro, margem


def moeda(valor):
    """Formata como moeda brasileira: R$ 1.234,56."""
    sinal = "-" if valor < 0 else ""
    texto = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sinal}R$ {texto}"


def percentual(valor):
    return f"{valor:.1f}".replace(".", ",") + "%"


# ----------------------------------------------------------------------
# Janela principal
# ----------------------------------------------------------------------
janela = tk.Tk()
janela.title("Calculadora de Lucro Líquido")
janela.geometry("1000x620")
janela.configure(background=co1)
janela.resizable(width=True, height=True)

style = ttk.Style(janela)
style.theme_use("clam")


def carregar_icone(nome, tamanho):
    """Carrega um ícone da pasta 'icons'. Se não existir, o programa segue sem ele."""
    try:
        imagem = Image.open(os.path.join(ICONES, nome)).resize(tamanho)
        return ImageTk.PhotoImage(imagem)
    except (FileNotFoundError, OSError):
        return None


img_logo = carregar_icone("icons8-saco-de-dinheiro-64.png", (50, 50))
img_calcular = carregar_icone("Paomedia-Small-N-Flat-Calculator.512.png", (20, 20))
img_salvar = carregar_icone("icons8-salvar-48.png", (20, 20))
img_deletar = carregar_icone("icons8-deletar-30.png", (20, 20))

# ----------------------------------------------------------------------
# Divisão da janela em partes (Frames)
# ----------------------------------------------------------------------
titulo = tk.Frame(janela, width=1000, height=75, bg=co1)
titulo.grid(row=0, column=0, columnspan=2)

sub_titulo = tk.Frame(janela, width=380, height=400, bg=co1)
sub_titulo.grid(row=2, column=0, pady=10)

tabela1 = tk.Frame(janela, width=900, height=200, bg=co9)
tabela1.grid(row=3, column=0, pady=5)

detalhe_produto = tk.Frame(sub_titulo, width=300, height=320, bg=co9)
detalhe_produto.grid(row=0, column=1, padx=3)

resultado_operacao = tk.Frame(sub_titulo, width=300, height=320, bg=co9)
resultado_operacao.grid(row=0, column=2, padx=3)

estatistica_produto = tk.Frame(sub_titulo, width=300, height=320, bg=co9)
estatistica_produto.grid(row=0, column=3, padx=3)

# ----------------------------------------------------------------------
# Título
# ----------------------------------------------------------------------
if img_logo:
    tk.Label(titulo, image=img_logo, bg=co1).place(x=5, y=0)
    x_titulo = 65
else:
    x_titulo = 10

tk.Label(titulo, text="Calculadora de Lucro Líquido", font=("Ivy", 12, "bold"),
         bg=co1, fg=co14).place(x=x_titulo, y=12)

# Linha fina abaixo do título
linha = tk.Canvas(titulo, width=1000, height=2, bg="lightgray", highlightthickness=0)
linha.place(x=0, y=47)
linha.create_line(0, 1, 1000, 1, fill=co6)


def subtitulo(pai, texto):
    tk.Label(pai, text=texto, width=28, height=1, padx=10, anchor="nw",
             font=("Verdana", 11), bg=co1, fg=co14).place(x=0, y=0)


# ----------------------------------------------------------------------
# Detalhes do produto (entradas)
# ----------------------------------------------------------------------
subtitulo(detalhe_produto, "Detalhes do Produto")


def criar_campo(pai, texto, x, y, largura):
    tk.Label(pai, text=texto, anchor="w", font=("Verdana", 9),
             bg=co9, fg=co0).place(x=x, y=y)
    entrada = tk.Entry(pai, width=largura, font=("Ivy", 10), justify="center", relief="groove")
    entrada.place(x=x, y=y + 20)
    return entrada


e_produto = criar_campo(detalhe_produto, "Nome do Produto", 10, 30, 20)
e_compra = criar_campo(detalhe_produto, "Preço compra (un.)", 10, 80, 10)
e_frete = criar_campo(detalhe_produto, "Frete (total)", 10, 130, 10)

e_quantidade = criar_campo(detalhe_produto, "Quantidade", 170, 30, 7)
e_venda = criar_campo(detalhe_produto, "Preço venda (un.)", 170, 80, 10)
e_custos = criar_campo(detalhe_produto, "Custos adic. (total)", 170, 130, 10)

tk.Label(detalhe_produto,
         text="Frete e custos adicionais: informe o valor total da operação "
              "(deixe em branco se não houver).",
         font=("Verdana", 7), bg=co9, fg=co4, wraplength=150, justify="left",
         anchor="w").place(x=10, y=190)

# ----------------------------------------------------------------------
# Resultado da operação
# ----------------------------------------------------------------------
subtitulo(resultado_operacao, "Resultado da Operação")


def criar_resultado(pai, texto, y):
    tk.Label(pai, text=texto, font=("Verdana", 9), bg=co9, fg=co0).place(x=20, y=y)
    valor = tk.Label(pai, text="", font=("Verdana", 14, "bold"), bg=co9, fg=co14)
    valor.place(x=20, y=y + 22)
    return valor


lbl_custo = criar_resultado(resultado_operacao, "Custo total", 50)
lbl_lucro = criar_resultado(resultado_operacao, "Lucro líquido", 120)
lbl_margem = criar_resultado(resultado_operacao, "Margem de lucro", 190)


def limpar_resultados():
    lbl_custo["text"] = moeda(0)
    lbl_lucro["text"] = moeda(0)
    lbl_lucro["fg"] = co14
    lbl_margem["text"] = percentual(0)


# ----------------------------------------------------------------------
# Estatística dos produtos (gráfico)
# ----------------------------------------------------------------------
subtitulo(estatistica_produto, "Estatística dos Produtos")

figura = Figure(figsize=(2.7, 2.7), dpi=100)
eixo = figura.add_subplot(111)
canvas_grafico = FigureCanvasTkAgg(figura, master=estatistica_produto)
canvas_grafico.get_tk_widget().place(x=15, y=35)

# Lista com os produtos salvos (valores numéricos, usados no gráfico)
registros = []


def atualizar_grafico():
    """Redesenha o gráfico com a soma de todos os produtos salvos."""
    eixo.clear()
    if registros:
        custo = sum(r["custo_total"] for r in registros)
        lucro = sum(r["lucro"] for r in registros)
        receita = sum(r["receita"] for r in registros)
        margem = (lucro / receita * 100) if receita > 0 else 0.0

        barras = eixo.bar(["Custo\ntotal", "Lucro\nlíquido"], [custo, lucro],
                          color=[co3, co2 if lucro >= 0 else co13])
        eixo.bar_label(barras, labels=[moeda(custo), moeda(lucro)], fontsize=7, padding=2)
        eixo.set_title(f"Margem do conjunto: {percentual(margem)}", fontsize=9, color=co14)
        eixo.margins(y=0.2)
    else:
        eixo.set_title("Salve um produto para ver o gráfico", fontsize=8)
        eixo.set_xticks([])
        eixo.set_yticks([])

    eixo.set_ylabel("R$", fontsize=8)
    eixo.tick_params(labelsize=8)
    figura.tight_layout()
    canvas_grafico.draw()


# ----------------------------------------------------------------------
# Tabela (Treeview)
# ----------------------------------------------------------------------
colunas = (
    ("Nome do Produto", 140),
    ("Qtd", 50),
    ("Compra(R$)", 100),
    ("Venda(R$)", 100),
    ("Frete(R$)", 90),
    ("Custos adic.(R$)", 125),
    ("Custo total(R$)", 110),
    ("Lucro(R$)", 105),
    ("Margem(%)", 80),
)

tabela = ttk.Treeview(tabela1, selectmode="browse",
                      columns=[nome for nome, _ in colunas],
                      show="headings", height=5)
for nome, largura in colunas:
    tabela.column(nome, width=largura, minwidth=40, stretch=False, anchor="center")
    tabela.heading(nome, text=nome, anchor="center")

barra_rolagem = ttk.Scrollbar(tabela1, orient="vertical", command=tabela.yview)
tabela.configure(yscrollcommand=barra_rolagem.set)
tabela.grid(row=0, column=0)
barra_rolagem.grid(row=0, column=1, sticky="ns")


# ----------------------------------------------------------------------
# Ações dos botões
# ----------------------------------------------------------------------
def calcular():
    """Lê os campos, mostra o resultado e devolve os valores (ou None se houver erro)."""
    try:
        compra = numero(e_compra.get(), "Preço de compra")
        venda = numero(e_venda.get(), "Preço de venda")
        quantidade = numero(e_quantidade.get(), "Quantidade")
        frete = numero(e_frete.get(), "Frete", obrigatorio=False)
        custos = numero(e_custos.get(), "Custos adicionais", obrigatorio=False)
        if quantidade <= 0:
            raise ValueError("A quantidade precisa ser maior que zero.")
        if venda <= 0:
            raise ValueError("O preço de venda precisa ser maior que zero.")
    except ValueError as erro:
        messagebox.showerror("Erro", str(erro))
        return None

    receita, custo_total, lucro, margem = calcular_operacao(compra, venda, frete, custos, quantidade)

    lbl_custo["text"] = moeda(custo_total)
    lbl_lucro["text"] = moeda(lucro)
    lbl_lucro["fg"] = co13 if lucro < 0 else co14
    lbl_margem["text"] = percentual(margem)

    return {
        "quantidade": quantidade, "compra": compra, "venda": venda,
        "frete": frete, "custos": custos, "receita": receita,
        "custo_total": custo_total, "lucro": lucro, "margem": margem,
    }


def salvar():
    """Calcula com os valores atuais, adiciona na tabela e atualiza o gráfico."""
    nome = e_produto.get().strip()
    if not nome:
        messagebox.showerror("Erro", 'Preencha o campo "Nome do Produto".')
        return

    resultado = calcular()
    if resultado is None:
        return

    resultado["nome"] = nome
    registros.append(resultado)

    tabela.insert("", "end", values=(
        nome,
        f"{resultado['quantidade']:g}",
        moeda(resultado["compra"]),
        moeda(resultado["venda"]),
        moeda(resultado["frete"]),
        moeda(resultado["custos"]),
        moeda(resultado["custo_total"]),
        moeda(resultado["lucro"]),
        percentual(resultado["margem"]),
    ))
    atualizar_grafico()


def deletar():
    """Limpa os campos e o resultado (a tabela e o gráfico continuam)."""
    for entrada in (e_produto, e_compra, e_venda, e_frete, e_custos, e_quantidade):
        entrada.delete(0, tk.END)
    limpar_resultados()


# ----------------------------------------------------------------------
# Botões
# ----------------------------------------------------------------------
def criar_botao(texto, comando, icone, y):
    opcoes = dict(command=comando, text=texto, padx=10, font=("Ivy", 11, "bold"),
                  bg=co1, fg=co0)
    if icone:
        opcoes.update(image=icone, compound="left", width=80, anchor="e")
    else:
        opcoes.update(width=10)
    botao = tk.Button(detalhe_produto, **opcoes)
    botao.place(x=170, y=y)
    return botao


criar_botao("Calcular", calcular, img_calcular, 200)
criar_botao("Salvar", salvar, img_salvar, 240)
criar_botao("Deletar", deletar, img_deletar, 280)

janela.bind("<Return>", lambda evento: calcular())

# ----------------------------------------------------------------------
# Estado inicial e início do programa
# ----------------------------------------------------------------------
limpar_resultados()
atualizar_grafico()
janela.mainloop()
