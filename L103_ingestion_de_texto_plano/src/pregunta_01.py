from pathlib import Path
import re

import pandas as pd


DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "clusters_report.txt"
)


def pregunta_01():
    patron_cluster = re.compile(
        r"^\s*(\d+)\s+(\d+)\s+(\d+,\d+)\s*%\s*(.*)$"
    )
    clusters = []

    with DATA_FILE.open(encoding="utf-8") as archivo:
        for linea in archivo:
            coincidencia = patron_cluster.match(linea)

            if coincidencia:
                numero, cantidad, porcentaje, palabras = coincidencia.groups()
                clusters.append(
                    {
                        "cluster": int(numero),
                        "cantidad_de_palabras_clave": int(cantidad),
                        "porcentaje_de_palabras_clave": float(
                            porcentaje.replace(",", ".")
                        ),
                        "_partes": [palabras.strip()] if palabras.strip() else [],
                    }
                )
            elif clusters and linea.strip():
                clusters[-1]["_partes"].append(linea.strip())

    filas = []
    for cluster in clusters:
        palabras = (
            re.sub(r"\s+", " ", " ".join(cluster.pop("_partes")))
            .strip()
            .removesuffix(".")
        )
        cluster["principales_palabras_clave"] = palabras
        filas.append(cluster)

    return pd.DataFrame(
        filas,
        columns=[
            "cluster",
            "cantidad_de_palabras_clave",
            "porcentaje_de_palabras_clave",
            "principales_palabras_clave",
        ],
    )   