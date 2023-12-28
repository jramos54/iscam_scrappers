from sqlalchemy import create_engine, MetaData, Table, Column, String, Date, UniqueConstraint, Text
from sqlalchemy.dialects.mysql import insert
from dotenv import load_dotenv
import os, csv

load_dotenv()

def make_conexion():
    USER_NAME = os.getenv("USER_NAME")
    PASSWORD = os.getenv("PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    engine = create_engine(f'mysql://{USER_NAME}:{PASSWORD}@localhost/{DB_NAME}')
    return engine

def create_table(engine):
    TABLE_NAME=os.getenv("TABLE_NAME")
    metadata = MetaData()

    tabla = Table(
        f'{TABLE_NAME}',
        metadata,
        Column('Informante', String(255)),
        Column('Categoria', String(255)),
        Column('DescripcionCorta', String(255)),
        Column('Referencia',String(255)),
        Column('Precio', String(255)),
        Column('Promocion', String(255)),
        Column('DescripcionLarga', Text),
        Column('Tamaño', String(50)),
        Column('Img', String(255)),
        Column('Fecha', Date),
        UniqueConstraint('Referencia', name='uix_1')
    )

    metadata.create_all(engine)
    return tabla

def insert_data(engine,tabla, datos):
    with engine.begin() as connection:
        insert_values = insert(tabla).values(**datos)
        on_duplicate_key = insert_values.on_duplicate_key_update(
            Categoria=insert_values.inserted.Categoria,
            DescripcionCorta=insert_values.inserted.DescripcionCorta,
            Precio=insert_values.inserted.Precio,
            Promocion=insert_values.inserted.Promocion,
            DescripcionLarga=insert_values.inserted.DescripcionLarga,
            Tamaño=insert_values.inserted.Tamaño,
            Img=insert_values.inserted.Img,
            Fecha=insert_values.inserted.Fecha
        )
        
        connection.execute(on_duplicate_key)

def read_csv(csv_file):
    data_list = []
    with open(csv_file, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter='|')  
        for row in csvreader:
            data_list.append(row)
    return data_list

def main():
    engine = make_conexion()
    tabla=create_table(engine)
    
    datos=read_csv('productos_circuloK_2023-11-28.csv')        
    
    for dato in datos:
        insert_data(engine, tabla,dato)

if __name__ == "__main__":
    main()


    """
    datos = [
        {
        'Informante': '7-eleven',
        'Categoria': 'Comida',
        'SubCategoria': 'Instantaneo',
        'Marca': 'La Sierra',
        'DescripcionCorta': 'La Sierra Frijol Negro Refrito Bols 516 G',
        'Precio': '$60.00',
        'Tamaño': '516 G',
        'Img': 'https://oneiconn.vtexassets.com/arquivos/ids/186356-300-300?v=638194382274030000&width=300&height=300&aspect=true',
        'Fecha': '2023-11-30'
        },
        {
        'Informante': '7-eleven',
        'Categoria': 'Abarrotes',
        'SubCategoria': 'Instantaneo',
        'Marca': 'Ranch Style',
        'DescripcionCorta': 'Ranch Style Frijol 425Gr',
        'Precio': '$12.00',
        'Tamaño': '425Gr',
        'Img': 'https://oneiconn.vtexassets.com/arquivos/ids/186401-300-300?v=638194382456500000&width=300&height=300&aspect=true',
        'Fecha': '2023-11-30'
        }
        ]

    """