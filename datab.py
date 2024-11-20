import sqlite3
from datetime import datetime, timedelta

# Crear la base de datos y tablas
def initialize_database():
    connection = sqlite3.connect("prestamos.db")
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prestamos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        monto REAL NOT NULL,
        interes REAL NOT NULL,
        tipo_pago TEXT NOT NULL,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT NOT NULL,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prestamo_id INTEGER NOT NULL,
        fecha_pago TEXT NOT NULL,
        monto_pago REAL NOT NULL,
        FOREIGN KEY(prestamo_id) REFERENCES prestamos(id)
    )
    """)
    connection.commit()
    connection.close()

# Función para ajustar fechas
def ajustar_fecha(fecha):
    if fecha.weekday() == 6:  # Si es domingo
        return fecha + timedelta(days=1)
    return fecha

# Registrar un usuario
def registrar_usuario(nombre):
    connection = sqlite3.connect("prestamos.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO usuarios (nombre) VALUES (?)", (nombre,))
    connection.commit()
    connection.close()

# Crear un préstamo
def crear_prestamo(usuario_id, monto, interes, tipo_pago, fecha_inicio, duracion_meses):
    connection = sqlite3.connect("prestamos.db")
    cursor = connection.cursor()

    fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_fin = fecha_inicio_dt + timedelta(days=duracion_meses * 30)  # Aproximación
    fecha_fin_str = fecha_fin.strftime("%Y-%m-%d")
    cursor.execute("""
    INSERT INTO prestamos (usuario_id, monto, interes, tipo_pago, fecha_inicio, fecha_fin)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (usuario_id, monto, interes, tipo_pago, fecha_inicio, fecha_fin_str))
    prestamo_id = cursor.lastrowid

    # Calcular fechas de pagos
    monto_total = monto + (monto * (interes / 100))
    num_pagos = duracion_meses * (4 if tipo_pago == "semanal" else 1)
    monto_pago = monto_total / num_pagos

    for i in range(num_pagos):
        if tipo_pago == "semanal":
            fecha_pago = fecha_inicio_dt + timedelta(weeks=i)
        elif tipo_pago == "mensual":
            fecha_pago = fecha_inicio_dt + timedelta(days=30 * i)
        fecha_pago = ajustar_fecha(fecha_pago)
        cursor.execute("""
        INSERT INTO pagos (prestamo_id, fecha_pago, monto_pago)
        VALUES (?, ?, ?)
        """, (prestamo_id, fecha_pago.strftime("%Y-%m-%d"), monto_pago))

    connection.commit()
    connection.close()

# Generar reporte por usuario
def generar_reporte(usuario_id):
    connection = sqlite3.connect("prestamos.db")
    cursor = connection.cursor()

    cursor.execute("SELECT nombre FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()
    if not usuario:
        print("Usuario no encontrado")
        return
    print(f"Reporte para el usuario: {usuario[0]}")

    cursor.execute("""
    SELECT id, monto, interes, tipo_pago, fecha_inicio, fecha_fin
    FROM prestamos WHERE usuario_id = ?
    """, (usuario_id,))
    prestamos = cursor.fetchall()
    for prestamo in prestamos:
        print(f"\nPréstamo ID: {prestamo[0]}")
        print(f"Monto: {prestamo[1]:.2f}, Interés: {prestamo[2]}%, Tipo de pago: {prestamo[3]}")
        print(f"Fecha de inicio: {prestamo[4]}, Fecha de fin: {prestamo[5]}")
        print("Pagos:")
        cursor.execute("""
        SELECT fecha_pago, monto_pago
        FROM pagos WHERE prestamo_id = ?
        """, (prestamo[0],))
        pagos = cursor.fetchall()
        for pago in pagos:
            print(f"  - Fecha: {pago[0]}, Monto: {pago[1]:.2f}")

    connection.close()

# Ejemplo de uso
if __name__ == "__main__":
    initialize_database()
    registrar_usuario("Juan Pérez")
    registrar_usuario("María López")
    crear_prestamo(1, 1000, 10, "semanal", "2024-11-20", 2)
    crear_prestamo(2, 2000, 5, "mensual", "2024-11-20", 12)
    generar_reporte(1)
    generar_reporte(2)
