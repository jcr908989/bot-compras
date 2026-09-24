from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura_123'

# ============================================
# BASE DE DATOS
# ============================================

def cargar_datos():
    """Carga los datos de productos y compras"""
    try:
        with open('datos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
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
            "compras": [],
            "proxies": []
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
    
    for p in datos["productos"]:
        if p["id"] == producto["id"]:
            p["stock"] -= cantidad
            break
    
    guardar_datos(datos)
    return compra

# ============================================
# AUTENTICACIÓN
# ============================================

def login_requerido(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorador(*args, **kwargs):
        if not session.get('logueado'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorador

# ============================================
# RUTAS PRINCIPALES
# ============================================

@app.route('/')
def home():
    """Página principal"""
    if session.get('logueado'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        if usuario == 'admin' and password == 'admin123':
            session['logueado'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login - Bot de Compras</title>
                <style>
                    body { font-family: Arial, sans-serif; background: #f0f0f0; display: flex; justify-content: center; align-items: center; height: 100vh; }
                    .login-box { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 300px; }
                    h1 { color: #128C7E; text-align: center; }
                    input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
                    button { width: 100%; padding: 10px; background: #128C7E; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
                    button:hover { background: #0e6b5e; }
                    .error { color: red; text-align: center; margin: 10px 0; }
                </style>
            </head>
            <body>
                <div class="login-box">
                    <h1>🤖 Bot de Compras</h1>
                    <div class="error">❌ Usuario o contraseña incorrectos</div>
                    <form method="POST">
                        <input type="text" name="usuario" placeholder="Usuario" required>
                        <input type="password" name="password" placeholder="Contraseña" required>
                        <button type="submit">Iniciar Sesión</button>
                    </form>
                </div>
            </body>
            </html>
            ''')
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - Bot de Compras</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f0f0f0; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .login-box { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 300px; }
            h1 { color: #128C7E; text-align: center; }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            button { width: 100%; padding: 10px; background: #128C7E; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0e6b5e; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h1>🤖 Bot de Compras</h1>
            <form method="POST">
                <input type="text" name="usuario" placeholder="Usuario" required>
                <input type="password" name="password" placeholder="Contraseña" required>
                <button type="submit">Iniciar Sesión</button>
            </form>
        </div>
    </body>
    </html>
    ''')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for('login'))

# ============================================
# DASHBOARD PRINCIPAL
# ============================================

@app.route('/dashboard')
@login_requerido
def dashboard():
    """Panel principal"""
    datos = cargar_datos()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - Bot de Compras</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #128C7E; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .nav { display: flex; gap: 20px; margin-bottom: 20px; }
            .nav a { text-decoration: none; color: #128C7E; padding: 10px 20px; background: white; border-radius: 5px; }
            .nav a:hover { background: #e0e0e0; }
            .nav a.active { background: #128C7E; color: white; }
            .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .card h3 { margin: 0 0 10px 0; color: #333; }
            .card .numero { font-size: 24px; font-weight: bold; color: #128C7E; }
            table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #128C7E; color: white; }
            tr:hover { background: #f5f5f5; }
            .btn { padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; }
            .btn-editar { background: #ffc107; color: white; }
            .btn-eliminar { background: #dc3545; color: white; }
            .btn-agregar { background: #28a745; color: white; padding: 10px 20px; font-size: 16px; }
            .btn:hover { opacity: 0.8; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 Bot de Compras - Dashboard</h1>
            <p>Bienvenido, admin | <a href="/logout" style="color: white;">Cerrar Sesión</a></p>
        </div>
        
        <div class="nav">
            <a href="/dashboard" class="active">📊 Dashboard</a>
            <a href="/productos">📦 Productos</a>
            <a href="/proxies">🔒 Proxies</a>
            <a href="/compras">🛒 Compras</a>
        </div>
        
        <div class="cards">
            <div class="card">
                <h3>Total Productos</h3>
                <div class="numero">{{ datos.productos|length }}</div>
            </div>
            <div class="card">
                <h3>Total Compras</h3>
                <div class="numero">{{ datos.compras|length }}</div>
            </div>
            <div class="card">
                <h3>Total Proxies</h3>
                <div class="numero">{{ datos.proxies|length }}</div>
            </div>
            <div class="card">
                <h3>Valor Inventario</h3>
                <div class="numero">€{{ valor_inventario }}</div>
            </div>
        </div>
        
        <h2>📦 Últimos Productos</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Precio</th>
                    <th>Stock</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for p in datos.productos[:5] %}
                <tr>
                    <td>{{ p.id }}</td>
                    <td>{{ p.nombre }}</td>
                    <td>€{{ "%.2f"|format(p.precio) }}</td>
                    <td>{{ p.stock }}</td>
                    <td>
                        <a href="/editar_producto/{{ p.id }}" class="btn btn-editar">✏️ Editar</a>
                        <a href="/eliminar_producto/{{ p.id }}" class="btn btn-eliminar" onclick="return confirm('¿Eliminar?')">🗑️ Eliminar</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <br>
        <a href="/productos" class="btn btn-agregar">➕ Ver Todos los Productos</a>
    </body>
    </html>
    ''', datos=datos, valor_inventario=sum(p["precio"] * p["stock"] for p in datos["productos"]))

# ============================================
# GESTIÓN DE PRODUCTOS
# ============================================

@app.route('/productos')
@login_requerido
def productos():
    """Lista de productos"""
    datos = cargar_datos()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Productos - Bot de Compras</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #128C7E; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .nav { display: flex; gap: 20px; margin-bottom: 20px; }
            .nav a { text-decoration: none; color: #128C7E; padding: 10px 20px; background: white; border-radius: 5px; }
            .nav a:hover { background: #e0e0e0; }
            .nav a.active { background: #128C7E; color: white; }
            table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #128C7E; color: white; }
            tr:hover { background: #f5f5f5; }
            .btn { padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; text-decoration: none; display: inline-block; }
            .btn-editar { background: #ffc107; color: white; }
            .btn-eliminar { background: #dc3545; color: white; }
            .btn-agregar { background: #28a745; color: white; padding: 10px 20px; font-size: 16px; text-decoration: none; }
            .btn:hover { opacity: 0.8; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📦 Gestión de Productos</h1>
            <p>Bienvenido, admin | <a href="/logout" style="color: white;">Cerrar Sesión</a></p>
        </div>
        
        <div class="nav">
            <a href="/dashboard">📊 Dashboard</a>
            <a href="/productos" class="active">📦 Productos</a>
            <a href="/proxies">🔒 Proxies</a>
            <a href="/compras">🛒 Compras</a>
        </div>
        
        <a href="/agregar_producto" class="btn btn-agregar" style="margin-bottom: 20px;">➕ Agregar Producto</a>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Precio</th>
                    <th>Stock</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for p in datos.productos %}
                <tr>
                    <td>{{ p.id }}</td>
                    <td>{{ p.nombre }}</td>
                    <td>€{{ "%.2f"|format(p.precio) }}</td>
                    <td>{{ p.stock }}</td>
                    <td>
                        <a href="/editar_producto/{{ p.id }}" class="btn btn-editar">✏️ Editar</a>
                        <a href="/eliminar_producto/{{ p.id }}" class="btn btn-eliminar" onclick="return confirm('¿Eliminar?')">🗑️ Eliminar</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    ''', datos=datos)

@app.route('/agregar_producto', methods=['GET', 'POST'])
@login_requerido
def agregar_producto():
    """Agregar nuevo producto"""
    if request.method == 'POST':
        datos = cargar_datos()
        nombre = request.form.get('nombre')
        precio = float(request.form.get('precio'))
        stock = int(request.form.get('stock'))
        
        nuevo_id = max([p["id"] for p in datos["productos"]], default=0) + 1
        
        datos["productos"].append({
            "id": nuevo_id,
            "nombre": nombre,
            "precio": precio,
            "stock": stock
        })
        
        guardar_datos(datos)
        return redirect(url_for('productos'))
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agregar Producto - Bot de Compras</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #128C7E; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .form-box { background: white; padding: 30px; border-radius: 10px; max-width: 400px; }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            button { width: 100%; padding: 10px; background: #128C7E; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0e6b5e; }
            .btn-cancelar { background: #dc3545; text-align: center; display: block; padding: 10px; border-radius: 5px; text-decoration: none; color: white; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>➕ Agregar Producto</h1>
            <p>Bienvenido, admin | <a href="/logout" style="color: white;">Cerrar Sesión</a></p>
        </div>
        
        <div class="form-box">
            <form method="POST">
                <label>Nombre del Producto:</label>
                <input type="text" name="nombre" required>
                
                <label>Precio (€):</label>
                <input type="number" name="precio" step="0.01" required>
                
                <label>Stock:</label>
                <input type="number" name="stock" required>
                
                <button type="submit">Guardar Producto</button>
            </form>
            <a href="/productos" class="btn-cancelar">Cancelar</a>
        </div>
    </body>
    </html>
    ''')

@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_producto(id):
    """Editar producto"""
    datos = cargar_datos()
    producto = next((p for p in datos["productos"] if p["id"] == id), None)
    
    if not producto:
        return "Producto no encontrado", 404
    
    if request.method == 'POST':
        producto["nombre"] = request.form.get('nombre')
        producto["precio"] = float(request.form.get('precio'))
        producto["stock"] = int(request.form.get('stock'))
        guardar_datos(datos)
        return redirect(url_for('productos'))
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Editar Producto - Bot de Compras</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #128C7E; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .form-box { background: white; padding: 30px; border-radius: 10px; max-width: 400px; }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            button { width: 100%; padding: 10px; background: #128C7E; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0e6b5e; }
            .btn-cancelar { background: #dc3545; text-align: center; display: block; padding: 10px; border-radius: 5px; text-decoration: none; color: white; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>✏️ Editar Producto</h1>
            <p>Bienvenido, admin | <a href="/logout" style="color: white;">Cerrar Sesión</a></p>
        </div>
        
        <div class="form-box">
            <form method="POST">
                <label>Nombre del Producto:</label>
                <input type="text" name="nombre" value="{{ producto.nombre }}" required>
                
                <label>Precio (€):</label>
                <input type="number" name="precio" step="0.01" value="{{ producto.precio }}" required>
                
                <label>Stock:</label>
                <input type="number" name="stock" value="{{ producto.stock }}" required>
                
                <button type="submit">Guardar Cambios</button>
            </form>
            <a href="/productos" class="btn-cancelar">Cancelar</a>
        </div>
    </body>
    </html>
    ''', producto=producto)

@app.route('/eliminar_producto/<int:id>')
@login_requerido
def eliminar_producto(id):
    """Eliminar producto"""
    datos = cargar_datos()
    datos["productos"] = [p for p in datos["productos"] if p["id"] != id]
    guardar_datos(datos)
    return redirect(url_for('productos'))

# ============================================
# GESTIÓN DE PROXIES
# ============================================

@app.route('/proxies')
@login_requerido
def proxies():
    """Lista de proxies"""
    datos = cargar_datos()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Proxies - Bot de Compras</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #128C7E; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .nav { display: flex; gap: 20px; margin-bottom: 20px; }
            .nav a { text-decoration: none; color: #128C7E; padding: 10px 20px; background: white; border-radius: 5px; }
            .nav a:hover { background: #e0e0e0; }
            .nav a.active { background: #128C7E; color: white; }
            table { width: 100%; border-collapse: collapse; background: white;
