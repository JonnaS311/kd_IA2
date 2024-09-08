from ucimlrepo import fetch_ucirepo 
import pandas as pd

clasificados = []

def algo(data, column):
    # si la instancia ya está clasificada se almacena y retorna
    if validarInstancia(data):
        return 0
    
    order = data.sort_values(by=data.columns[column%7])
    mitad = int(order.shape[0]/2)

    # separamos el dataFrame en dos mitades 
    divisiones = []
    divisiones.append(order.iloc[:mitad])  # Primeras filas
    divisiones.append(order.iloc[mitad:])  # Segundas filas

    # validamos si cada mitad tiene una única instancia
    for i in range(len(divisiones)):
        if validarInstancia(divisiones[i]) == False:
            algo(divisiones[i],column+1)
    pass

def validarInstancia(df) -> bool:
    if df['class'].nunique() == 1 and df['class'].iloc[0] == 'Osmancik':
        clasificados.append(df)
        return True
    elif  df['class'].nunique() == 1 and df['class'].iloc[0] == 'Cammeo': 
        clasificados.append(df)
        return True
    else:
        print('no tiene elementos iguales')
        return False

def main():
    '''
    https://archive.ics.uci.edu/dataset/545/rice+cammeo+and+osmancik
    Link del set de Datos
    '''
    data = pd.read_csv('./datos.csv')
    data = data.iloc[:1631]
    algo(data,0)
    print(clasificados)
    print(len(clasificados))


if __name__ == '__main__':
    main()