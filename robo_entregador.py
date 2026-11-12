# ROBO ENTREGADOR - comparando A* e Algoritmo Genetico
# Problema: o robo sai de S e precisa chegar em E (casa do cliente).
#   #  = parede (nao passa)
#   .  = rua normal (custo 1)
#   ~  = lama (custo 3)
# Objetivo: chegar em E gastando o MENOR custo possivel.

import heapq
import random

MAPA = [
    "S..#......",
    ".#.#.#####",
    ".#........",
    ".#######.#",
    "......#...",
    "#####.####",
    "......~~..",
    "#########.",
    "E.........",
]
# OBS: o E fica no canto de baixo, veja abaixo onde ele e encontrado

# transforma o mapa em lista de listas para ficar mais facil de mexer
grade = [list(linha) for linha in MAPA]
LINHAS = len(grade)
COLUNAS = len(grade[0])

# acha onde esta o S e o E
inicio = None
fim = None
for i in range(LINHAS):
    for j in range(COLUNAS):
        if grade[i][j] == "S":
            inicio = (i, j)
        if grade[i][j] == "E":
            fim = (i, j)

# movimentos: cima, baixo, esquerda, direita
MOVIMENTOS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def custo_da_casa(pos):
    """Retorna quanto custa entrar na casa."""
    if grade[pos[0]][pos[1]] == "~":
        return 3
    return 1


def posicao_valida(pos):
    """Verifica se esta dentro do mapa e nao e parede."""
    l, c = pos
    if l < 0 or l >= LINHAS or c < 0 or c >= COLUNAS:
        return False
    if grade[l][c] == "#":
        return False
    return True


def distancia(a, b):
    """Distancia de Manhattan (usada como heuristica)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ------------------------------------------------------------
# ALGORITMO A*
# ------------------------------------------------------------
def a_estrela():
    # fila de prioridade: (f, g, posicao)
    fila = []
    heapq.heappush(fila, (distancia(inicio, fim), 0, inicio))
    veio_de = {inicio: None}      # para reconstruir o caminho
    custo_g = {inicio: 0}         # menor custo conhecido ate cada casa
    expandidos = 0

    while fila:
        f, g, atual = heapq.heappop(fila)
        expandidos += 1

        if atual == fim:
            # chegou! reconstroi o caminho de tras pra frente
            caminho = []
            while atual is not None:
                caminho.append(atual)
                atual = veio_de[atual]
            caminho.reverse()
            return caminho, g, expandidos

        for dl, dc in MOVIMENTOS:
            vizinho = (atual[0] + dl, atual[1] + dc)
            if not posicao_valida(vizinho):
                continue
            novo_g = g + custo_da_casa(vizinho)
            if vizinho not in custo_g or novo_g < custo_g[vizinho]:
                custo_g[vizinho] = novo_g
                veio_de[vizinho] = atual
                f_novo = novo_g + distancia(vizinho, fim)
                heapq.heappush(fila, (f_novo, novo_g, vizinho))

    return None, 0, expandidos


# ------------------------------------------------------------
# ALGORITMO GENETICO
# Cada individuo e uma lista de movimentos (0=cima,1=baixo,2=esq,3=dir)
# ------------------------------------------------------------
TAM_CROMOSSOMO = 40
TAM_POPULACAO = 100
GERACOES = 300
TAXA_MUTACAO = 0.05


def criar_individuo():
    return [random.randint(0, 3) for _ in range(TAM_CROMOSSOMO)]


def executar(individuo):
    """Faz o robo andar seguindo os genes. Retorna (caminho, custo, chegou)."""
    pos = inicio
    caminho = [pos]
    custo = 0
    for gene in individuo:
        dl, dc = MOVIMENTOS[gene]
        nova = (pos[0] + dl, pos[1] + dc)
        # se bater na parede, fica parado (mas perde um "passo" do gene)
        if posicao_valida(nova):
            pos = nova
            custo += custo_da_casa(pos)
            caminho.append(pos)
            if pos == fim:
                return caminho, custo, True
    return caminho, custo, False


def calcular_nota(individuo):
    """Quanto MENOR a nota, melhor o individuo."""
    caminho, custo, chegou = executar(individuo)
    if chegou:
        return custo
    # se nao chegou, penaliza pela distancia que faltou
    return custo + 20 * distancia(caminho[-1], fim) + 100


def torneio(populacao, notas):
    # sorteia 3 individuos e pega o melhor
    candidatos = random.sample(range(len(populacao)), 3)
    melhor = candidatos[0]
    for c in candidatos:
        if notas[c] < notas[melhor]:
            melhor = c
    return populacao[melhor]


def cruzamento(pai1, pai2):
    # corte em um ponto
    ponto = random.randint(1, TAM_CROMOSSOMO - 1)
    return pai1[:ponto] + pai2[ponto:]


def mutacao(individuo):
    for i in range(len(individuo)):
        if random.random() < TAXA_MUTACAO:
            individuo[i] = random.randint(0, 3)
    return individuo


def algoritmo_genetico():
    populacao = [criar_individuo() for _ in range(TAM_POPULACAO)]
    melhor_ind = None
    melhor_nota = float("inf")
    historico = []

    for ger in range(GERACOES):
        notas = [calcular_nota(ind) for ind in populacao]

        # guarda o melhor de todos
        for i in range(len(populacao)):
            if notas[i] < melhor_nota:
                melhor_nota = notas[i]
                melhor_ind = populacao[i][:]
        historico.append(melhor_nota)

        # nova geracao (elitismo: o melhor passa direto)
        nova_pop = [melhor_ind[:]]
        while len(nova_pop) < TAM_POPULACAO:
            p1 = torneio(populacao, notas)
            p2 = torneio(populacao, notas)
            filho = cruzamento(p1, p2)
            filho = mutacao(filho)
            nova_pop.append(filho)
        populacao = nova_pop

    caminho, custo, chegou = executar(melhor_ind)
    return caminho, custo, chegou, historico


# ------------------------------------------------------------
# Mostrar o mapa com o caminho
# ------------------------------------------------------------
def mostrar(caminho):
    for i in range(LINHAS):
        linha = ""
        for j in range(COLUNAS):
            if (i, j) in caminho and grade[i][j] not in ("S", "E"):
                linha += "*"
            else:
                linha += grade[i][j]
        print(linha)


# ------------------------------------------------------------
# Programa principal
# ------------------------------------------------------------
if __name__ == "__main__":
    random.seed(42)  # para dar sempre o mesmo resultado

    print("MAPA ORIGINAL:")
    for linha in MAPA:
        print(linha)

    print("\n=== A* ===")
    caminho_a, custo_a, exp = a_estrela()
    print("Custo:", custo_a)
    print("Passos:", len(caminho_a) - 1)
    print("Casas expandidas:", exp)
    mostrar(caminho_a)

    print("\n=== ALGORITMO GENETICO ===")
    caminho_g, custo_g, chegou, hist = algoritmo_genetico()
    if chegou:
        print("Custo:", custo_g)
        print("Passos:", len(caminho_g) - 1)
    else:
        print("O AG nao conseguiu chegar ao destino :(")
    print("Nota na geracao 1:", hist[0])
    print("Nota na geracao", GERACOES, ":", hist[-1])
    mostrar(caminho_g)

    print("\n=== COMPARACAO ===")
    print("A* custo:", custo_a, "| AG custo:", custo_g if chegou else "falhou")
    if chegou and custo_g == custo_a:
        print("O AG achou a mesma solucao otima do A*!")
    elif chegou:
        print("O AG achou uma solucao pior que a otima (diferenca de", custo_g - custo_a, ")")
