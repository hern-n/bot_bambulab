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

import json
import os

import scanner
import mouse
import time
import agentmail_client



# Tiempo de espera entre acciones para asegurar carga completa de la interfaz
waiting_time = 1.5
initial_waiting_time = 3

# Contador global para rastrear el elemento actual a procesar
current_element_number = 0


def load_json(file_path: str) -> dict:
    """Carga un archivo JSON y lo devuelve como un diccionario de Python."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

data = load_json("config.json")
password = data["password"]

# Inicializar el correo 
agentmail_client.delete_all_inboxes()
email = agentmail_client.create_inbox()

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

    global current_element_number, data, email

    # Inicializar las acciones específicas
    password = data["password"]
    special = data["special"]

    # Incrementar el número de elemento actual para buscar el siguiente elemento en la secuencia
    current_element_number += 1

    # Esperar un tiempo configurable para asegurar que la interfaz se cargue completamente
    time.sleep(waiting_time)

    # Limpiar capturas de pantalla anteriores para evitar confusiones en el análisis
    scanner.clear_screenshots()

    # Capturar la pantalla actual para análisis de elementos
    scanner.scan()

    # Buscar la posición del elemento actual usando coincidencia de plantillas
    match_result = scanner.match_template(
        "screenshots/1.png", f"elements/{current_element_number}.png"
    )

    # Si se encuentra el elemento, realizar clic en su posición
    if match_result is not None:
        mouse.click_at_position(match_result)
        print(f"Clicked on element {current_element_number}")
    else:
        # Registrar cuando no se encuentra un elemento para depuración
        print(f"No match found for elements/{current_element_number}.png")

    # Ejecutar acciones específicas según el tipo de elemento detectado

    if current_element_number in special["write_email"]:
        mouse.type_text(email)
    elif current_element_number in special["write_pasword"]:
        mouse.type_text(password)
    elif current_element_number in special["write_code"]:
        code = agentmail_client.get_code(agentmail_client.get_email(email))
        mouse.type_text(code)
    elif current_element_number in special["human"]:
        mouse.wait_for_human()
    elif current_element_number in special["scroll"]:
        time.sleep(waiting_time)
        mouse.scroll_down()



# Ejecutar el ciclo de automatización 6 veces para procesar los primeros 6 elementos
# Cada iteración procesará un elemento diferente usando el contador global
print("Starting BambuLab Bot automation...")
time.sleep(initial_waiting_time)
for _ in range(len(os.listdir("elements"))):
    main()
print("Automation completed.")
