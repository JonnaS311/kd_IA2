from ucimlrepo import fetch_ucirepo 
import pandas as pd
from nodo import Nodo

clasificados = []
nodo = Nodo(None,None,None)

def TreeKD(data, column,nodoAct):
    # si la instancia ya está clasificada se almacena y retorna
    if validarInstancia(data,nodoAct):
        return 0
    
    name = data.columns[column%7 + 1]
    order = data.sort_values(by=name)
    mitad = int(order.shape[0]/2)
    # Añadimos el valor del nodo junto a la columna a la que pertenece
    nodoAct.value = {name : order[name].iloc[mitad]} 
    
    # Creamos los nodos hijos
    nodoAct.hijoD = Nodo(None,None,None)
    nodoAct.hijoI = Nodo(None,None,None)

    # separamos el dataFrame en dos mitades 
    divisiones = []
    divisiones.append(order.iloc[:mitad])  # Primeras filas
    divisiones.append(order.iloc[mitad:])  # Segundas filas

    # Entramos en recursividad
    for i in range(len(divisiones)):
        if i == 0:
            TreeKD(divisiones[i],column+1,nodoAct.hijoI)
        elif i == 1:
            TreeKD(divisiones[i],column+1,nodoAct.hijoD)
           
    pass

def validarInstancia(df, nodo_Act) -> bool:
    # validamos si en ese grupo hay una única instancia y a que clase pertenece
    if df['class'].nunique() == 1 and df['class'].iloc[0] == 'Osmancik':
        # añadir clase 'Osmancik' al nodo actual 
        nodo_Act.value = {'class': 'Osmancik'}
        clasificados.append(df)
        return True
    elif  df['class'].nunique() == 1 and df['class'].iloc[0] == 'Cammeo': 
         # añadir clase 'Cammeo' al nodo actual 
        nodo_Act.value = {'class': 'Cammeo'}
        clasificados.append(df)
        return True
    else:
        return False

def main():
    '''
    https://archive.ics.uci.edu/dataset/545/rice+cammeo+and+osmancik
    Link del set de Datos
    '''
    data = pd.read_csv('./datos.csv')
    data = data.iloc[:1632]
    TreeKD(data,0,nodo)
    print(len(clasificados))

if __name__ == '__main__':
    main()