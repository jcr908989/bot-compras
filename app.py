import os
import json
import time
import threading
import random
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from scraper import verificar_producto, compra_automatica

app = Flask(__name__)
app.secret_key = "clave_secreta"

USERS = {"admin": "admin123"}

config = {
    "intervalo": 30,
    "tienda": "todas",
    "usar_proxies": False,
    "proxies_lista": [],
    "modo_turbo": False,
    "intervalo_turbo": 5,
    "captcha_solver": False,
    "api_key_2captcha": "",
    "api_key_anticaptcha": "",
    "discord_webhook": "",
    "monitoreo_activo": False,
    "datos_tarjeta": {"numero": "", "expiracion": "", "cvv": "", "titular": ""},
    "datos_envio": {"nombre": "", "apellidos": "", "direccion": "", "ciudad": "", "cp": "", "provincia": "", "pais": "Espana", "email": "", "telefono": ""}
}

productos = []
preventas = []
logs = []

estadisticas = {
    "verificaciones": 0,
    "exitosas": 0,
    "fallidas": 0,
    "checkouts_completados": 0,
    "reintentos": 0,
    "tiempos_respuesta": [],
    "ultima_verificacion": None,
    "ultima_compra": None,
    "inicio": datetime.now()
}

hilo_monitoreo = None
detener_monitoreo = threading.Event()

def anadir_log(nivel, mensaje):
    timestamp = datetime.now().strftime("%H:%M:%S")
    logs.append({"time": timestamp, "level": nivel, "message": mensaje})
    if len(logs) > 100:
        logs.pop(0)
    print(f"[{timestamp}] [{nivel}] {mensaje}")

def detectar_tienda_producto(url):
    url_lower = url.lower()
    tiendas = {
        "cardmarket": "CardMarket",
        "toysrus": "Toys R Us",
        "unsobremas": "Un Solo Mas",
        "flashstore": "Flash Store",
        "turolgames": "Turol Games",
        "game.es": "Game",
        "mediamarkt": "MediaMarkt",
        "amazon": "Amazon",
        "ebay": "eBay"
    }
    for dominio, nombre in tiendas.items():
        if dominio in url_lower:
            return nombre
    return "Desconocida"

def obtener_proxy_aleatorio():
    if config["usar_proxies"] and config["proxies_lista"]:
        return random.choice(config["proxies_lista"])
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username in USERS and USERS[username] == password:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Credenciales invalidas")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("index.html", productos=productos, preventas=preventas, config=config, logs=logs[-20:], estadisticas=estadisticas)

@app.route("/productos")
@login_required
def pagina_productos():
    return render_template("productos.html", productos=productos)

@app.route("/preventas")
@login_required
def pagina_preventas():
    return render_template("preventas.html", preventas=preventas)

@app.route("/configuracion")
@login_required
def pagina_configuracion():
    return render_template("configuracion.html", config=config)
@app.route("/api/productos/agregar", methods=["POST"])
@login_required
def agregar_producto():
    data = request.get_json()
    nombre = data.get("nombre", "").strip()
    url = data.get("url", "").strip()
    if not nombre or not url:
        return jsonify({"success": False, "error": "Nombre y URL son obligatorios"})
    tienda = detectar_tienda_producto(url)
    nuevo_producto = {
        "id": len(productos),
        "nombre": nombre,
        "url": url,
        "tienda": tienda,
        "disponible": False,
        "precio": None,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ultima_verificacion": None,
        "veces_disponible": 0
    }
    productos.append(nuevo_producto)
    anadir_log("INFO", f"Producto anadido: {nombre}")
    return jsonify({"success": True, "producto": nuevo_producto})

@app.route("/api/productos/eliminar/<int:index>", methods=["DELETE"])
@login_required
def eliminar_producto(index):
    if 0 <= index < len(productos):
        producto = productos.pop(index)
        anadir_log("WARN", f"Producto eliminado: {producto['nombre']}")
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Indice invalido"})

@app.route("/api/productos/<int:index>/verificar", methods=["POST"])
@login_required
def verificar_producto_manual(index):
    if 0 <= index < len(productos):
        producto = productos[index]
        proxy = obtener_proxy_aleatorio()
        inicio = time.time()
        resultado = verificar_producto(producto["url"], proxy)
        latencia = int((time.time() - inicio) * 1000)
        estadisticas["verificaciones"] += 1
        estadisticas["tiempos_respuesta"].append(latencia)
        estadisticas["ultima_verificacion"] = datetime.now().strftime("%H:%M:%S")
        if resultado.get("disponible"):
            estadisticas["exitosas"] += 1
            producto["disponible"] = True
            producto["precio"] = resultado.get("precio")
            producto["veces_disponible"] += 1
            anadir_log("SUCCESS", f"Producto disponible: {producto['nombre']}")
        else:
            estadisticas["fallidas"] += 1
            producto["disponible"] = False
            anadir_log("INFO", f"Producto agotado: {producto['nombre']}")
        producto["ultima_verificacion"] = datetime.now().strftime("%H:%M:%S")
        return jsonify({"success": True, "disponible": producto["disponible"], "precio": producto["precio"], "latencia": latencia})
    return jsonify({"success": False, "error": "Producto no encontrado"})

@app.route("/api/preventas", methods=["POST"])
@login_required
def anadir_preventa():
    nombre = request.form.get("nombre", "").strip()
    url = request.form.get("url", "").strip()
    if not nombre or not url:
        return jsonify({"status": "error", "message": "Nombre y URL son obligatorios"})
    nueva_preventa = {
        "id": len(preventas),
        "nombre": nombre,
        "url": url,
        "tienda": detectar_tienda_producto(url),
        "estado": "pendiente",
        "fecha_anadido": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    preventas.append(nueva_preventa)
    anadir_log("INFO", f"Preventa anadida: {nombre}")
    return jsonify({"status": "ok", "message": "Preventa anadida"})

@app.route("/api/preventas/<int:index>", methods=["DELETE"])
@login_required
def eliminar_preventa(index):
    if 0 <= index < len(preventas):
        preventa = preventas.pop(index)
        anadir_log("WARN", f"Preventa eliminada: {preventa['nombre']}")
        return jsonify({"status": "ok", "message": "Preventa eliminada"})
    return jsonify({"status": "error", "message": "Preventa no encontrada"})
@app.route("/api/configuracion", methods=["POST"])
@login_required
def guardar_configuracion():
    global config
    data = request.get_json()
    if "intervalo" in data:
        config["intervalo"] = int(data.get("intervalo", 30))
    if "tienda" in data:
        config["tienda"] = data.get("tienda", "todas")
    if "usar_proxies" in data:
        config["usar_proxies"] = data.get("usar_proxies", False)
    if "modo_turbo" in data:
        config["modo_turbo"] = data.get("modo_turbo", False)
    if "discord_webhook" in data:
        config["discord_webhook"] = data.get("discord_webhook", "")
    if "datos_tarjeta" in data:
        config["datos_tarjeta"] = data["datos_tarjeta"]
    if "datos_envio" in data:
        config["datos_envio"] = data["datos_envio"]
    anadir_log("INFO", "Configuracion guardada")
    return jsonify({"status": "ok", "message": "Configuracion guardada"})

@app.route("/api/configuracion/cargar", methods=["GET"])
@login_required
def cargar_configuracion():
    return jsonify(config)

@app.route("/api/proxies", methods=["GET"])
@login_required
def obtener_proxies():
    return jsonify({"proxies": config["proxies_lista"], "usar_proxies": config["usar_proxies"], "total": len(config["proxies_lista"])})

@app.route("/api/proxies/agregar", methods=["POST"])
@login_required
def agregar_proxy():
    data = request.get_json()
    proxy = data.get("proxy", "").strip()
    if not proxy:
        return jsonify({"status": "error", "message": "El proxy es obligatorio"})
    if proxy in config["proxies_lista"]:
        return jsonify({"status": "error", "message": "Este proxy ya existe"})
    config["proxies_lista"].append(proxy)
    anadir_log("INFO", f"Proxy anadido: {proxy}")
    return jsonify({"status": "ok", "message": "Proxy anadido"})

@app.route("/api/proxies/eliminar/<int:index>", methods=["DELETE"])
@login_required
def eliminar_proxy(index):
    if 0 <= index < len(config["proxies_lista"]):
        proxy = config["proxies_lista"].pop(index)
        anadir_log("WARN", f"Proxy eliminado: {proxy}")
        return jsonify({"status": "ok", "message": "Proxy eliminado"})
    return jsonify({"status": "error", "message": "Indice invalido"})

@app.route("/api/proxies/test", methods=["POST"])
@login_required
def test_proxy():
    data = request.get_json()
    proxy = data.get("proxy", "")
    if not proxy:
        return jsonify({"status": "error", "message": "No se proporciono proxy"})
    try:
        proxies = {"http": proxy, "https": proxy}
        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
        if response.status_code == 200:
            ip = response.json().get("origin", "desconocida")
            return jsonify({"status": "ok", "message": f"Proxy funciona - IP: {ip}", "ip": ip})
        return jsonify({"status": "error", "message": "Proxy no funciona"})
    except:
        return jsonify({"status": "error", "message": "Proxy no funciona"})

@app.route("/api/estadisticas", methods=["GET"])
@login_required
def obtener_estadisticas():
    return jsonify({
        "productos_activos": len(productos),
        "checkouts_completados": estadisticas["checkouts_completados"],
        "reintentos": estadisticas["reintentos"],
        "total_verificaciones": estadisticas["verificaciones"],
        "ultima_verificacion": estadisticas["ultima_verificacion"],
        "ultima_compra": estadisticas["ultima_compra"]
    })

@app.route("/api/logs", methods=["GET"])
@login_required
def obtener_logs():
    return jsonify({"logs": logs[-50:]})

@app.route("/api/logs/clear", methods=["POST"])
@login_required
def limpiar_logs():
    logs.clear()
    return jsonify({"status": "ok"})

@app.route("/api/monitoreo", methods=["POST"])
@login_required
def toggle_monitoreo():
    global hilo_monitoreo, detener_monitoreo
    if config["monitoreo_activo"]:
        detener_monitoreo.set()
        config["monitoreo_activo"] = False
        anadir_log("WARN", "Monitoreo detenido")
        return jsonify({"status": "ok", "message": "Monitoreo detenido", "activo": False})
    else:
        detener_monitoreo = threading.Event()
        hilo_monitoreo = threading.Thread(target=loop_monitoreo, daemon=True)
        hilo_monitoreo.start()
        config["monitoreo_activo"] = True
        anadir_log("SUCCESS", "Monitoreo iniciado")
        return jsonify({"status": "ok", "message": "Monitoreo iniciado", "activo": True})
def loop_monitoreo():
    anadir_log("INFO", "Bucle de monitoreo iniciado")
    while not detener_monitoreo.is_set():
        try:
            for producto in productos:
                if detener_monitoreo.is_set():
                    break
                intervalo = config["intervalo_turbo"] if config["modo_turbo"] else config["intervalo"]
                proxy = obtener_proxy_aleatorio()
                inicio = time.time()
                resultado = verificar_producto(producto["url"], proxy)
                latencia = int((time.time() - inicio) * 1000)
                estadisticas["verificaciones"] += 1
                estadisticas["tiempos_respuesta"].append(latencia)
                estadisticas["ultima_verificacion"] = datetime.now().strftime("%H:%M:%S")
                producto["ultima_verificacion"] = datetime.now().strftime("%H:%M:%S")
                if resultado.get("disponible"):
                    if not producto["disponible"]:
                        producto["disponible"] = True
                        producto["precio"] = resultado.get("precio")
                        producto["veces_disponible"] += 1
                        anadir_log("SUCCESS", f"Producto disponible: {producto['nombre']}")
                        if config["discord_webhook"]:
                            enviar_discord_notificacion(producto)
                        if config["datos_tarjeta"]["numero"]:
                            intentar_compra_automatica(producto)
                    else:
                        estadisticas["exitosas"] += 1
                else:
                    if producto["disponible"]:
                        producto["disponible"] = False
                        anadir_log("WARN", f"Producto agotado: {producto['nombre']}")
                    estadisticas["fallidas"] += 1
                time.sleep(min(intervalo, 2))
            if not config["modo_turbo"]:
                time.sleep(config["intervalo"])
        except Exception as e:
            anadir_log("ERROR", f"Error en monitoreo: {str(e)}")
            estadisticas["reintentos"] += 1
            time.sleep(5)
    anadir_log("INFO", "Monitoreo detenido")

def intentar_compra_automatica(producto):
    try:
        anadir_log("INFO", f"Intentando compra de {producto['nombre']}")
        proxy = obtener_proxy_aleatorio()
        resultado = compra_automatica(producto["url"], config["datos_tarjeta"], proxy=proxy)
        if resultado.get("success"):
            estadisticas["checkouts_completados"] += 1
            estadisticas["ultima_compra"] = datetime.now().strftime("%H:%M:%S")
            anadir_log("SUCCESS", f"Compra completada: {producto['nombre']}")
            if config["discord_webhook"]:
                enviar_discord_notificacion(producto, tipo="compra")
        else:
            anadir_log("ERROR", f"Compra fallida: {resultado.get('message', 'Error')}")
    except Exception as e:
        anadir_log("ERROR", f"Error en compra: {str(e)}")

def enviar_discord_notificacion(producto, tipo="stock"):
    try:
        webhook_url = config["discord_webhook"]
        if tipo == "stock":
            titulo = "STOCK DISPONIBLE"
        else:
            titulo = "COMPRA REALIZADA"
        mensaje = {
            "content": None,
            "embeds": [
                {
                    "title": titulo,
                    "description": f"{producto['nombre']} - {producto['tienda']} - {producto.get('precio', 'N/A')}",
                    "color": 3066993,
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        requests.post(webhook_url, json=mensaje)
    except Exception as e:
        anadir_log("ERROR", f"Error Discord: {str(e)}")
@app.route("/api/comprar/<int:index>", methods=["POST"])
@login_required
def comprar_producto(index):
    if 0 <= index < len(productos):
        producto = productos[index]
        if not config["datos_tarjeta"]["numero"]:
            return jsonify({"status": "error", "message": "Configura la tarjeta primero"})
        proxy = obtener_proxy_aleatorio()
        resultado = compra_automatica(producto["url"], config["datos_tarjeta"], proxy=proxy)
        if resultado.get("success"):
            estadisticas["checkouts_completados"] += 1
            anadir_log("SUCCESS", f"Compra manual: {producto['nombre']}")
            return jsonify({"status": "ok", "message": "Compra realizada"})
        else:
            return jsonify({"status": "error", "message": resultado.get("message", "Error")})
    return jsonify({"status": "error", "message": "Producto no encontrado"})

@app.route("/api/verificar/todas", methods=["POST"])
@login_required
def verificar_todas_tiendas():
    tiendas = {
        "cardmarket": "https://www.cardmarket.com",
        "toysrus": "https://www.toysrus.es",
        "unsobremas": "https://www.unsobremas.com",
        "flashstore": "https://www.flashstore.com",
        "turolgames": "https://www.turolgames.com"
    }
    resultados = {}
    for tienda, url in tiendas.items():
        try:
            proxy = obtener_proxy_aleatorio()
            resultado = verificar_producto(url, proxy)
            resultados[tienda] = {"disponible": resultado.get("disponible", False)}
        except:
            resultados[tienda] = {"disponible": False, "error": "Error"}
    return jsonify({"status": "ok", "resultados": resultados})

def guardar_datos():
    try:
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        with open("productos.json", "w") as f:
            json.dump(productos, f, indent=2)
    except:
        pass

def cargar_datos():
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                config.update(json.load(f))
        if os.path.exists("productos.json"):
            with open("productos.json", "r") as f:
                global productos
                productos = json.load(f)
    except:
        pass

cargar_datos()

@app.route('/')
def home():
    return "🤖 BOT DE COMPRAS AUTOMATICAS 24/7 funcionando!"

@app.route('/login')
def login():
    return "Página de login del bot"

if __name__ == "__main__":
    print("BOT DE COMPRAS AUTOMATICAS 24/7")
    print("http://localhost:5000")
    print("Usuario: admin")
    print("Contrasena: admin123")
    import atexit
    atexit.register(guardar_datos)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
