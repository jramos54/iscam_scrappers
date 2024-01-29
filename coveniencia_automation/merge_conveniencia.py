import os, json,csv
import re

def exportar_csv(diccionarios, nombre_archivo):
    # Obtener las claves del primer diccionario para definir los encabezados del CSV
    encabezados = diccionarios[0].keys()

    with open(nombre_archivo, 'w', newline='',encoding='utf-8') as archivo_csv:
        writer = csv.DictWriter(archivo_csv, fieldnames=encabezados, delimiter='|')

        # Escribir los encabezados en la primera línea del CSV
        writer.writeheader()

        # Escribir cada diccionario como una línea en el CSV
        for diccionario in diccionarios:
            writer.writerow(diccionario)
            
def read_files(directory):
    resultados = []
    patron = re.compile(r'(.+)_(\d{4}-\d{2})-\d{2}\.csv')

    for archivo in os.listdir(directory):
        coincidencia = patron.match(archivo)
        if coincidencia:
            nombre = coincidencia.group(1)
            periodo = coincidencia.group(2)

            encontrado = False
            for resultado in resultados:
                if resultado['nombre'] == nombre and resultado['periodo'] == periodo:
                    resultado['archivos'].append(archivo)
                    encontrado = True
                    break

            if not encontrado:
                resultados.append({
                    'nombre': nombre,
                    'periodo': periodo,
                    'archivos': [archivo]
                })

    return resultados

def make_names(resultado):
    nombre = resultado['nombre']
    periodo = resultado['periodo']
    nombre_archivo_mezclado = f'{nombre}_{periodo}_merged.csv'
    return nombre_archivo_mezclado

def get_file_values(resultado,directory=''):
    lista_diccionarios = []

    for archivo in resultado["archivos"]:
        archivo_ruta = os.path.join(directory, archivo)
        with open(archivo_ruta, "r", newline='', encoding="utf-8") as archivo_csv:
            lector_csv = csv.reader(archivo_csv, delimiter="|")
            encabezados = next(lector_csv) 

            for fila in lector_csv:
                elemento = {}
                for i, valor in enumerate(fila):
                    elemento[encabezados[i]] = valor
                lista_diccionarios.append(elemento)

    return lista_diccionarios

def save_json(diccionario, nombre_archivo):
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo_json:
            json.dump(diccionario, archivo_json, ensure_ascii=False, indent=4)
        print(f"El diccionario se ha guardado en '{nombre_archivo}'")
    except Exception as e:
        print(f"Error al guardar el diccionario en '{nombre_archivo}': {e}")

def merge_values(products):
    merged_products=[]
    
    for product in products:
        exist_product=False
        new_product={}
        for item in merged_products:
            
            if item['DescripcionCorta']==product['DescripcionCorta']:
                
                price=product['Precio']
                promocion=product.get('Promocion',None)
                fecha=product['Fecha']
                price_field=f"Precio_{fecha}"
                
                item[price_field]=price
                if promocion is not None:
                    promocion_field=f"Promocion_{fecha}"
                    item[promocion_field]=promocion
                # print(item)
                exist_product=True
            
        if not exist_product:
            price=product['Precio']
            promocion=product.get('Promocion',None)
            fecha=product['Fecha']
            price_field=f"Precio_{fecha}"
            
            for key,value in product.items():
                new_product[key]=value
                
            new_product.pop('Precio')
            new_product.pop('Fecha')
            new_product[price_field]=price
            if promocion is not None:
                # print(new_product)
                promocion_field=f"Promocion_{fecha}"
                new_product.pop('Promocion')
                new_product[promocion_field]=promocion
            merged_products.append(new_product)
    return merged_products
            
        
if __name__=="__main__":
    
    directorio = 'csv_merge'  
    
    resultados = read_files(directorio)
    # print(json.dumps(resultado,indent=4))
    for resultado in resultados:
        name=make_names(resultado)
        valores=get_file_values(resultado,directorio)
        merged=merge_values(valores)
        save_json(merged,name[:-4]+'.json')
        exportar_csv(merged,name)
        print(name)
