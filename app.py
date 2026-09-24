from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# ============================================
# BASE DE DATOS SIMULADA
# ============================================

def cargar_datos():
    """Carga los datos de productos y compras"""
    try:
        with open('datos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Datos iniciales si no existe el archivo
        datos_iniciales = {
            "productos": [
                {"id": 1, "nombre": "leche", "precio": 2.50, "stock": 20},
                {"id": 2, "nombre": "pan", "precio": 1.20, "stock": 50},
                {"id": 3, "nombre": "huevos", "precio": 3.00, "stock": 30},
                {"id": 4, "nombre": "arroz", "precio": 4.50, "stock": 40},
                {"id": 5, "nombre": "azúcar", "precio": 2.80, "stock": 25},
                {"id": 6, "nombre": "café", "precio": 5.00, "stock": 15},
                {"id": 7, "nombre": "galletas", "precio": 1.50, "stock": 35},
                {"id": 8, "nombre": "jabón", "precio": 2.00, "stock": 45}
            ],
            "compras": []
        }
        guardar_datos(datos_iniciales)
        return datos_iniciales

def guardar_datos(datos):
    """Guarda los datos en el archivo"""
    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def buscar_producto(nombre):
    """Busca un producto por nombre"""
    datos = cargar_datos()
    nombre = nombre.lower().strip()
    for producto in datos["productos"]:
        if nombre in producto["nombre"].lower():
            return producto
    return None

def formatear_precio(precio):
    """Formatea el precio con símbolo de euro"""
    return f"€{precio:.2f}"

def registrar_compra(producto, cantidad):
    """Registra una compra en el sistema"""
    datos = cargar_datos()
    compra = {
        "producto": producto["nombre"],
        "cantidad": cantidad,
        "precio_unitario": producto["precio"],
        "total": producto["precio"] * cantidad,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    datos["compras"].append(compra)
    
    # Actualizar stock
    for p in datos["productos"]:
        if p["id"] == producto["id"]:
            p["stock"] -= cantidad
            break
    
    guardar_datos(datos)
    return compra

# ============================================
# RUTAS PRINCIPALES
# ============================================

@app.route('/')
def home():
    """Página principal"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bot de Compras</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #128C7E; }
            .info { background: #f0f0f0; padding: 20px; border-radius: 10px; }
        </style>
    </head>
    <body>
        <h1>🤖 Bot de Compras</h1>
        <div class="info">
            <p><strong>Estado:</strong> ✅ Funcionando</p>
            <p><strong>Productos disponibles:</strong> 8</p>
            <p><strong>Compras registradas:</strong> 0</p>
        </div>
    </body>
    </html>
    '''

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Webhook para WhatsApp (mantenido pero sin notificaciones)"""
    if request.method == 'GET':
        # Verificación del webhook
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if verify_token == 'botcompras123':
            return challenge
        return 'Token de verificación incorrecto', 403
    
    # Recibir mensajes de WhatsApp
    if request.method == 'POST':
        data = request.get_json()
        print(f"Mensaje recibido: {data}")
        
        # Procesar mensajes (sin enviar notificaciones)
        if data and 'entry' in data:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    messages = value.get('messages', [])
                    
                    for message in messages:
                        if message.get('type') == 'text':
                            texto = message.get('text', {}).get('body', '').lower()
                            from_number = message.get('from', '')
                            
                            # Procesar comandos
                            respuesta = procesar_comando(texto)
                            
                            # Aquí NO se envía respuesta por WhatsApp
                            # Solo se registra en logs
                            print(f"Comando: {texto}")
                            print(f"Respuesta: {respuesta}")
                            print(f"De: {from_number}")
        
        return jsonify({"status": "received"}), 200

def procesar_comando(texto):
    """Procesa los comandos del bot"""
    # Comandos básicos
    if texto == "hola":
        return "¡Hola! 👋 Soy tu bot de compras. Escribe 'ayuda' para ver los comandos."
    
    if texto == "ayuda":
        return "📋 Comandos disponibles:\n" \
               "• 'precio [producto]' - Ver precio\n" \
               "• 'stock [producto]' - Ver stock\n" \
               "• 'comprar [producto]' - Hacer compra\n" \
               "• 'precios' - Ver todos los precios\n" \
               "• 'hola' - Saludo"
    
    if texto == "precios":
        datos = cargar_datos()
        respuesta = "📦 Precios de productos:\n"
        for p in datos["productos"]:
            respuesta += f"• {p['nombre'].capitalize()}: {formatear_precio(p['precio'])} (Stock: {p['stock']})\n"
        return respuesta
    
    # Comando precio
    if texto.startswith("precio "):
        nombre = texto.replace("precio ", "")
        producto = buscar_producto(nombre)
        if producto:
            return f"💰 {producto['nombre'].capitalize()}: {formatear_precio(producto['precio'])}"
        return f"❌ Producto '{nombre}' no encontrado"
    
    # Comando stock
    if texto.startswith("stock "):
        nombre = texto.replace("stock ", "")
        producto = buscar_producto(nombre)
        if producto:
            return f"📦 {producto['nombre'].capitalize()}: {producto['stock']} unidades disponibles"
        return f"❌ Producto '{nombre}' no encontrado"
    
    # Comando comprar
    if texto.startswith("comprar "):
        nombre = texto.replace("comprar ", "")
        producto = buscar_producto(nombre)
        if producto:
            if producto["stock"] > 0:
                compra = registrar_compra(producto, 1)
                return f"✅ Compra registrada:\n" \
                       f"• Producto: {producto['nombre'].capitalize()}\n" \
                       f"• Precio: {formatear_precio(producto['precio'])}\n" \
                       f"• Total: {formatear_precio(compra['total'])}"
            return f"❌ No hay stock de {producto['nombre']}"
        return f"❌ Producto '{nombre}' no encontrado"
    
    return "❌ Comando no reconocido. Escribe 'ayuda' para ver los comandos."

# ============================================
# INICIO DEL SERVIDOR
# ============================================

if __name__ == '__main__':
    print("🤖 Bot de Compras iniciado")
    print("📦 Cargando datos...")
    cargar_datos()
    print("✅ Datos cargados correctamente")
    print("🌐 Servidor iniciado en puerto 5000")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
