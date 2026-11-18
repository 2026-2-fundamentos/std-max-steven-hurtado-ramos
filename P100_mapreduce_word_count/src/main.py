import shutil
import string
from pathlib import Path

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ACTIVITY_DIR / "data"
INPUT_DIR = ACTIVITY_DIR / "temp" / "input"
OUTPUT_DIR = ACTIVITY_DIR / "temp" / "output"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"


def main():
    # Limpia las carpetas de trabajo para que las ejecuciones repetidas
    # no acumulen archivos.
    for directory in (INPUT_DIR, OUTPUT_DIR):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True, exist_ok=True)

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)

    data_files = sorted(DATA_DIR.glob("*.txt"))

    if not data_files:
        raise FileNotFoundError(f"No hay archivos .txt en {DATA_DIR}")

    # Crea 1.000 copias de cada archivo de datos.
    for data_file in data_files:
        for number in range(1, 1001):
            input_file = INPUT_DIR / (
                f"{data_file.stem}_{number:05d}{data_file.suffix}"
            )
            shutil.copyfile(data_file, input_file)

    # Map: cuenta las palabras de cada archivo.
    # Reduce: suma los conteos de todos los archivos.
    punctuation = str.maketrans("", "", string.punctuation)
    word_counts = {}

    for input_file in sorted(INPUT_DIR.glob("*.txt")):
        file_counts = {}

        with input_file.open("r", encoding="utf-8") as file:
            for line in file:
                words = line.lower().translate(punctuation).split()

                for word in words:
                    file_counts[word] = file_counts.get(word, 0) + 1

        for word, count in file_counts.items():
            word_counts[word] = word_counts.get(word, 0) + count

    # Guarda la salida del proceso.
    part_file = OUTPUT_DIR / "part-00000"
    with part_file.open("w", encoding="utf-8") as file:
        for word in sorted(word_counts):
            file.write(f"{word}\t{word_counts[word]}\n")

    success_file = OUTPUT_DIR / "_SUCCESS"
    success_file.touch()

    # Copia los archivos donde los buscan las pruebas.
    shutil.copyfile(part_file, SUBMISSION_DIR / "part-00000")
    shutil.copyfile(success_file, SUBMISSION_DIR / "_SUCCESS")


if __name__ == "__main__":
    main()