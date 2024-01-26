import pandas as pd
import openpyxl,json,os

def extract_information(input_excel_file, sheet_names):
    try:
        xls = pd.ExcelFile(input_excel_file)
        data = {}

        for sheet_name in sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=1)

            df.dropna(axis=0, how='all', inplace=True)
            df.dropna(axis=1, how='all', inplace=True)

            sheet_data = []
            for _, row in df.iterrows():
                row_dict = {col: row[col] for col in df.columns if pd.notna(row[col])}
                sheet_data.append(row_dict)

            data[sheet_name] = sheet_data

        return data
    
    except Exception as e:
        print(f"Se produjo un error al procesar el archivo Excel: {str(e)}")

def extract_items(input_excel_file, sheet_names):
    try:
        xls = pd.ExcelFile(input_excel_file)
        data = {}

        for sheet_name in sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=1)

            df.dropna(axis=0, how='all', inplace=True)
            df.dropna(axis=1, how='all', inplace=True)

            sheet_data = []
            for _, row in df.iterrows():
                row_dict = {col: row[col].strftime('%Y-%m-%d %H:%M:%S') if isinstance(row[col], pd.Timestamp) else row[col] for col in df.columns if pd.notna(row[col])}
                sheet_data.append(row_dict)

            data[sheet_name] = sheet_data
        # print(json.dumps(data,indent=4))
        return data

    except Exception as e:
        print(f"Se produjo un error al procesar el archivo Excel: {str(e)}")
        return None
    
def save_json(data, output_json_file):
    try:
        with open(output_json_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, default=str, indent=4)

    except Exception as e:
        print(f"Se produjo un error al guardar el diccionario como JSON: {str(e)}")

def get_excelfiles(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), directory)
            file_list.append(relative_path.replace('\\', '/'))
    return file_list

def extract_searches(dict_list, key_list):
    result = {}

    for key_dict in key_list:
        for friendly_key, real_key in key_dict.items():
            unique_values = set()

            for dictionary in dict_list:
                if real_key in dictionary:
                    unique_values.add(dictionary[real_key])

            result[friendly_key] = list(unique_values)

    return result

def load_json(file_name):
    try:
        with open(file_name, 'r',encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return None

def save_items():
    directory = r'excel_files'
    items_json = "items_cleaned.json"
    sheets_to_import = ["Entities"]
    existing_data = load_json(items_json)

    all_data = existing_data
    print(f"Datos iniciales: {len(all_data['Entities'])}")

    excel_files = get_excelfiles(directory)

    for file in excel_files:
        data = extract_items(os.path.join(directory, file), sheets_to_import)
        if data:
            # Fusionar las listas en lugar de actualizar el diccionario
            all_data["Entities"].extend(data["Entities"])
    
    print(f"Datos después de importar: {len(all_data['Entities'])}")
    
    unique_data = []
    unique_gtins = set()

    for element in all_data["Entities"]:
        gtin = element.get('GTIN BMSid 67')
        if gtin and gtin not in unique_gtins:
            unique_gtins.add(gtin)
            unique_data.append(element)
    
    all_data["Entities"] = unique_data  # Actualizar con los elementos únicos
    print(f"Datos únicos: {len(all_data['Entities'])}")
    save_json(all_data, items_json)
    
    return all_data

def save_searches(all_data):
    keys_search="key_search.json"
    
    keys=[{"nombre_generico":"Name"},{"marca":"Brand Name BMSid 3541"},{"publicador":"Information provider party name BMSid 85"}]
    
    search_terms=extract_searches(all_data["Entities"],keys)
    save_json(search_terms,keys_search)
    
    
def main():
    
    all_data=save_items()
    save_searches(all_data)
    print(len(all_data['Entities']))

    
if __name__=="__main__":
    
    main()

    


