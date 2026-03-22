"""
BambuLab Bot - Main Automation Script

Este script implementa un flujo de automatización GUI que combina:
1. Captura de pantalla
2. Detección de elementos mediante plantillas
3. Interacción automática con el mouse
4. Acciones condicionales (pegar y escribir texto)

El proceso se repite un número determinado de veces, buscando elementos
secuenciales en pantalla y realizando acciones específicas según el tipo de elemento.
"""

import ctypes
import json
import logging
import os
import sys
import time

ctypes.windll.shcore.SetProcessDpiAwareness(2)

import scanner
import mouse
import agentmail_client
import keyboard

logger = logging.getLogger(__name__)


# Contador global para rastrear el elemento actual a procesar
current_element_number = 0


def load_json(file_path: str) -> dict:
    """Carga un archivo JSON y lo devuelve como un diccionario de Python."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


data = load_json("config.json")

# Tiempo de espera entre acciones para asegurar carga completa de la interfaz
waiting_time = data["waiting_time"]
initial_waiting_time = data["initial_waiting_time"]


def main():
    """
    Función principal de automatización que ejecuta un ciclo completo de interacción.

    Proceso:
    1. Incrementa el contador de elementos
    2. Espera a que la interfaz esté lista
    3. Limpia y captura la pantalla
    4. Busca el elemento correspondiente mediante plantilla
    5. Realiza clic si encuentra el elemento
    6. Ejecuta acciones específicas según el tipo de elemento

    Returns:
        None
    """

    # Comrobar que no se le ha dado a salir del porgrama

    if keyboard.is_pressed("f2"):
        sys.exit()

    global current_element_number, data, email

    # Inicializar las acciones específicas
    special = data["special"]
    more_time = data["more_time"]
    coordenates = data["coordenates"]

    # Incrementar el número de elemento actual
    current_element_number += 1

    # Esperar un tiempo configurable para asegurar carga completa
    if current_element_number in more_time:
        time.sleep(waiting_time * 3.1)
    else:
        time.sleep(waiting_time)

    # Limpiar capturas de pantalla anteriores para evitar confusiones en el análisis
    scanner.clear_screenshots()

    # Comporbar si hay que quitar lo de las descargas de google
    if current_element_number in special["away_downloads"]:
        mouse.click_at_position([400, 20])
        time.sleep(0.4)

    # Si está en la lista de posiciones manuales, cliquea en coordenadas
    if str(current_element_number) in coordenates:
        logger.info(f"Manual coordinate click: {current_element_number}")
        mouse.click_at_position(coordenates[str(current_element_number)])

    else:

        # Capturar la pantalla actual para análisis de elementos
        scanner.scan()

        for i in range(3):
            # Buscar la posición del elemento actual usando coincidencia de plantillas
            match_result = scanner.match_template(
                "screenshots/1.png", f"elements/{current_element_number}.png"
            )

            # Si se encuentra el elemento, realizar clic en su posición
            if match_result is not None:
                mouse.click_at_position(match_result)
                logger.debug(f"Clicked on element {current_element_number}")
                break
            else:
                logger.warning(
                    f"No match found for elements/{current_element_number}.png"
                )
                time.sleep(waiting_time)
                if i == 2:
                    logger.error("Element not detected, exiting the program")
                    sys.exit()

    # Ejecutar acciones específicas según el tipo de elemento detectado

    if current_element_number in special["write_email"]:
        mouse.type_text(email)

    elif str(current_element_number) in special["write_things"]:
        mouse.type_text(special["write_things"][str(current_element_number)])

    elif current_element_number in special["write_code"]:
        code = agentmail_client.get_code(agentmail_client.get_email(email))
        mouse.type_text(code)

    elif current_element_number in special["human"]:
        mouse.wait_for_human(f"elements/{current_element_number}.png")

    elif current_element_number in special["scroll"]:
        time.sleep(4)
        mouse.scroll_down()


running = True
while running:

    # Inicializar el correo
    agentmail_client.delete_all_inboxes()
    email = agentmail_client.create_inbox()

    current_element_number = 0

    # Ejecutar el ciclo de automatización 6 veces para procesar los primeros 6 elementos
    # Cada iteración procesará un elemento diferente usando el contador global
    logger.info("")
    logger.info("")
    logger.info("Starting BambuLab Bot automation...")
    time.sleep(initial_waiting_time)
    for _ in range(len(os.listdir("elements"))):
        main()
    logger.info("Automation completed.")
    logger.info("")
    logger.info("")
