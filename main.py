from dotenv import load_dotenv
import yfinance as yf
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

app = FastAPI(title="Agente de Riesgo Financiero")

class MessageRequest(BaseModel):
    message: str
    session_id: str
    user_id: str

class MessageResponse(BaseModel):
    reply: str
    session_id: str

def analizar_opciones_ticker(ticker: str) -> dict:
    """Obtiene el precio del activo subyacente y los datos de la cadena de opciones

    (calls/puts, volatilidad implicita y volumen) para el vencimiento mas
    cercano.

    Args:
        ticker: Simbolo bursatil de la accion (ej. 'AAPL', 'NVDA', 'TSLA').

    Returns:
        Diccionario con el precio actual, fecha de expiracion y contratos
        cercanos al dinero (ATM).
    """
    try:
        activo = yf.Ticker(ticker)
        precio_actual = activo.info.get("currentPrice") or activo.info.get("regularMarketPrice")

        fechas_vencimiento = activo.options
        if not fechas_vencimiento:
            return {"error": "No hay opciones disponibles para este ticker"}
        
        proximo_vencimiento = fechas_vencimiento[0]
        cadena = activo.option_chain(proximo_vencimiento)

        def filtrar_atm(df):
            df_ordenado = df.iloc[(df['strike'] - precio_actual).abs().argsort()[:3]]
            return df_ordenado[['strike', 'lastPrice', 'impliedVolatility', 'volume', 'openInterest']].to_dict(orient='records')

        return {
            "ticker": ticker.upper(),
            "precio_subyacente": precio_actual,
            "proxima_expiracion": proximo_vencimiento,
            "calls_destacados": filtrar_atm(cadena.calls),
            "puts_destacados": filtrar_atm(cadena.puts)
        }
    except Exception as e:
        return {"error": f"No se pudo analizar el ticker: {e}"}

instruction = """
Eres un analista de derivados financieros especializado en opciones (calls y puts).
Cuando el usuario pregunte si es un buen día o buen momento para comprar una opción:

1. Llama a la herramienta `analizar_opciones_ticker` para obtener la cotización y la cadena de opciones.
2. Analiza los siguientes puntos críticos antes de responder:
   - **Volatilidad Implícita (IV):** Si la IV es excesivamente alta, comprar opciones suele ser caro (riesgo de 'IV crush'). Si es baja, la prima es más barata.
   - **Liquidez:** Revisa el 'volume' y el 'openInterest'. Si son muy bajos, advierte que habrá mucho spread entre compra y venta (slippage).
   - **Decaimiento Temporal (Theta):** Advierte sobre los días restantes hasta la fecha de expiración.
3. Concluye con un veredicto técnico basado en los datos (ej: "Momento favorable", "Riesgo alto por primas infladas", "Falta de liquidez") aclarando que se trata de un análisis técnico y no de asesoría financiera legal.
"""

agent = Agent(
    name = "analista_riesgo",
    model = "gemini-3.6-flash",
    instruction = instruction,
    tools = [analizar_opciones_ticker]
)

session_service = InMemorySessionService()

runner = Runner(
    agent= agent,
    session_service= session_service,
    app_name="app_analista_riesgo",
    auto_create_session=True
)

@app.post("/send-message", response_model= MessageResponse)
async def send_message(request: MessageRequest):
    try:
        session_id = request.session_id or "default_session"
        user_id = request.user_id or "default_user"

        content = types.Content(
            role = "user",
            parts = [types.Part.from_text(text=request.message)]
        )

        reply_parts = []

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.content and event.content.parts:
                text = "".join(part.text for part in event.content.parts if getattr(part, "text", None))
                if text:
                    reply_parts.append(text)
        
        reply_text = "".join(reply_parts)

        return MessageResponse(
            reply = reply_text,
            session_id = session_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el mensaje {str(e)}"
        )