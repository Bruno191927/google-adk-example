# Agente de Riesgo Financiero 📈🤖

API basada en **FastAPI** y **Google Agent Development Kit (ADK)** impulsada por modelos **Google Gemini**. El agente actúa como analista financiero especializado en derivados (opciones calls y puts), consultando datos de mercado en tiempo real mediante **Yahoo Finance (`yfinance`)** para evaluar el riesgo técnico antes de operar.

---

## 🚀 Características

- **Consulta en tiempo real:** Obtiene precio del subyacente y cadena de opciones (Calls/Puts) para el vencimiento más cercano.
- **Filtro ATM (At The Money):** Selecciona los contratos con strike más cercanos al precio actual.
- **Evaluación de Factores Clave:**
  - **Volatilidad Implícita (IV):** Alerta sobre primas sobrevaloradas y riesgo de *IV Crush*.
  - **Liquidez:** Analiza volumen y *Open Interest* para advertir sobre posibles spreads y *slippage*.
  - **Decaimiento Temporal ($\Theta$ - Theta):** Monitorea la proximidad a la fecha de expiración.
- **Memoria de Sesión:** Mantiene contexto conversacional por usuario y sesión con `InMemorySessionService`.
- **API REST lista para producción:** Construida sobre FastAPI con soporte para llamadas asíncronas y documentación automática.

---

## 🛠️ Tecnologías

- **Python 3.10+**
- [FastAPI](https://fastapi.tiangolo.com/) y [Uvicorn](https://www.uvicorn.org/)
- [Google ADK](https://github.com/google/agent-development-kit) (`google-adk`, `google-genai`)
- [yfinance](https://github.com/ranaroussi/yfinance)
- [Pydantic](https://docs.pydantic.dev/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

---

## 📋 Requisitos Previos

1. Tener instalado **Python 3.10** o superior.
2. Contar con una API Key de **Google Gemini** ([Google AI Studio](https://aistudio.google.com/)).

---

## ⚙️ Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd AgenteRiesgo
   ```

2. **Crear y activar un entorno virtual:**
   - En Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - En Linux / macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Copia el archivo `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```
   Edita `.env` y añade tu API Key:
   ```env
   GOOGLE_API_KEY=tu-api-key-de-gemini
   ```

---

## 🏃‍♂️ Ejecución

Inicia el servidor de desarrollo con Uvicorn:

```bash
uvicorn main:app --reload
```

El servicio estará disponible en `http://127.0.0.1:8000`.

- **Documentación interactiva (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentación alternativa (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 Uso de la API

### Enviar mensaje al agente

- **Ruta:** `POST /send-message`
- **Headers:** `Content-Type: application/json`

#### Ejemplo de Petición (`Request`):

```json
{
  "message": "¿Es buen momento para comprar un Call de NVDA?",
  "session_id": "sesion_123",
  "user_id": "usuario_456"
}
```

#### Ejemplo de Respuesta (`Response`):

```json
{
  "reply": "Actualmente NVDA cotiza en $X. Para el próximo vencimiento del YYYY-MM-DD, los contratos Call ATM muestran una volatilidad implícita del Z%...",
  "session_id": "sesion_123"
}
```

---

## 📁 Estructura del Proyecto

```text
AgenteRiesgo/
├── .env.example       # Plantilla de variables de entorno
├── .gitignore          # Exclusión de archivos para Git (.env, .venv, caché)
├── requirements.txt   # Dependencias del proyecto
├── main.py            # Servidor FastAPI, definición del agente y herramientas
└── README.md          # Documentación del proyecto
```

---

## ⚠️ Descargo de Responsabilidad (Disclaimer)

Este software y el agente de IA proporcionan análisis técnico y educativo con base en datos públicos de mercado. **No constituyen asesoramiento financiero, legal ni recomendaciones de inversión**. Toda operación con derivados financieros conlleva un alto riesgo de pérdida de capital.

