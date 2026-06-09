import random

# Lista de productos de seco
VALID_PRODUCTS = [
    110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
    120, 121, 122, 123, 124, 125, 126, 127, 128, 129,

    210, 211, 212, 213, 214, 215, 216, 217, 218, 219,
    220, 221, 222, 223, 224, 225, 226, 227, 228, 229,

    310, 311, 312, 313, 314, 315, 316, 317, 318, 319,
    320, 321, 322, 323, 324, 325, 326, 327, 328, 329,

    410, 411, 412, 413, 414, 415, 416, 417, 418, 419,
    420, 421, 422, 423, 424, 425, 426, 427, 428, 429,

    510, 511, 512, 513, 514, 515, 516, 517, 518, 519,
    520, 521, 522, 523, 524, 525, 526, 527, 528, 529,

    610, 611, 612, 613, 614, 615, 616, 617, 618, 619,
    620, 621, 622, 623, 624, 625, 626, 627, 628, 629
]

if 'order_counter' not in globals():
    order_counter = 0

# Variables internas para la orden generada
current_product_list = []
current_num_lineas = 0

# Genera ordenes de seco
def nueva_orden_id():
    global order_counter
    order_counter += 1
    return order_counter

# Genera una lista de productos para la orden, con 12 lineas, sin repetidos y ponderada por unidad
def nueva_orden_num_lineas():
    global current_product_list, current_num_lineas

    current_num_lineas = 12
    current_product_list = []

    productos_disponibles = VALID_PRODUCTS.copy()
    pesos = []

    for p in productos_disponibles:
        unidad = p % 10
        peso = 10 - unidad
        pesos.append(peso)

    for _ in range(current_num_lineas):
        elegido = random.choices(productos_disponibles, weights=pesos, k=1)[0]

        idx = productos_disponibles.index(elegido)

        current_product_list.append(elegido)

        productos_disponibles.pop(idx)
        pesos.pop(idx)

    return current_num_lineas


# Dado un numero de linea, devuelve el producto correspondiente
def nueva_orden_producto(i):
    i = int(i)
    return current_product_list[i - 1]

# Devuelve la cola destino de la orden
def nueva_orden_queue(i):
    i = int(i)
    num_queue = ((i - 1) % 3) + 1
    return num_queue

# Devuelve la lista de VALID_PRODUCTS para el control de cantidad en almacén
def valid_number_por_orden(i):
    i = int(i)
    return VALID_PRODUCTS[i - 1]