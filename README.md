# BambuLab Bot

Python GUI automation bot using computer vision (OpenCV) and mouse automation (pyautogui) for screen interaction with graphical interfaces.

## Features

- Screenshot capture and template matching with OpenCV
- Mouse automation (click, type, scroll, paste)
- Configurable automation workflow via JSON

## Installation

### Prerequisites

- Python 3.12+

### Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Rename .env.example to .env and add your AgentMail API key
cp .env.example .env
```

## Usage

```bash
# Run main automation
python src/main.py

# Run scanner module directly
python src/scanner.py
```

## Configuration

Edit `config.json` to customize:

- `waiting_time`: Delay between actions
- `initial_waiting_time`: Initial delay before starting
- `special`: Element-specific actions (write email, write text, write code, human interaction, scroll)
- `coordenates`: Manual click coordinates for specific elements

## Testing

```bash
pytest                        # Run all tests
pytest test/test.py           # Run single test file
pytest -v                     # Verbose output
```

## Code Quality

```bash
black src/                    # Format code
flake8 src/ --max-line-length=88
pyflakes src/
```

## Project Structure

```
bot_bambulab/
├── src/
│   ├── main.py              # Main automation entry point
│   ├── scanner.py           # Screenshot, template matching
│   ├── mouse.py             # Mouse automation
│   └── agentmail_client.py  # AgentMail API client
├── elements/                 # Template images for matching
├── screenshots/              # Captured screenshots
├── test/                     # Exploratory tests
├── config.json               # Configuration file
└── AGENTS.md                 # Developer guide
```

## Sobre el Proyecto

**BambuLab Bot** es un bot de automatización GUI desarrollado en Python que utiliza visión por computadora (OpenCV) y automatización de mouse (pyautogui) para interactuar con interfaces gráficas de usuario.

### Estructura y Funciones de Archivos

| Archivo | Descripción |
|---------|-------------|
| `src/main.py` | Punto de entrada principal. Ejecuta el flujo de automatización definido en `config.json`. Coordina todas las operaciones del bot. |
| `src/scanner.py` | Módulo de captura de pantalla y visión por computadora. Incluye funciones para capturar screenshots, buscar plantillas (template matching) y verificar existencia de elementos en pantalla. |
| `src/mouse.py` | Automatización del mouse y teclado. Proporciona funciones para hacer clic, mover el mouse, escribir texto, pegar desde el portapapeles y desplazar. |
| `src/agentmail_client.py` | Cliente para la API de AgentMail. Permite crear bandejas de correo temporales, obtener códigos de verificación y gestionar correos electrónicos. |
| `elements/` | Directorio que contiene imágenes de plantilla (screenshots de elementos UI) usadas para el reconocimiento visual mediante OpenCV. |
| `screenshots/` | Directorio donde se guardan las capturas de pantalla tomadas durante la ejecución del bot. |
| `test/` | Pruebas exploratorias para validar diferentes tecnologías y funcionalidades. |
| `config.json` | Archivo de configuración del flujo de automatización (tiempos de espera, coordenadas, acciones especiales). |
| `AGENTS.md` | Guía de desarrollo con convenciones, comandos y documentación técnica. |

## License

MIT
