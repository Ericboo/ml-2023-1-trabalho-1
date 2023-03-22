#TRABALHO 1 DE APRENDIZADO DE MÁQUINA 2023.1 POR ERIC JONAI COSTA SOUZA

import pandas
import numpy as np
from statistics import mode

#Abre o arquivo
df = pandas.read_excel('./dataset.xlsx').replace({np.nan:None})
#Guarda o quantitativo de linhas
df_lines = df.shape[0]
#Guarda todas as informações num dicionário
dataset = df.to_dict('records')

#Cria um novo dicionário padrão, com apenas um paciente modelo. Armazena informações de média de cada 
#   coluna numérica e tipagem de cada coluna existente. Colunas com menos de 10% das linhas preenchidas
#   não são salvas no dicionário e serão excluídas posteriormente.
def load_std_dict():
    print("carregando tipos das colunas...", end="")
    
    std_dict = {}
    #para cada coluna do arquivo
    for key in dataset[0]:
        #pega todas as linhas não nulas desta coluna
        dataset_no_null = [x for x in (d[key] for d in dataset) if x is not None]
        #se existe alguma linha não nula
        if (dataset_no_null != []):
            #se esta coluna guarda strings
            if type(mode(dataset_no_null)) == str:
                #se possui mais de 10% das linhas preenchidas
                if (float(len(dataset_no_null) / df_lines) > 0.1):
                    #guarda um "no info", apenas para modelo
                    std_dict[key] = 'no-info'
            #se esta coluna não guarda strings
            else:
                #guarda a média dos valores desta coluna
                std_dict[key] = '{0:.10f}'.format(np.mean(dataset_no_null))
    print("ok")
    return std_dict

#carrega as informações padrão para uso no decorrer da aplicação
std_dict = load_std_dict()

#lida com campos nulos
def missing_data():
    #index do paciente
    index = 0
    #paciente modelo para receber as informações faltantes
    override_patient = {}
    #guarda colunas que deverão ser excluídas
    to_pop = []
    #para cada paciente nos dados
    for patient in dataset:
        #armazena incialmente o paciente em questão no índex
        override_patient = patient
        #para cada par de coluna e valor do paciente em questão
        for key, value in patient.items():
            #Se a chave não está no paciente padrão
            if key not in std_dict.keys():
                #guarda como coluna que deverá ser excluída
                to_pop.append(key)
            #se a coluna não deve ser excluída e o valor é nulo
            elif value == None:
                #O paciente modelo deve receber o valor padrão
                override_patient[key] = std_dict[key] 
        #Guarda as informações no dataset
        dataset[index] = override_patient
        #avança o índex
        index += 1
    #para cada coluna que deve ser excluída
    for item in to_pop:
        #Itera sobre o dataset exclíndo a coluna em questão de cada dicionário
        for data in dataset:
            data.pop(item, None)
    print("ok")

#Lida com valores inconsistentes
def inconsistencies():
    #Range de palavras que são aceitas no dataset
    word_range = ['negative', 'absent','positive', 
                  'detected', 'not_detected', 'no-info', 
                  'No-info-at-all', 'yellow', 'clear', 'normal',
                  'light_yellow', 'orange', 'cloudy', 'present']
    index = 0

    #Altera todas as strings para os valores dentro do range. ignora floats
    for patient in dataset:
        patient_to_override = patient
        index += 1
        for key, value in patient.items():
            if type(std_dict[key]) == str and key != 'Patient ID':
                if value not in word_range:
                    if value == "Ausentes":
                        patient_to_override[key] = "absent"
                        dataset[index] = patient_to_override
                    elif value == "not_done" or value == "Não Realizado":
                        patient_to_override[key] = "no-info"
                        dataset[index] = patient_to_override
                    else:
                        try:
                            float(value)
                        except:
                            print(value)    
    print("ok")

#Detecta os outliers usando funções do pandas                
def detect_outliers(data):
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    IQR = q3 - q1
    outliers = data[((data<(q1-1.5*IQR)) | (data>(q3+1.5*IQR)))]
    return outliers

#Remove os outliers detectados
def remove_outliers():
    for key in dataset[0].keys():
        try:
            float(dataset[0][key])
        except:
            continue
        if (std_dict[key] != str and key != 'Patient ID'):
            data = [float(d[key]) for d in dataset]
            data_file = pandas.DataFrame(data)
            outliers = detect_outliers(data_file).dropna()
            index = 0
            for val in data:
                if (val in outliers.to_dict()):
                    dataset[index][key] = std_dict[key]
                index += 1
    print("ok")

print("Lidando com dados faltantes...", end = "")
missing_data()
print("Removendo inconsistências...", end='')
inconsistencies()

print("Removendo outliers...", end='')
remove_outliers()

new_df = pandas.DataFrame(data=dataset)

new_df.to_excel("newDataset.xlsx", index=False)