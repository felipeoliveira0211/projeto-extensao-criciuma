"""Execute python main.py. Para refazer o banco, use --reconstruir com a pasta original."""
import argparse
from pathlib import Path
from analise import analisar

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Distribuição dos recursos de Criciúma, 2024–2025")
    parser.add_argument("--reconstruir", type=Path, metavar="PASTA_ORIGINAL",
                        help="recria o banco compacto a partir dos CSVs originais e seus anexos")
    args = parser.parse_args()
    projeto = Path(__file__).resolve().parent
    if args.reconstruir:
        from preparar_dados import preparar
        preparar(args.reconstruir, projeto / "dados")
    analisar(projeto)
