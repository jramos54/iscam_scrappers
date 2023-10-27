import requests
import PyPDF2
import tabula
import camelot
import json
import funciones
import datetime

def get_pdf_file():
    url='https://www.dunosusa.com.mx/ubicaciones.pdf'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

    response=requests.get(url,headers=headers)

    print(response.status_code)
    with open('archivo.pdf', 'wb') as file:
        file.write(response.content)

# Extraer el texto del PDF
# total_lines=[]
# with open('archivo.pdf', 'rb') as pdf_file:
#     pdf_reader = PyPDF2.PdfReader(pdf_file)

#     for page_num in range(len(pdf_reader.pages)):
#         page = pdf_reader.pages[page_num]
#         page_text = page.extract_text()
#         page_lines=page_text.splitlines()
#         total_lines.extend(page_lines)

# # Limpiar PDF de primer y 4ta columna
# total_lines=total_lines[2:-1]
# clean_lines=[]
# for line in total_lines:
#     words=line.split()
#     if words[0].isnumeric():
#         words.pop(0)
#     elif words[-1].startswith('https'):
#         words.pop()
#     new_line=' '.join(words)
#     clean_lines.append(new_line)

# # Separar sucursal de direccion. 


# for i,line in enumerate(clean_lines):
#     print(f'{i} - {line}')


if __name__=='__main__':
    get_pdf_file()
    file='archivo.pdf'
    INFORMANTE='Dunosusa'
    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    tables = camelot.read_pdf(file,pages='1-end')

    list_sucursales=[]
    for table in tables:
        for _,fila in table.df.iterrows():
            sucursal_lines=fila[1].splitlines()
            sucursal=' '.join(sucursal_lines)
            direccion_lines=fila[2].splitlines()
            direccion=' '.join(direccion_lines)

            longitud,latitud = funciones.geolocalizacion(direccion)

            tienda={
                'Informante':INFORMANTE,
                'Sucursal': sucursal,
                'Direccion': direccion,
                'CP':funciones.obtencion_cp(direccion),
                'Latitud':latitud,
                'Longitud':longitud,
                'Telefono':'',
                'Email':'',
                'fecha':stamped_today
                }

            list_sucursales.append(tienda)

    for i,sucursal in enumerate(list_sucursales):
        print('-'*15,f'\t\t{i}\t\t','-'*15)
        print(json.dumps(sucursal,indent=4))
        
    filename='dunosusa_tiendas_'+stamped_today+'.csv'
    funciones.exportar_csv(list_sucursales,filename)