from PIL import Image
from collections import defaultdict
import numpy as np
from sklearn.cluster import KMeans
from io import BytesIO
import requests
import base64
import csv


def agrupar_colores(imagen_path, num_clusters):
    # Abre la imagen
    imagen = Image.open(imagen_path)

    # Convierte la imagen a una matriz numpy
    imagen_np = np.array(imagen)

    # Redimensiona la matriz de la imagen para tener una lista de píxeles
    píxeles = imagen_np.reshape(-1, 4)  # 4 para RGBA

    # Crea un modelo K-Means con el número de clusters deseado
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(píxeles)

    # Asigna cada píxel a su cluster correspondiente
    labels = kmeans.labels_

    # Inicializa un diccionario para rastrear los colores y su recuento
    colores = defaultdict(int)

    # Itera a través de cada píxel y cuenta los colores
    total_pixeles = len(labels)
    for label in labels:
        color = tuple(map(int, kmeans.cluster_centers_[label][:3]))  # Ignora el canal alfa
        colores[color] += 1

    # Cierra la imagen
    imagen.close()

    return colores

def calcular_porcentaje_colores(imagen_path, num_clusters):
    # Abre la imagen
    imagen = Image.open(imagen_path)

    # Convierte la imagen a una matriz numpy
    imagen_np = np.array(imagen)

    # Redimensiona la matriz de la imagen para tener una lista de píxeles
    píxeles = imagen_np.reshape(-1, 4)  # 4 para RGBA

    # Crea un modelo K-Means con el número de clusters deseado
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(píxeles)

    # Asigna cada píxel a su cluster correspondiente
    labels = kmeans.labels_

    # Inicializa un diccionario para rastrear los colores y su recuento
    colores = defaultdict(int)

    # Itera a través de cada píxel y cuenta los colores
    total_pixeles = len(labels)
    for label in labels:
        color = tuple(map(int, kmeans.cluster_centers_[label][:3]))  # Ignora el canal alfa
        colores[color] += 1

    # Calcula el porcentaje de aparición de cada color
    colores_porcentaje = {}
    for color, count in colores.items():
        porcentaje = (count / total_pixeles) * 100
        colores_porcentaje[color] = porcentaje

    # Cierra la imagen
    imagen.close()

    return colores_porcentaje

def verificar_colores(imagen_path, valor_1, valor_2, valor_3):
    # Calcula el porcentaje de aparición de cada color en la imagen
    resultados = calcular_porcentaje_colores(imagen_path, 10)  # 10 es un número de clusters predeterminado

    # Comprueba si los valores de color coinciden con los proporcionados
    for color, porcentaje in resultados.items():
        # print(f'{color} {porcentaje}')
        if color == (254, 254, 254) and porcentaje >= valor_1:
            return False
        elif color == (207, 52, 59) and porcentaje >= valor_2:
            return False
        elif color == (61, 202, 55) and porcentaje >= valor_3:
            return False

    # Si los valores NO coinciden, devuelve False
    return True

def base_image(imagen_url):

    # Realiza la solicitud GET para descargar la imagen
    respuesta = requests.get(imagen_url)

    # Verifica si la solicitud fue exitosa (código de estado 200)
    if respuesta.status_code == 200:
        # Convierte los datos de la imagen en una cadena Base64
        imagen_base64 = base64.b64encode(respuesta.content).decode('utf-8')
        print("Imagen en formato Base64 descargada")
        # print(imagen_base64)
    else:
        print("No se pudo descargar la imagen. Código de estado:", respuesta.status_code)
    return imagen_base64

def base64_to_numpy(imagen_base64):
    # Decodifica la imagen en base64
    imagen_bytes = base64.b64decode(imagen_base64)

    # Convierte los bytes en una imagen PIL
    imagen = Image.open(BytesIO(imagen_bytes))

    # Convierte la imagen a una matriz numpy
    imagen_np = np.array(imagen)
    print('Base64 to numpy done!')

    return imagen_np

def agrupar_colores_base64(imagen_base64, num_clusters):
    # Convierte la imagen en base64 en una matriz numpy
    imagen_np = base64_to_numpy(imagen_base64)

    # Redimensiona la matriz de la imagen para tener una lista de píxeles
    pixeles = imagen_np.reshape(-1, 4)  # 4 para RGBA

    # Crea un modelo K-Means con el número de clusters deseado
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(pixeles)

    # Asigna cada píxel a su cluster correspondiente
    labels = kmeans.labels_

    # Inicializa un diccionario para rastrear los colores y su recuento
    colores = defaultdict(int)

    # Itera a través de cada píxel y cuenta los colores
    total_pixeles = len(labels)
    for label in labels:
        color = tuple(map(int, kmeans.cluster_centers_[label][:3]))  # Ignora el canal alfa
        colores[color] += 1

    print('Agrupar colores done!')
    return colores

def calcular_porcentaje_colores_base64(imagen_base64, num_clusters):
    # Convierte la imagen en base64 en una matriz numpy
    imagen_np = base64_to_numpy(imagen_base64)
    if imagen_np.size % 4 != 0:
        print("La imagen no tiene un tamaño válido para reshape.")
        return {(0, 0, 0): 100.0}  # Valor por defecto
    # Redimensiona la matriz de la imagen para tener una lista de píxeles
    pixeles = imagen_np.reshape(-1, 4)  # 4 para RGBA

    # Crea un modelo K-Means con el número de clusters deseado
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(pixeles)

    # Asigna cada píxel a su cluster correspondiente
    labels = kmeans.labels_

    # Inicializa un diccionario para rastrear los colores y su recuento
    colores = defaultdict(int)

    # Itera a través de cada píxel y cuenta los colores
    total_pixeles = len(labels)
    for label in labels:
        color = tuple(map(int, kmeans.cluster_centers_[label][:3]))  # Ignora el canal alfa
        colores[color] += 1

    # Calcula el porcentaje de aparición de cada color
    colores_porcentaje = {}
    for color, count in colores.items():
        porcentaje = (count / total_pixeles) * 100
        colores_porcentaje[color] = porcentaje
        #print(f'color {color} = {colores_porcentaje[color]}')

    return colores_porcentaje

def verificar_colores_base64(imagen_base64, valor_1, valor_2, valor_3):
    # Calcula el porcentaje de aparición de cada color en la imagen
    resultados = calcular_porcentaje_colores_base64(imagen_base64, 10)  # 10 es un número de clusters predeterminado

    # Comprueba si los valores de color coinciden con los proporcionados
    negro=False
    gris=False
    light=False
    for color, porcentaje in resultados.items():
        
        
        if color == (254, 254, 254) and porcentaje >= valor_1:
            print(f'{color} {porcentaje}')
            negro=True
            # print(negro)
        elif color == (207, 52, 59) and porcentaje >= valor_2:
            print(f'{color} {porcentaje}')
            gris=True
            # print(gris)
        elif color == (61, 202, 55) and porcentaje >= valor_3:
            print(f'{color} {porcentaje}')
            light=True
            # print(light)
    print(f'negro:{negro} gris:{gris} light:{light}')
    if negro and gris and light:
        return False
    else:
        return True

if __name__=='__main__':
    imagen_path = ['productosinimagen.webp','07503000555097.1.webp','07501018310592.1.webp']  # , Reemplaza con la ruta de tu imagen
    num_clusters = 10  # Número de clusters deseados

    # for imagen in imagen_path:
        
    #     resultados = calcular_porcentaje_colores(imagen, num_clusters)
    #     for color, porcentaje in resultados.items():
    #         print(f'Color (RGB) {color} aparece en un {porcentaje:.2f}% de la imagen')
    #     resultado = verificar_colores(imagen, 87, 3, 3)
    #     print(resultado)
    
    # links=[
    #     'https://www.elreydeldulce.com/web/image/product.product/2058/image_1024/%5BCLMOZ%5D%20CHOC%20RICOLINO%20MONEDA%2024-45%20PZS?unique=28f9d51',
    #     'https://www.elreydeldulce.com/web/image/product.product/2057/image_1024/%5BCLBLUM%5D%20CHOC%20RICOLINO%20MINI%20LUNETA%2014-16%20PZS?unique=28f9d51',
    #     'https://www.elreydeldulce.com/web/image/product.product/63/image_1024/%5BBESIS%5D%20BEBIDA%20SABOREX%20INFANTIL%20SURTIDO%2024-250%20ML?unique=28f9d51'
    #     ]
    # for link in links:
    #     imagen_base64=base_image(link)
    #     #colores = agrupar_colores_base64(imagen_base64, num_clusters)
    #     #porcentaje_colores = calcular_porcentaje_colores_base64(imagen_base64, num_clusters)
    #     es_valido = verificar_colores_base64(imagen_base64, 66, 31, 1)
    #     print('='*50)
    #     print(es_valido)
    #     print('='*50)



    archivo_entrada = 'sutritienda_productos_2023-09-20.csv'
    archivo_salida = 'sutritienda_productos_2023-09-20_imagen.csv'

# Abre el archivo CSV de entrada y crea uno nuevo para escribir los resultados
    with open(archivo_entrada, 'r') as entrada, open(archivo_salida, 'w', newline='') as salida:
        lector_csv = csv.DictReader(entrada, delimiter='|')
        campos = lector_csv.fieldnames

        escritor_csv = csv.DictWriter(salida, fieldnames=campos, delimiter='|')
        escritor_csv.writeheader()

        for fila in lector_csv:
            link = fila['Img']
            imagen_base64=base_image(link)
            if verificar_colores_base64(imagen_base64, 87, 3, 3):
                # Si la imagen es válida, no hacemos cambios
                escritor_csv.writerow(fila)
                print('link sin cambios')
                
            else:
                # Si la imagen no es válida, dejamos el campo Img en blanco
                print('link sin imagen')
                fila['Img'] = ''
                escritor_csv.writerow(fila)
                print(link)

    print("Proceso completado. El archivo con los cambios se encuentra en", archivo_salida)
