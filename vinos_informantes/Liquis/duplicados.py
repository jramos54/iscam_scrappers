def eliminar_duplicados(archivo_entrada, archivo_salida):
    lineas_procesadas = set()
    lineas_nuevas = []

    with open(archivo_entrada, 'r', encoding='utf-8') as entrada:
        encabezado = entrada.readline()
        lineas_nuevas.append(encabezado)
        
        for linea in entrada:
            sku = linea.split('|')[2]  # El SKU es el tercer campo (índice 2)
            if sku not in lineas_procesadas:
                lineas_procesadas.add(sku)
                lineas_nuevas.append(linea)

    with open(archivo_salida, 'w', encoding='utf-8') as salida:
        for linea in lineas_nuevas:
            salida.write(linea)

# Llamar a la función para eliminar duplicados
archivo_entrada = 'liquis_productos_2023-08-17.csv'
archivo_salida = 'liquis_productos_2023-08-24.csv'
eliminar_duplicados(archivo_entrada, archivo_salida)

print("Duplicados eliminados y archivo guardado.")
