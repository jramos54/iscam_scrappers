import csv

def reemplazar_descripcion_larga_con_corta(input_file, output_file):
    with open(input_file, mode='r', newline='') as infile, \
         open(output_file, mode='w', newline='') as outfile:
        
        reader = csv.reader(infile, delimiter='|')
        writer = csv.writer(outfile, delimiter='|')
        
        # Escribe la primera línea (encabezados)
        headers = next(reader)
        writer.writerow(headers)
        
        for row in reader:
            # Reemplaza la columna DescripcionLarga con DescripcionCorta
            row[5] = row[3]
            writer.writerow(row)

def extraer_precio(input_file, output_file):
    with open(input_file, mode='r', newline='') as infile, \
         open(output_file, mode='w', newline='') as outfile:
        
        reader = csv.reader(infile, delimiter='|')
        writer = csv.writer(outfile, delimiter='|')
        
        # Escribe la primera línea (encabezados)
        headers = next(reader)
        writer.writerow(headers)
        
        for row in reader:
            # Extrae el texto después de los ':' en el campo Precio
            row[4] = row[4].split(':')[-1].strip()
            writer.writerow(row)

# Ejemplo de uso
input_file = 'sutritienda_productos_2023-09-25_imagen.csv'
output_file_temp = 'archivo_temp.csv'
output_file_final = 'sutritienda_productos_2023-09-25.csv'

# Primero, reemplaza DescripcionLarga con DescripcionCorta
reemplazar_descripcion_larga_con_corta(input_file, output_file_temp)

# Luego, extrae el texto después de los ':' en el campo Precio
extraer_precio(output_file_temp, output_file_final)

# Finalmente, puedes eliminar el archivo temporal si no lo necesitas
import os
os.remove(output_file_temp)
