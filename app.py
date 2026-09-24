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
    """Página principal - Redirige al login o dashboard"""
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
            return '''
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
            '''
    
    return '''
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
    '''

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for('login'))

# ============================================
# DASHBOARD
# ============================================

@app.route('/dashboard')
@login_requerido
def dashboard():
    """Panel principal"""
    datos = cargar_datos()
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - Bot de Compras</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .header {{ background: #128C7E; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .nav {{ display: flex; gap: 20px; margin-bottom: 20px; }}
            .nav a {{ text-decoration: none; color: #128C7E; padding: 10px 20px; background: white; border-radius: 5px; }}
            .nav a:hover {{ background: #e0e0e0; }}
            .nav a.active {{ background: #128C7E; color: white; }}
            .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }}
            .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .card h3 {{ margin: 0 0 10px 0; color: #333; }}
            .card .numero {{ font-size: 24px; font-weight: bold; color: #128C7E; }}
            table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #128C7E; color: white; }}
            tr:hover {{ background: #f5f5f5; }}
            .btn {{ padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; text-decoration: none; display: inline-block; }}
            .btn-editar {{ background: #ffc107; color: white; }}
            .btn-eliminar {{ background: #dc3545; color: white; }}
            .btn-agregar {{ background: #28a745; color: white; padding: 10px 20px; font-size: 16px; text-decoration: none; }}
            .btn:hover {{ opacity: 0.8; }}
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
                <div class="numero">{len(datos["productos"])}</div>
            </div>
            <div class="card">
                <h3>Total Compras</h3>
                <div class="numero">{len(datos["compras"])}</div>
            </div>
            <div class="card">
                <h3>Total Proxies</h3>
                <div class="numero">{len(datos["proxies"])}</div>
            </div>
            <div class="card">
                <h3>Valor Inventario</h3>
                <div class="numero">€{sum(p["precio"] * p["stock"] for p in datos["productos"]):.2f}</div>
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
                {''.join(f'''
                <tr>
                    <td>{p["id"]}</td>
                    <td>{p["nombre"]}</td>
                    <td>€{p["precio"]:.2f}</td>
                    <td>{p["stock"]}</td>
                    <td>
                        <a href="/editar_producto/{p["id"]}" class="btn btn-editar">✏️ Editar</a>
                        <a href="/eliminar_producto/{p["id"]}" class="btn btn-eliminar" onclick="return confirm('¿Eliminar?')">🗑️ Eliminar</a>
                    </td>
                </tr>
                ''' for p in datos["productos"][:5])}
            </tbody>
        </table>
        
        <br>
        <a href="/productos" class="btn btn-agregar">➕ Ver Todos los Productos</a>
    </body>
    </html>
    '''

# ============================================
# GESTIÓN DE PRODUCTOS
# ============================================

@app.route('/productos')
@login_requerido
def productos():
    """Lista de productos"""
    datos = cargar_datos()
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Productos - Bot de Compras</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .header {{ background: #128C7E; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .nav {{ display: flex; gap: 20px; margin-bottom: 20px; }}
            .nav a {{ text-decoration: none; color: #128C7E; padding: 10px 20px; background: white; border-radius: 5px; }}
            .nav a:hover {{ background: #e0e0e0; }}
            .nav a.active {{ background: #128C7E; color: white; }}
            table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #128C7E; color: white; }}
            tr:hover {{ background: #f5f5f5; }}
            .btn {{ padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; text-decoration: none; display: inline-block; }}
            .btn-editar {{ background: #ffc107; color: white; }}
            .btn-eliminar {{ background: #dc3545; color: white; }}
            .btn-agregar {{ background: #28a745; color: white; padding: 10px 20px; font-size: 16px; text-decoration: none; }}
            .btn:hover {{ opacity: 0.8; }}
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
                {''.join(f'''
                <tr>
                    <td>{p["id"]}</td>
                    <td>{p["nombre"]}</td>
                    <td>€{p["precio"]:.2f}</td>
                    <td>{p["stock"]}</td>
                    <td>
                        <a href="/editar_producto/{p["id"]}" class="btn btn-editar">✏️ Editar</a>
                        <a href="/eliminar_producto/{p["id"]}" class="btn btn-eliminar" onclick="return confirm('¿Eliminar?')">🗑️ Eliminar</a>
                    </td>
                </tr>
                ''' for p in datos["productos"])}
            </tbody>
        </table>
    </body>
    </html>
    '''

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
    
    return '''
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
    '''

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
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Editar Producto - Bot de Compras</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .header {{ background: #128C7E; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .form-box {{ background: white; padding: 30px; border-radius: 10px; max-width: 400px; }}
            input {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
            button {{ width: 100%; padding: 10px; background: #128C7E; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
            button:hover {{ background: #0e6b5e; }}
            .btn-cancelar {{ background: #dc3545; text-align: center; display: block; padding: 10px; border-radius: 5px; text-decoration: none; color: white; margin-top: 10px; }}
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
                <input type="text" name="nombre" value="{producto["nombre"]}" required>
                
                <label>Precio (€):</label>
                <input type="number" name="precio" step="0.01" value="{producto["precio"]}" required>
                
                <label>Stock:</label>
                <input type="number" name="stock" value="{producto["stock"]}" required>
                
                <button type="submit">Guardar Cambios</button>
            </form>
            <a href="/productos" class="btn-cancelar">Cancelar</a>
        </div>
    </body>
    </html>
    '''

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
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Proxies - Bot de Compras</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .header {{ background: #128C7E; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .nav {{ display: flex; gap: 20px; margin-bottom: 20px; }}
            .nav a {{ text-decoration: none; color: #128C7E; padding: 10px 20px; background: white; border-radius: 5px; }}
            .nav a:hover {{ background: #e0e0e0; }}
            .nav a.active {{ background: #128C7E; color: white; }}
            table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #128C7E; color: white; }}
            tr:hover {{ background: #f5f5f5; }}
            .btn {{ padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; text-decoration: none; display: inline-block; }}
            .btn-editar {{ background: #ffc107; color: white; }}
            .btn-eliminar {{ background: #dc3545; color: white; }}
            .btn-agregar {{ background: #28a745; color: white; padding: 10px 20px; font-size: 16px; text-decoration: none; }}
            .btn:hover {{ opacity: 0.8; }}
            .proxy-info {{ background: #e8f5e9; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔒 Gestión de Proxies</h1>
            <p>Bienvenido, admin | <a href="/logout" style="color: white;">Cerrar Sesión</a></p>
        </div>
        
        <div class="nav">
            <a href="/dashboard">📊 Dashboard</a>
            <a href="/productos">📦 Productos</a>
            <a href="/proxies" class="active">🔒 Proxies</a>
            <a href="/compras">🛒 Compras</a>
        </div>
        
        <div class="proxy-info">
            📌 Los proxies se utilizan para realizar compras de forma anónima y segura.
        </div>
        
        <a href="/agregar_proxy" class="btn btn-agregar" style="margin-bottom: 20px;">➕ Agregar Proxy</a>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>IP</th>
                    <th>Puerto</th>
                    <th>Usuario</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {''.join(f'''
                <tr>
                    <td>{proxy["id"]}</td>
                    <td>{proxy["ip"]}</td>
                    <td>{proxy["puerto"]}</td>
                    <td>{proxy.get("usuario", "-")}</td>
                    <td>
                        {"✅ Activo" if proxy.get("activo") else "❌ Inactivo"}
                    </td>
                    <td>
                        <a href="/editar_proxy/{proxy["id"]}" class="btn btn-editar">✏️ Editar</a>
                        <a href="/eliminar_proxy/{proxy["id"]}" class="btn btn-eliminar" onclick="return confirm('¿Eliminar?')">🗑️ Eliminar</a>
                    </td>
                </tr>
                ''' for proxy in datos["proxies"])}
            </tbody>
        </table>
        
        {'' if datos["proxies"] else '<p style="text-align: center; color: #666; margin-top: 20px;">No hay proxies configurados. Agrega uno para comenzar.</p>'}
    </body>
    </html>
    '''

@app.route('/agregar_proxy', methods=['GET', 'POST'])
@login_requerido
def agregar_proxy():
    """Agregar nuevo proxy"""
    if request.method == 'POST':
        datos = cargar_datos()
        ip = request.form.get('ip')
        puerto = request.form.get('puerto')
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        activo = request.form.get('activo') == 'on'
        
        nuevo_id = max([p["id"] for p in datos["proxies"]], default=0) + 1
        
        datos["proxies"].append({
            "id": nuevo_id,
            "ip": ip,
            "puerto": puerto,
            "usuario": usuario,
            "password": password,
            "activo": activo
        })
        
        guardar_datos(datos)
        return redirect(url_for('proxies'))
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agregar Proxy - Bot de Compras</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #128C7E; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .form-box { background: white; padding: 30px; border-radius: 10px; max-width: 400px; }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            button { width: 100%; padding: 10px; background: #128C7E; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0e6b5e; }
            .btn-cancelar { background: #dc3545; text-align: center; display: block; padding: 10px; border-radius: 5px; text-decoration: none; color: white; margin-top: 10px; }
            .checkbox-container { display: flex; align-items: center; margin: 10px 0; }
            .checkbox-container input { width: auto; margin-right: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>➕ Agregar Proxy</h1>
            <p>Bienvenido, admin | <a href="/logout" style="color: white;">Cerrar Sesión</a></p>
        </div>
        
        <div class="form-box">
            <form method="POST">
                <label>IP del Proxy:</label>
                <input type="text" name="ip" placeholder="192.168.1.1" required>
                
                <label>Puerto:</label>
                <input type="text" name="puerto" placeholder="8080" required>
                
                <label>Usuario (opcional):</label>
                <input type="text" name="usuario" placeholder="usuario">
                
                <label>Contraseña (opcional):</label>
                <input type="password" name="password" placeholder="contraseña">
                
                <div class="checkbox-container">
                    <input type="checkbox" name="activo" checked>
                    <label>Proxy Activo</label>
                </div>
                
                <button type="submit">Guardar Proxy</button>
            </form>
            <a href="/proxies" class="btn-cancelar">Cancelar</a>
        </div>
    </body>
    </html>
    '''

@app.route('/editar_proxy/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_proxy(id):
    """Editar proxy"""
    datos = cargar_datos()
    proxy = next((p for p in datos["proxies"] if p["id"] == id), None)
    
    if not proxy:
        return "Proxy no encontrado", 404
    
    if request.method == 'POST':
        proxy["ip"] = request.form.get('ip')
        proxy["puerto"] = request.form.get('puerto')
        proxy["usuario"] = request.form.get('usuario')
        proxy["password"] = request.form.get('password')
        proxy["activo"] = request.form.get('activo') == 'on'
        guardar_datos(datos)
        return redirect(url_for('proxies'))
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Editar Proxy - Bot de Compras</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .header {{ background: #128C7E; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .form-box {{ background: white; padding: 30px; border-radius: 10px; max-width: 400px; }}
            input {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
            button {{ width: 100%; padding: 10px; background: #128C7E; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
            button:hover {{ background: #0e6b5e; }}
            .btn-cancelar {{ background: #dc3545; text-align: center; display: block; padding: 10px; border-radius: 5px; text-decoration: none; color: white; margin-top: 10px; }}
            .checkbox-container {{ display: flex; align-items: center; margin: 10px 0; }}
            .checkbox-container input {{ width: auto; margin-right: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>✏️ Editar Proxy</h1>
            <p>Bienvenido, admin | <a href="/logout" style="color: white;">Cerrar Sesión</a></p>
        </div>
        
        <div class="form-box">
            <form method="POST">
                <label>IP del Proxy:</label>
                <input type="text" name="ip" value="{proxy["ip"]}" required>
                
                <label>Puerto:</label>
                <input type="text" name="puerto" value="{proxy["puerto"]}" required>
                
                <label>Usuario (opcional):</label>
                <input type="text" name="usuario" value="{proxy.get("usuario", "")}">
                
                <label>Contraseña (opcional):</label>
                <input type="password" name="password" value="{proxy.get("password", "")}">
                
                <div class="checkbox-container">
                    <input type="checkbox" name="activo" {"checked" if proxy.get("activo") else ""}>
                    <label>Proxy Activo</label>
                </div>
                
                <button type="submit">Guardar Cambios</button>
            </form>
            <a href="/proxies" class="btn-cancelar">Cancelar</a>
        </div>
    </body>
    </html>
    '''

@app.route('/eliminar_proxy/<int:id>')
@login_requerido
def eliminar_proxy(id):
    """Eliminar proxy"""
    datos = cargar_datos()
    datos["proxies"] = [p for p in datos["proxies"] if p["id"] != id]
    guardar_datos(datos)
    return redirect(url_for('proxies'))

# ============================================
# GESTIÓN DE COMPRAS
# ============================================

@app.route('/compras')
@login_requerido
def compras():
    """Lista de compras"""
    datos = cargar_datos()
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Compras - Bot de Compras</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .header {{ background: #128C7E; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .nav {{ display: flex; gap: 20px; margin-bottom: 20px; }}
            .nav a {{ text-decoration: none; color: #128C7E; padding: 10px 20px; background: white; border-radius: 5px; }}
            .nav a:hover {{ background: #e0e0e0; }}
            .nav a.active {{ background: #128C7E; color: white; }}
            table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #128C7E; color: white; }}
            tr:hover {{ background: #f5f5f5; }}
            .btn {{ padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; text-decoration: none; display: inline-block; }}
            .btn-eliminar {{ background: #dc3545; color: white; }}
            .btn:hover {{ opacity: 0.8; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛒 Historial de Compras</h1>
            <p>Bienvenido, admin | <a href="/logout" style="color: white;">Cerrar Sesión</a></p>
        </div>
        
        <div class="nav">
            <a href="/dashboard">📊 Dashboard</a>
            <a href="/productos">📦 Productos</a>
            <a href="/proxies">🔒 Proxies</a>
            <a href="/compras" class="active">🛒 Compras</a>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio Unitario</th>
                    <th>Total</th>
                    <th>Fecha</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {''.join(f'''
                <tr>
                    <td>{i+1}</td>
                    <td>{compra["producto"]}</td>
                    <td>{compra["cantidad"]}</td>
                    <td>€{compra["precio_unitario"]:.2f}</td>
                    <td>€{compra["total"]:.2f}</td>
                    <td>{compra["fecha"]}</td>
                    <td>
                        <a href="/eliminar_compra/{i}" class="btn btn-eliminar" onclick="return confirm('¿Eliminar?')">🗑️ Eliminar</a>
                    </td>
                </tr>
                ''' for i, compra in enumerate(datos["compras"]))}
            </tbody>
        </table>
        
        {'' if datos["compras"] else '<p style="text-align: center; color: #666; margin-top: 20px;">No hay compras registradas.</p>'}
    </body>
    </html>
    '''

@app.route('/eliminar_compra/<int:index>')
@login_requerido
def eliminar_compra(index):
    """Eliminar compra"""
    datos = cargar_datos()
    if 0 <= index < len(datos["compras"]):
        del datos["compras"][index]
        guardar_datos(datos)
    return redirect(url_for('compras'))

# ============================================
# INICIO DEL SERVIDOR
# ============================================

if __name__ == '__main__':
    print("🤖 Bot de Compras iniciado")
    print("📦 Cargando datos...")
    cargar_datos()
    print("✅ Datos cargados correctamente")
    print("🌐 Servidor iniciado")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
