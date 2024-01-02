from PIL import Image
from collections import defaultdict
import numpy as np
from sklearn.cluster import KMeans
from io import BytesIO
import requests
import base64
import csv


def base_image(imagen_url):

    respuesta = requests.get(imagen_url)

    if respuesta.status_code == 200:
        imagen_base64 = base64.b64encode(respuesta.content).decode('utf-8')
        print("Imagen en formato Base64 descargada")
    else:
        print("No se pudo descargar la imagen. Código de estado:", respuesta.status_code)
    return imagen_base64

def base64_to_numpy(imagen_base64):
    imagen_bytes = base64.b64decode(imagen_base64)

    imagen = Image.open(BytesIO(imagen_bytes))

    imagen_np = np.array(imagen)
    print('Base64 to numpy done!')

    return imagen_np

def agrupar_colores_base64(imagen_base64, num_clusters):
    imagen_np = base64_to_numpy(imagen_base64)

    pixeles = imagen_np.reshape(-1, 4)  # 4 para RGBA

    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(pixeles)

    labels = kmeans.labels_

    colores = defaultdict(int)

    total_pixeles = len(labels)
    for label in labels:
        color = tuple(map(int, kmeans.cluster_centers_[label][:3]))  
        colores[color] += 1

    print('Agrupar colores done!')
    return colores

def calcular_porcentaje_colores_base64(imagen_base64, num_clusters):
    imagen_np = base64_to_numpy(imagen_base64)
    if imagen_np.size % 4 != 0:
        print("La imagen no tiene un tamaño válido para reshape.")
        return {(0, 0, 0): 100.0}  # Valor por defecto
    pixeles = imagen_np.reshape(-1, 4)  # 4 para RGBA

    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(pixeles)

    labels = kmeans.labels_

    colores = defaultdict(int)

    total_pixeles = len(labels)
    for label in labels:
        color = tuple(map(int, kmeans.cluster_centers_[label][:3]))  
        colores[color] += 1

    colores_porcentaje = {}
    for color, count in colores.items():
        porcentaje = (count / total_pixeles) * 100
        colores_porcentaje[color] = porcentaje

    return colores_porcentaje

def verificar_colores_base64(imagen_base64, valor_1, valor_2, valor_3):
    resultados = calcular_porcentaje_colores_base64(imagen_base64, 10)  
    negro=False
    gris=False
    light=False
    for color, porcentaje in resultados.items():
        
        print(f'{color} {porcentaje}')
        if color == (54, 54, 54) and porcentaje >= valor_1:
            print(f'{color} {porcentaje}')
            negro=True
        elif color == (5, 5, 5) and porcentaje >= valor_2:
            print(f'{color} {porcentaje}')
            gris=True
           
    print(f'negro:{negro} gris:{gris} light:{light}')
    if negro and gris:
        return False
    else:
        return True

if __name__=='__main__':
   
    num_clusters = 10  # Número de clusters deseados
      
    # links=[
    #     'https://oneiconn.vtexassets.com/arquivos/ids/183849-300-300?v=638026783009270000&width=300&height=300&aspect=true'
    #     ]
    # for link in links:
    #     imagen_base64=base_image(link)
    #     colores = agrupar_colores_base64(imagen_base64, num_clusters)
    #     porcentaje_colores = calcular_porcentaje_colores_base64(imagen_base64, num_clusters)
    #     es_valido = verificar_colores_base64(imagen_base64, 90, 3, 3)
    #     print('='*50)
    #     print(es_valido)
    #     print('='*50)



    archivo_entrada = 'productos_7-eleven2023-10-31.csv'
    archivo_salida = 'productos_7-eleven_2023-10-31.csv_imagen.csv'

    with open(archivo_entrada, 'r',encoding='utf-8') as entrada, open(archivo_salida, 'w', newline='') as salida:
        lector_csv = csv.DictReader(entrada, delimiter='|')
        campos = lector_csv.fieldnames

        escritor_csv = csv.DictWriter(salida, fieldnames=campos, delimiter='|')
        escritor_csv.writeheader()

        for fila in lector_csv:
            link = fila['Img']
            imagen_base64=base_image(link)
            if verificar_colores_base64(imagen_base64, 90, 3, 3):
                escritor_csv.writerow(fila)
                print('link sin cambios')
                
            else:
                print('link sin imagen')
                fila['Img'] = ''
                escritor_csv.writerow(fila)
                print(link)

    print("Proceso completado. El archivo con los cambios se encuentra en", archivo_salida)
