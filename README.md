# Soma dos Quadrados com Memória Distribuída (MPI)

Projeto didático em Python utilizando **MPI (`mpi4py`)** para demonstrar o modelo de programação com **memória distribuída**, no qual diferentes processos mantêm espaços de memória independentes e cooperam via troca de mensagens para calcular a soma dos quadrados de `0` até `N - 1`.

---

## Objetivo

Demonstrar na prática que processos MPI possuem dados locais separados e colaboram para resolver um problema computacional de forma distribuída, comparando ao final o resultado obtido com a execução sequencial para validação.

---

## Como Funciona

O fluxo de execução em [`memoria_distribuida.py`](memoria_distribuida.py) segue cinco etapas principais:

1. **Geração e particionamento (Rank 0):** Apenas o processo raiz (`rank == 0`) cria a lista completa `[0, 1, ..., n-1]` e a divide entre todos os processos usando distribuição cíclica (`valores[rank::total_processos]`), garantindo que nenhum elemento seja perdido mesmo quando `n` não é divisível pelo número de processos.
   - *Exemplo* (`valores = [0, 1, 2, 3, 4, 5]` com 3 processos):
     - `rank 0` → `[0, 3]`
     - `rank 1` → `[1, 4]`
     - `rank 2` → `[2, 5]`
2. **Sincronização e distribuição (`scatter`):** Após uma barreira (`Barrier()`), o rank 0 envia a cada processo somente a sua respectiva sublista via `scatter()`.
3. **Processamento local:** Cada processo calcula de forma independente a soma dos quadrados dos seus próprios números (`somar_quadrados`).
4. **Coleta dos resultados (`gather`):** Cada processo envia uma tupla `(rank, dados_locais, soma_parcial)` de volta para o rank 0 via `gather()`.
5. **Consolidação e conferência (Rank 0):** O rank 0 exibe os subtotais de cada processo, calcula a soma distribuída total, compara com o cálculo sequencial e apresenta o tempo total decorrido.

---

## Principais Conceitos e Funções MPI

| Conceito / Função | Descrição |
| :--- | :--- |
| `MPI.COMM_WORLD` | Comunicador padrão que agrupa todos os processos participantes da execução. |
| `Get_rank()` | Retorna o identificador único (ID) do processo dentro do comunicador (`0` até `size - 1`). |
| `Get_size()` | Retorna o número total de processos no comunicador. |
| `Barrier()` | Sincroniza todos os processos antes da medição de tempo e início da comunicação. |
| `scatter()` | Distribui partes distintas de uma coleção do processo raiz para os demais processos. |
| `gather()` | Reúne os resultados individuais de todos os processos no processo raiz. |
| `MPI.Wtime()` | Relógio de alta resolução usado para medir o tempo de execução (incluindo comunicação). |

---

## Pré-requisitos e Instalação

Para executar o programa, é necessário ter o **Python 3**, um **runtime MPI** instalado no sistema e a biblioteca **`mpi4py`**.

### Instalação padrão

```bash
python -m pip install mpi4py impi-rt
```

### Configuração no Windows (PowerShell + Python 3.12 + Intel MPI)

Caso utilize o Python 3.12 com o pacote `impi-rt` no Windows, configure as variáveis de ambiente na sessão do PowerShell antes de executar:

```powershell
# 1. Instalar as dependências
py -3.12 -m pip install mpi4py impi-rt

# 2. Configurar PATH e raiz do Intel MPI
$env:Path = "$env:LOCALAPPDATA\Programs\Python\Python312\Library\bin;$env:Path"
$env:I_MPI_ROOT = "$env:LOCALAPPDATA\Programs\Python\Python312\Library"
```

### Verificar a instalação

```powershell
# Verificar versão da biblioteca MPI vinculada ao mpi4py
py -3.12 -c "from mpi4py import MPI; print(MPI.Get_library_version())"

# Testar execução paralela com 4 processos
mpiexec -n 4 py -3.12 -c "from mpi4py import MPI; c=MPI.COMM_WORLD; print('Processo', c.Get_rank(), 'de', c.Get_size())"
```

---

## Como Executar

Execute o script utilizando `mpiexec` para iniciar múltiplos processos MPI:

```bash
mpiexec -n 4 python memoria_distribuida.py --n 12
```

Ou, especificando o launcher do Python 3.12 no Windows:

```powershell
mpiexec -n 4 py -3.12 memoria_distribuida.py --n 12
```

### Parâmetros do Comando

| Parâmetro | Significado |
| :--- | :--- |
| `mpiexec` | Programa responsável por iniciar a execução paralela usando MPI. |
| `-n` | Indica quantos processos MPI serão criados. |
| `4` | Quantidade de processos independentes a serem executados. |
| `python` | Interpretador Python responsável por executar o script. |
| `memoria_distribuida.py` | Arquivo Python executado por cada processo. |
| `--n` | Argumento da aplicação que define a quantidade de números gerados (`0` até `n - 1`). Padrão: `12`. Deve ser `>= 0`. |
| `12` | Valor passado para `--n` (calcula a soma dos quadrados de `0` a `11`). |

---

## Observações

- **Espaços de memória isolados:** Mesmo quando todos os processos rodam em um único computador (mesmo host), cada processo possui seu próprio espaço de memória separado. O MPI também permite a execução distribuída em múltiplos nós quando o ambiente de rede/cluster está configurado.
- **Propósito didático:** Este exemplo tem foco educacional e **não** deve ser usado como benchmark de desempenho, pois para valores pequenos de `--n` o custo de comunicação MPI supera o ganho do paralelismo.
