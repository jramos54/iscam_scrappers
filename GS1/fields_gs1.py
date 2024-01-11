import pandas as pd
import openpyxl,json


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


if __name__=="__main__":
    archivo_excel = r'1d2cbd6a-1b39-4d74-ac94-22cb42620991_out.xlsm'
    resultado = extraer_encabezados_excel(archivo_excel)
    sheets_to_import = ["Relationships", "Model", "Entities"]
    non_empty_cells_count = count_non_empty_cells(archivo_excel, sheets_to_import)
    print(json.dumps(non_empty_cells_count,indent=4))


