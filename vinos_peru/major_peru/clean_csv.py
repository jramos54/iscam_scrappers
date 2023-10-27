import csv

# Nombre del archivo CSV de entrada y salida
archivo_entrada = 'majorperu_productos_2023-10-04.csv'
archivo_salida = 'majorperu_productos_2023-10-06.csv'

# Lista para almacenar las líneas únicas
lineas_unicas = []

# Diccionario para llevar un registro de las líneas ya vistas
lineas_vistas = set()

with open(archivo_entrada, 'r', newline='',encoding='utf-8') as csvfile:
    lector_csv = csv.DictReader(csvfile, delimiter='|')
    encabezados = lector_csv.fieldnames

    lineas_unicas.append(encabezados)  # Agrega los encabezados al archivo de salida

    for fila in lector_csv:
        descripcion_corta = fila['DescripcionCorta']

        # Verifica si la descripción corta ya ha sido vista
        if descripcion_corta not in lineas_vistas:
            lineas_unicas.append([fila[campo] for campo in encabezados])
            lineas_vistas.add(descripcion_corta)

# Escribe las líneas únicas en un nuevo archivo CSV
with open(archivo_salida, 'w', newline='',encoding='utf-8') as csvfile:
    escritor_csv = csv.writer(csvfile, delimiter='|')
    escritor_csv.writerows(lineas_unicas)
