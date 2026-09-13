class Producto:
    def __init__(self, codigo, nombre, precio, stock):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def __repr__(self):
        return f"{self.codigo}: {self.nombre} (${self.precio})"


def catalogo_inicial():
    return [
        Producto("A01", "Agua SmartWater", 1600, 8),
        Producto("A02", "Jugo Aquarius", 2100, 6),
        Producto("A03", "Alfajor Guaymallen", 500, 10),
        Producto("A04", "Galletitas Pitusas", 1200, 2),
        Producto("A05", "Barrita Cereal Mix", 800, 5),
        Producto("A06", "Palitos de la Selva", 1500, 3),
        Producto("A07", "Chocolates Bon o Bon", 1100, 4),
        Producto("A08", "Gaseosa Coca-Cola", 3500, 7),
        Producto("A09", "Galletitas Oreo", 1700, 9),
        Producto("A10", "Chocolates Milka", 3500, 1),
        Producto("A12", "Hamburguesa Simple", 4000, 5),
        Producto("A13", "Pancho Simple", 1200, 10),
        Producto("A14", "Papas Fritas Krachitos", 2500, 2),
        Producto("A15", "Gomitas Mogul", 500, 6),
        Producto("A16", "Pipas", 480, 4),
        Producto("A17", "Don Satur (Grasa)", 1500, 3),
        Producto("A18", "Jugo Cepita", 3500, 5),
        Producto("A19", "Galletitas Chocolinas", 2500, 7),
        Producto("A20", "Alfajor Rasta", 1700, 9),
        Producto("A21", "Pebete", 1100, 4),
        Producto("A22", "Empanadas de carne", 2500, 3),
        Producto("A23", "Sprite", 5000, 10),
        Producto("A24","Surtido Bagley",3250,5),
        Producto("A25","Manaos cola",1700,5),
        Producto("A26","Placer",1400,5),
        Producto("A27","Helado de Agua Grido",720,5),
        Producto("A28","Cono de helado",6800,5),
        Producto("A29","Chicle beldent",800,5),
        Producto("A30","Cono de Papas",4600,5),
        Producto("A31","Pico dulce",350,5),
        Producto("A32", "Alfajor Jorgito", 1200, 8),
        Producto("A33", "Tita", 1000, 8),
        Producto("A34", "Rhodesia", 1300, 8),
        Producto("A35", "Mantecol", 1900, 6),
        Producto("A36", "Rocklets", 2200, 7),
        Producto("A37", "Flynn Paff", 300, 10),
        Producto("A38", "Caramelos Sugus", 1700, 8),
        Producto("A39", "Menthoplus", 900, 8),
        Producto("A40", "Halls", 900, 8),
        Producto("A41", "Doritos", 3800, 6),
        Producto("A42", "Papas Lays", 3800, 6),
        Producto("A43", "Cheetos", 3900, 6),
        Producto("A44", "Galletitas Pepitos", 2600, 7),
        Producto("A45", "Club Social", 2700, 8),
        Producto("A46", "Jugo Baggio", 2200, 8),
        Producto("A47", "Fanta", 2600, 8),
        Producto("A48", "Pepsi", 2100, 8),
        Producto("A49", "Paso de los Toros", 2000, 7),
        Producto("A50", "Energizante Speed", 3000, 6),
        Producto("A51", "Chocolate Cofler", 4200, 6),
        
        
        
        
        
    ]   

def buscar(productos, codigo):
    for producto in productos:
        if producto.codigo == codigo:
            return producto
    raise ValueError("El producto no existe.")


def cantidad_en_carrito(carrito, codigo):
    cantidad = 0
    for producto in carrito:
        if producto.codigo == codigo:
            cantidad += 1
    return cantidad


def total_carrito(carrito):
    total = 0
    for producto in carrito:
        total += producto.precio
    return total


def agregar(productos, carrito, codigo):
    producto = buscar(productos, codigo)
    if cantidad_en_carrito(carrito, codigo) >= producto.stock:
        raise ValueError("No queda stock para agregar otra unidad.")
    carrito.append(producto)


def confirmar(carrito, ventas):
    if not carrito:
        raise ValueError("El carrito está vacío.")
    for producto in carrito:
        cantidad = cantidad_en_carrito(carrito, producto.codigo)
        if cantidad > producto.stock:
            raise ValueError("El stock cambió. Revisá el carrito.")
    total = total_carrito(carrito)
    for producto in carrito:
        producto.stock -= 1
    ventas.append(total)
    carrito.clear()
    return total


def sugerir_pares(productos, presupuesto):
    if presupuesto <= 0:
        raise ValueError("El presupuesto debe ser mayor que cero.")
    opciones = []
    for i in range(len(productos)):
        for j in range(i + 1, len(productos)):
            primero = productos[i]
            segundo = productos[j]
            total = primero.precio + segundo.precio
            if primero.stock > 0 and segundo.stock > 0:
                if total <= presupuesto:
                    opciones.append([primero.nombre, segundo.nombre, total, presupuesto - total])
    return opciones