import glob
import os.path
import string
import time
from pathlib import Path


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FOLDER = ACTIVITY_DIR / "data"
INPUT_FOLDER = ACTIVITY_DIR / "temp" / "input"
OUTPUT_FOLDER = ACTIVITY_DIR / "temp" / "output"
SUBMISSION_FOLDER = ACTIVITY_DIR / "submission"


def prepare_folder(folder: Path) -> None:
    """Crea la carpeta y elimina sus archivos anteriores, conservando .gitkeep."""
    folder.mkdir(parents=True, exist_ok=True)

    for path in folder.iterdir():
        if path.is_file() and path.name != ".gitkeep":
            path.unlink()


# Prepara las carpetas.
prepare_folder(INPUT_FOLDER)
prepare_folder(OUTPUT_FOLDER)
prepare_folder(SUBMISSION_FOLDER)


# Genera 1000 copias de cada archivo de data/ en temp/input/.
n = 1000

for file in sorted(glob.glob(f"{DATA_FOLDER}/*")):
    with open(file, "r", encoding="utf-8") as source_file:
        text = source_file.read()

    raw_filename = os.path.basename(file)
    filename_without_extension = os.path.splitext(raw_filename)[0]

    for i in range(1, n + 1):
        new_filename = f"{filename_without_extension}_{i:05d}.txt"
        input_file = INPUT_FOLDER / new_filename

        with open(input_file, "w", encoding="utf-8") as output_file:
            output_file.write(text)


# Lee los archivos de entrada.
start_time = time.time()

sequence = []

for file in sorted(glob.glob(f"{INPUT_FOLDER}/*")):
    with open(file, "r", encoding="utf-8") as input_file:
        for line in input_file:
            sequence.append((file, line))


# Mapper: convierte cada palabra en un par (palabra, 1).
pairs_sequence = []

for _, line in sequence:
    line = line.lower()
    line = line.translate(str.maketrans("", "", string.punctuation))
    words = line.replace("\n", "").split()
    pairs_sequence.extend((word, 1) for word in words)


# Shuffle and sort.
pairs_sequence.sort()


# Reducer: suma el conteo de cada palabra.
result = []

for key, value in pairs_sequence:
    if result and result[-1][0] == key:
        result[-1] = (key, result[-1][1] + value)
    else:
        result.append((key, value))


# Escribe los resultados en temp/output/ y submission/.
for destination_folder in (OUTPUT_FOLDER, SUBMISSION_FOLDER):
    with open(destination_folder / "part-00000", "w", encoding="utf-8") as output_file:
        for key, value in result:
            output_file.write(f"{key}\t{value}\n")

    with open(destination_folder / "_SUCCESS", "w", encoding="utf-8") as success_file:
        success_file.write("")


end_time = time.time()
print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")