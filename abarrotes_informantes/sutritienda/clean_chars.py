import os
from datetime import datetime

def limpiar_csv(archivo_entrada, archivo_salida, **caracteres_a_reemplazar):
    with open(archivo_entrada, 'r', encoding='utf-8') as entrada:
        lineas = entrada.readlines()

    lineas_limpias = []
    for linea in lineas:
        linea_limpia = linea
        for caracter, reemplazo in caracteres_a_reemplazar.items():
            linea_limpia = linea_limpia.replace(caracter, reemplazo)
        lineas_limpias.append(linea_limpia)

    with open(archivo_salida, 'w', encoding='utf-8') as salida:
        salida.writelines(lineas_limpias)

directorio = '.'  # Directorio actual, cambia a la ubicación deseada

# Definir caracteres a reemplazar en forma de diccionario
caracteres_a_reemplazar = {
    '\u00a0': '',  # U+00a0: Espacio no rompible
    '\u200e': '',
       '"':'',
       '\u2212':'', # U+2212
       '\u00b4':'', # ´
       '\u00a0':''   # U+00a0
}

#
#  Iterar a través de los archivos en el directorio
for archivo in os.listdir(directorio):
    if archivo.endswith('.csv'):
        archivo_entrada = os.path.join(directorio, archivo)
        
        # Extraer la fecha del archivo de entrada
        fecha_archivo = archivo.split('_')[-1].split('.')[0]
        
        # Obtener la fecha actual
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        
        archivo_salida = os.path.join(directorio, archivo.replace(fecha_archivo, fecha_actual))
        
        limpiar_csv(archivo_entrada, archivo_salida, **caracteres_a_reemplazar)
        print(f"CSV {archivo} limpiado y archivo guardado como {archivo_salida}.")

print("Proceso completo.")
