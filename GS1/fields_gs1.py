import pandas as pd
import openpyxl,json
import numpy as np



def extraer_encabezados_excel(archivo_excel):
    try:
        # Abrir el archivo de Excel con openpyxl
        workbook = openpyxl.load_workbook(archivo_excel, read_only=True)
        
        encabezados_por_pestaña = {}
        
        # Nombres de pestañas específicos que deseas procesar
        pestañas_deseadas = ["Relationships", "Model", "Entities"]
        
        # Iterar a través de todas las pestañas
        for nombre_pestaña in workbook.sheetnames:
            if nombre_pestaña in pestañas_deseadas:
                sheet = workbook[nombre_pestaña]
                
                # Obtener los encabezados de la segunda fila
                encabezados = []
                for row in sheet.iter_rows(min_row=2, max_row=2, values_only=True):
                    encabezados.extend(row)
                
                # Agregar los encabezados al diccionario de la pestaña
                encabezados_por_pestaña[nombre_pestaña] = encabezados
        
        # Guardar la salida en un archivo JSON
        with open('encabezados.json', 'w', encoding='utf-8') as json_file:
            json.dump(encabezados_por_pestaña, json_file, ensure_ascii=False, indent=4)
        
        return "Los encabezados se han guardado en 'encabezados.json'"
    except Exception as e:
        return str(e)



def count_non_empty_cells(file_path, sheets):
    """
    Cuenta las celdas no vacías en cada columna de las hojas especificadas de un archivo Excel.

    Parámetros:
    file_path (str): La ruta del archivo Excel.
    sheets (list): Lista de nombres de las hojas que se desean importar.

    Retorna:
    dict: Un diccionario donde cada clave es el nombre de la hoja y el valor es otro diccionario
          con el conteo de celdas no vacías para cada columna.
    """
    non_empty_counts = {}
    # for sheet in sheets:
    #     # Importar la hoja, omitiendo la primera fila (header=1)
    #     df = pd.read_excel(file_path, sheet_name=sheet, header=1)
    #     # Contar celdas no vacías para cada columna
    #     counts = df.count().to_dict()
    #     non_empty_counts[sheet] = counts
    for sheet in sheets:
        # Importar la hoja, omitiendo la primera fila (header=1)
        df = pd.read_excel(file_path, sheet_name=sheet, header=1)
        # Contar celdas no vacías para cada columna y excluir columnas con conteo cero
        counts = {col: count for col, count in df.count().items() if count > 0}
        non_empty_counts[sheet] = counts
    
    with open('cuantificacion.json', 'w', encoding='utf-8') as json_file:
        json.dump(non_empty_counts, json_file, ensure_ascii=False, indent=4)
                
    return non_empty_counts

def excel_to_json_null(input_excel_file, output_json_file, sheet_names):
    try:
        # Lee el archivo Excel
        xls = pd.ExcelFile(input_excel_file)
        data = {}

        for sheet_name in sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=1)  # Comienza desde la fila 2

            # Elimina las filas y columnas con todos los valores en blanco (NaN, null, None)
            df.dropna(axis=0, how='all', inplace=True)
            df.dropna(axis=1, how='all', inplace=True)

            # Convierte la hoja de datos a una lista de diccionarios
            # excluyendo explícitamente las claves con valores NaN, null o None
            sheet_data = []
            for _, row in df.iterrows():
                row_dict = {col: row[col] for col in df.columns if pd.notna(row[col])}
                sheet_data.append(row_dict)

            # Almacena la lista de diccionarios en el diccionario principal
            data[sheet_name] = sheet_data

        # Convierte el diccionario a formato JSON
        with open(output_json_file, 'w') as json_file:
            json.dump(data, json_file, default=str, indent=4)

        print(f"El archivo JSON '{output_json_file}' ha sido creado con éxito.")
    
    except Exception as e:
        print(f"Se produjo un error al procesar el archivo Excel: {str(e)}")



def excel_to_json(input_excel_file, output_json_file, sheet_names):
    try:
        # Lee el archivo Excel
        xls = pd.ExcelFile(input_excel_file)
        data = {}

        for sheet_name in sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=1)  # Comienza desde la fila 2

            # Elimina las filas con todos los valores en blanco
            df.dropna(axis=0, how='all', inplace=True)

            # Reemplaza los valores NaN, null o None con None
            df = df.where(pd.notnull(df), None)

            # Convierte la hoja de datos a un diccionario
            # Aquí, las celdas con None serán ignoradas en el diccionario
            sheet_dict = df.to_dict(orient='records')

            # Almacena el diccionario en el diccionario principal usando el nombre de la hoja como clave
            data[sheet_name] = sheet_dict

        # Convierte el diccionario a formato JSON
        with open(output_json_file, 'w') as json_file:
            json.dump(data, json_file, default=str, indent=4)  # Usamos default=str para manejar objetos no serializables

        print(f"El archivo JSON '{output_json_file}' ha sido creado con éxito.")
    
    except Exception as e:
        print(f"Se produjo un error al procesar el archivo Excel: {str(e)}")


if __name__=="__main__":
    archivo_excel = r'1d2cbd6a-1b39-4d74-ac94-22cb42620991_out.xlsm'
    resultado = extraer_encabezados_excel(archivo_excel)
    sheets_to_import = ["Relationships", "Model", "Entities"]
    non_empty_cells_count = count_non_empty_cells(archivo_excel, sheets_to_import)
    print(json.dumps(non_empty_cells_count,indent=4))
    excel_to_json(archivo_excel, 'ejemplo.json', sheets_to_import)
    excel_to_json_null(archivo_excel, 'ejemplo_null.json', sheets_to_import)


