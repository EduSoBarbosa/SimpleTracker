import pandas as pd

from database.engine import init_db, get_session
from database.models import TacoAlimento
from database import repository as repo

CSV_PATH = "data/taco_limpo.csv"


def ja_importado():
    """Evita duplicar dados se o script for rodado mais de uma vez."""
    session = get_session()
    try:
        return session.query(TacoAlimento).count() > 0
    finally:
        session.close()


def main():
    init_db()

    if ja_importado():
        print("Tabela taco_alimentos já tem dados. Nada foi importado (evitando duplicar).")
        print("Se quiser reimportar do zero, apague o arquivo database/app.db e rode de novo.")
        return

    df = pd.read_csv(CSV_PATH)

    # NaN do pandas precisa virar None para o SQLAlchemy gravar como NULL
    df = df.where(pd.notnull(df), None)

    registros = df.to_dict(orient="records")
    total = repo.importar_alimentos_taco(registros)

    print(f"Importados {total} alimentos da tabela TACO para o banco.")


if __name__ == "__main__":
    main()