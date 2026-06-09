import random

# =========================
# GENERAR PRODUCTOS 110-429
# =========================
VALID_PRODUCTS = [
    110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
    120, 121, 122, 123, 124, 125, 126, 127, 128, 129,

    210, 211, 212, 213, 214, 215, 216, 217, 218, 219,
    220, 221, 222, 223, 224, 225, 226, 227, 228, 229,

    310, 311, 312, 313, 314, 315, 316, 317, 318, 319,
    320, 321, 322, 323, 324, 325, 326, 327, 328, 329,

    410, 411, 412, 413, 414, 415, 416, 417, 418, 419,
    420, 421, 422, 423, 424, 425, 426, 427, 428, 429
]
# =========================

if 'order_counter' not in globals():
    order_counter = 0

# Variables internas para la orden generada
current_product_list = []
current_num_lineas = 0


def nueva_orden_id_fresco():
    global order_counter
    order_counter += 1
    return order_counter


def nueva_orden_num_lineas_fresco():
    global current_product_list, current_num_lineas

    current_num_lineas = 12

    productos_disponibles = VALID_PRODUCTS.copy()

    # pesos según la unidad
    # unidad 0 -> peso 1
    # unidad 9 -> peso 10

    pesos = []

    for p in productos_disponibles:
        unidad = p % 10
        peso = unidad + 1
        pesos.append(peso)
        current_product_list = []

    # selección sin repetidos pero ponderada
    for _ in range(current_num_lineas):

        elegido = random.choices(
            productos_disponibles,
            weights=pesos,
            k=1
        )[0]

        idx = productos_disponibles.index(elegido)

        current_product_list.append(elegido)

        productos_disponibles.pop(idx)
        pesos.pop(idx)

    return current_num_lineas


def nueva_orden_producto_fresco(i):
    i = int(i)
    return current_product_list[i - 1]

# Devuelve la lista de VALID_PRODUCTS para el control de cantidad en almacén
def valid_number_por_orden(i):
    i = int(i)
    return VALID_PRODUCTS[i - 1]