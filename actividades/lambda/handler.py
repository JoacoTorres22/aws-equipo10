import json
import boto3
import requests

BASE_URL = "https://api.mercadolibre.com"


def get_productos(event):
    params = event.get("queryStringParameters") or {}
    response = requests.get(f"{BASE_URL}/sites/MLA/search", params=params)
    response.raise_for_status()
    return {"statusCode": 200, "body": json.dumps(response.json())}


def get_producto_by_id(event):
    product_id = event.get("pathParameters", {}).get("id")
    if not product_id:
        return {"statusCode": 400, "body": json.dumps({"error": "id requerido"})}
    response = requests.get(f"{BASE_URL}/items/{product_id}")
    response.raise_for_status()
    return {"statusCode": 200, "body": json.dumps(response.json())}


def put_producto(event):
    body = json.loads(event.get("body") or "{}")
    if not body:
        return {"statusCode": 400, "body": json.dumps({"error": "body requerido"})}
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("productos")
    table.put_item(Item=body)
    return {"statusCode": 200, "body": json.dumps({"message": "Producto guardado", "item": body})}


def get_descripcion(event):
    product_id = event.get("pathParameters", {}).get("id")
    if not product_id:
        return {"statusCode": 400, "body": json.dumps({"error": "id requerido"})}
    response = requests.get(f"{BASE_URL}/items/{product_id}/description")
    response.raise_for_status()
    return {"statusCode": 200, "body": json.dumps(response.json())}


def handler(event, context):
    method = event.get("httpMethod", "GET")
    path = event.get("path", "/productos")

    routes = {
        ("GET", "/productos"): get_productos,
        ("GET", "/productos/{id}"): get_producto_by_id,
        ("GET", "/productos/{id}/descripcion"): get_descripcion,
        ("PUT", "/productos"): put_producto,
    }

    # match path with id parameter
    route_key = (method, path)
    if method == "GET" and path.startswith("/productos/"):
        if path.endswith("/descripcion"):
            route_key = ("GET", "/productos/{id}/descripcion")
        else:
            route_key = ("GET", "/productos/{id}")

    func = routes.get(route_key)
    if not func:
        return {"statusCode": 404, "body": json.dumps({"error": "Ruta no encontrada"})}

    return func(event)
