from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

# Configuración de WhatsApp (desde variables de entorno)
WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN', '')
PHONE_ID = os.environ.get('PHONE_ID', '')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN', 'botcompras123')

# ========== RUTA PRINCIPAL (HOME) ==========
@app.route('/')
def home():
    return "🤖 Bot de Compras con WhatsApp funcionando!"

# ========== WEBHOOK DE WHATSAPP ==========
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # Verificación inicial (GET)
    if request.method == 'GET':
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if verify_token == VERIFY_TOKEN:
            return challenge, 200
        return "Token incorrecto", 403
    
    # Recibir mensajes (POST)
    if request.method == 'POST':
        data = request.get_json()
        print("Mensaje recibido:", json.dumps(data, indent=2))
        
        # Procesar mensaje
        try:
            if 'messages' in data['entry'][0]['changes'][0]['value']:
                message = data['entry'][0]['changes'][0]['value']['messages'][0]
                sender = message['from']
                text = message['text']['body']
                
                # Responder
                respuesta = procesar_mensaje(text)
                enviar_whatsapp(sender, respuesta)
        except Exception as e:
            print("Error:", e)
        
        return "OK", 200

# ========== FUNCIONES DEL BOT ==========
def procesar_mensaje(texto):
    texto = texto.lower().strip()
    
    # Comandos del bot
    if "hola" in texto or "buenas" in texto:
        return "¡Hola! 👋 Soy tu bot de compras.\n\nComandos:\n- 'precio [producto]' para ver precios\n- 'stock [producto]' para ver stock\n- 'comprar [producto]' para comprar\n- 'ayuda' para ver ayuda"
    
    elif "precio" in texto:
        producto = texto.replace("precio", "").strip()
        if producto:
            return buscar_precio(producto)
        else:
            return "¿Qué producto quieres consultar?\nEjemplo: 'precio leche'"
    
    elif "stock" in texto:
        producto = texto.replace("stock", "").strip()
        if producto:
            return buscar_stock(producto)
        else:
            return "¿Qué producto quieres consultar?\nEjemplo: 'stock pan'"
    
    elif "comprar" in texto:
        producto = texto.replace("comprar", "").strip()
        if producto:
            return comprar_producto(producto)
        else:
            return "¿Qué producto quieres comprar?\nEjemplo: 'comprar arroz'"
    
    elif "ayuda" in texto:
        return "🤖 COMANDOS DISPONIBLES:\n\n• 'hola' - Saludo\n• 'precio [producto]' - Ver precio\n• 'stock [producto]' - Ver stock\n• 'comprar [producto]' - Hacer compra\n• 'ayuda' - Ver esta ayuda"
    
    elif "precios" in texto:
        return mostrar_todos_los_precios()
    
    else:
        return "No entendí tu mensaje 🤔\nEscribe 'ayuda' para ver los comandos disponibles."

# ========== FUNCIONES DE NEGOCIO ==========
def buscar_precio(producto):
    # Aquí puedes conectar con tu base de datos
    precios = {
        "leche": "$45.00",
        "pan": "$20.00",
        "arroz": "$35.00",
        "huevo": "$30.00",
        "azucar": "$40.00"
    }
    
    if producto in precios:
        return f"💰 Precio de {producto}: {precios[producto]}"
    else:
        return f"Producto '{producto}' no encontrado. Productos disponibles: {', '.join(precios.keys())}"

def buscar_stock(producto):
    # Simulación de stock
    stock = {
        "leche": "Disponible (50 unidades)",
        "pan": "Disponible (100 unidades)",
        "arroz": "Pocas unidades (10)",
        "huevo": "Agotado",
        "azucar": "Disponible (30 unidades)"
    }
    
    if producto in stock:
        return f"📦 Stock de {producto}: {stock[producto]}"
    else:
        return f"Producto '{producto}' no encontrado."

def comprar_producto(producto):
    # Simulación de compra
    return f"✅ ¡Compra realizada!\n\nProducto: {producto}\nEstado: Procesando\n\nTe notificaremos cuando esté listo."

def mostrar_todos_los_precios():
    precios = {
        "leche": "$45.00",
        "pan": "$20.00",
        "arroz": "$35.00",
        "huevo": "$30.00",
        "azucar": "$40.00"
    }
    
    mensaje = "💰 PRECIOS ACTUALES:\n\n"
    for producto, precio in precios.items():
        mensaje += f"• {producto}: {precio}\n"
    return mensaje

# ========== ENVIAR MENSAJE DE WHATSAPP ==========
def enviar_whatsapp(numero, mensaje):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensaje}
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# ========== CARGA DE DATOS ==========
def cargar_datos():
    # Tu lógica de carga de datos
    print("Datos cargados correctamente")

def guardar_datos():
    # Tu lógica de guardado de datos
    print("Datos guardados correctamente")

cargar_datos()

if __name__ == "__main__":
    print("BOT DE COMPRAS CON WHATSAPP 24/7")
    print("Usuario: admin")
    print("Contrasena: admin123")
    import atexit
    atexit.register(guardar_datos)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
