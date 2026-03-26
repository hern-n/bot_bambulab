import logging
import os
import re

logger = logging.getLogger(__name__)


def rename_pngs(folder_path: str) -> None:
    png_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".png")]

    pattern = re.compile(r"(\d+)")
    files_with_num = []
    for file in png_files:
        match = pattern.search(file)
        if match:
            number = int(match.group(1))
            files_with_num.append((number, file))

    files_with_num.sort()

    temp_names = []
    for i, (_, file) in enumerate(files_with_num):
        original_path = os.path.join(folder_path, file)
        temp_name = os.path.join(folder_path, f"temp_{i}.png")
        os.rename(original_path, temp_name)
        temp_names.append(temp_name)
        logger.debug(f"Renamed '{file}' to temp_{i}.png")

    for i, temp_path in enumerate(temp_names, start=1):
        new_path = os.path.join(folder_path, f"{i}.png")
        os.rename(temp_path, new_path)
        logger.debug(f"Renamed temp file to {i}.png")

    logger.info("Renaming completed.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    rename_pngs("elements")
