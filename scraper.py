def verificar_producto(url, proxy=None):
    return {"disponible": False, "precio": None}

def compra_automatica(url, datos_tarjeta, proxy=None, usar_captcha=False, api_key_captcha=""):
    return {"success": False, "message": "No implementado"}

def obtener_info_producto(url, proxy=None):
    return {"nombre": "Producto", "precio": None}

def detectar_tienda(url):
    return "Desconocida"
