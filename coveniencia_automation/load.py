import os
import pandas as pd
import pyodbc

# Configura la cadena de conexión a tu base de datos SQL Server
connection_string = "Driver={SQL Server Native Client 11.0};Server=CCAZR-PROC01\PROC_cirugias;Database=ScrapingTDC;Uid=UsrInovacion;Pwd=M4ryW1tch041123!;"

# Ruta al directorio donde se encuentran los archivos CSV
directorio_archivos = ".\\csv"

# Lista de archivos CSV en el directorio
archivos_csv = [archivo for archivo in os.listdir(directorio_archivos) if archivo.endswith(".csv")]

# Función para cargar datos en SQL Server
def cargar_datos_en_sqlserver(archivo_csv):
    try:
        # Leer el archivo CSV en un DataFrame
        df = pd.read_csv(os.path.join(directorio_archivos, archivo_csv), sep='|')

        # Reemplazar los valores NaN en 'Precio' con una cadena vacía
        df['Precio'] = df['Precio'].fillna("")

        # Filtrar las filas donde 'DescripcionCorta' es vacío
        df = df[df['DescripcionCorta'].notna() & (df['DescripcionCorta'] != '')]

        # Verificar si la columna 'Promocion' existe en el DataFrame
        if 'Promocion' not in df.columns:
            df['Promocion'] = ''  # Agregar la columna con valores vacíos si no existe
        else:
            # Reemplazar celdas vacías en la columna 'Promocion' con ''
            df['Promocion'].fillna('', inplace=True)

        # Establecer la conexión a SQL Server
        conn = pyodbc.connect(connection_string)

        # Iterar a través de las filas del DataFrame y cargar los datos en SQL Server
        for index, row in df.iterrows():
            informante = row['Informante']
            categoria = row['Categoria']
            descripcioncorta = row['DescripcionCorta']
            precio = row['Precio']
            promocion = row['Promocion']
            fecha = row['Fecha']

            cursor = conn.cursor()

            # Insertar los datos en la tabla 'PreciosConveniencia' de SQL Server
            cursor.execute("INSERT INTO PreciosConveniencia (Informante, Categoria, DescripcionCorta, Precio, Promocion, Fecha) VALUES (?, ?, ?, ?, ?, ?)",
                           informante, categoria, descripcioncorta, precio, promocion, fecha)

            conn.commit()

            cursor.close()

        conn.close()
        print(f"Los datos del archivo {archivo_csv} se han cargado en SQL Server con éxito.")

    except Exception as e:
        print(f"Error al cargar los datos del archivo {archivo_csv} en SQL Server: {str(e)}")

# Iterar a través de los archivos CSV y cargar los datos en SQL Server
for archivo_csv in archivos_csv:
    cargar_datos_en_sqlserver(archivo_csv)
