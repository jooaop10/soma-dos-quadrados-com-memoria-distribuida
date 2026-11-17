import argparse

try:
    from mpi4py import MPI
except ImportError as erro:
    raise SystemExit(
        "mpi4py não encontrada. Instale MPI e depois execute: "
        "python -m pip install mpi4py"
    ) from erro


def dividir_dados(valores, quantidade_processos):
    return [valores[rank::quantidade_processos]
            for rank in range(quantidade_processos)]


def somar_quadrados(valores_locais):
    return sum(numero ** 2 for numero in valores_locais)


def main():
    parser = argparse.ArgumentParser(
        description="Soma de quadrados com memória distribuída usando MPI."
    )
    parser.add_argument("--n", type=int, default=12,
                        help="Quantos números gerar: 0 até n-1 (padrão: 12).")
    args = parser.parse_args()
    if args.n < 0:
        parser.error("--n deve ser maior ou igual a zero")

    comunicador = MPI.COMM_WORLD
    rank = comunicador.Get_rank()
    total_processos = comunicador.Get_size()

    if rank == 0:
        dados = list(range(args.n))
        partes = dividir_dados(dados, total_processos)
        print(f"\n[RAIZ] {args.n} números; {total_processos} processos MPI.",
              flush=True)
    else:
        partes = None

    comunicador.Barrier()
    inicio = MPI.Wtime()

    meus_dados = comunicador.scatter(partes, root=0)
    meu_resultado = somar_quadrados(meus_dados)
    resultados = comunicador.gather(
        (rank, meus_dados, meu_resultado), root=0
    )

    if rank == 0:
        tempo_total = MPI.Wtime() - inicio
        print("\n[RESULTADOS POR PROCESSO]")
        for rank_recebido, lista_recebida, parcial in sorted(resultados):
            print(f"  rank {rank_recebido}: dados={lista_recebida}; "
                  f"soma parcial={parcial}")

        soma_distribuida = sum(parcial for _, _, parcial in resultados)
        soma_sequencial = somar_quadrados(range(args.n))

        print(f"\n[RESULTADO DISTRIBUÍDO] {soma_distribuida}")
        print(f"[CONFERÊNCIA SEQUENCIAL] {soma_sequencial}")
        print(f"[CORRETO?] {soma_distribuida == soma_sequencial}")
        print(f"[TEMPO TOTAL (s)] {tempo_total:.6f}")
        print("[OBS.] Tempo inclui a comunicação MPI e pode variar; "
              "não use este exemplo pequeno como benchmark.\n")


if __name__ == "__main__":
    main()
