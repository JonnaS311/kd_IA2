#from ucimlrepo import fetch_ucirepo 
import pandas as pd
from nodo import Nodo
from graphviz import Digraph

clasificados = []
nodo = Nodo(None,None,None)

def identificador():
    value = 0
    while True:
        yield value
        value += 1

gen = identificador()
nodos_clase = identificador()
dot = Digraph(comment='Árbol')
falsos_positivos = []

def TreeKD(data, column,nodoAct,direccion):
    # si la instancia ya está clasificada se almacena y retorna
    if validarInstancia(data,nodoAct, direccion):
        return 0
    
    name = data.columns[column%7 + 1]
    order = data.sort_values(by=name)
    mitad = int(order.shape[0]/2)
    # Añadimos el valor del nodo junto a la columna a la que pertenece

    # valor medio entre las dos separaciones con 8 cifras significativas
    valor = round((order[name].iloc[mitad] + order[name].iloc[mitad-1])/2, 8)

    if direccion is None:
        nodoAct.value = {name : valor, 'id': next(gen)}
    else:
        nodoAct.value = {name : valor, 'id': next(gen), 'dir':direccion}

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
            TreeKD(divisiones[i],column+1,nodoAct.hijoI, True)
        elif i == 1:
            TreeKD(divisiones[i],column+1,nodoAct.hijoD, False)
           

def validarInstancia(df, nodo_Act, direccion) -> bool:
    # validamos si en ese grupo hay una única instancia y a que clase pertenece
    if df['class'].nunique() == 1 and df['class'].iloc[0] == 'Osmancik':
        # añadir clase 'Osmancik' al nodo actual 
        nodo_Act.value = {'class': 'Osmancik', 'id': next(gen), 'dir':direccion}
        clasificados.append(df)
        return True
    elif  df['class'].nunique() == 1 and df['class'].iloc[0] == 'Cammeo': 
         # añadir clase 'Cammeo' al nodo actual 
        nodo_Act.value = {'class': 'Cammeo', 'id': next(gen), 'dir':direccion}
        clasificados.append(df)
        return True
    else:
        return False
    
def graficar(node,parentNode,isGraficable):
    '''
    ejemplo de como añadir un nodo
    dot.node('A', 'Raíz')
    dot.node('B', 'Nodo B')
    dot.node('C', 'Nodo C')
    dot.node('D', 'Nodo D')

    ejemplo de aristas
    dot.edges([('A', 'B'), ('A', 'C'), ('B', 'D')])
    '''
    llave = list(node.value.keys())
    if llave[0] == 'class':
        dot.node(str(node.value['id']),f'{llave[0]} = {node.value[llave[0]]}')
        next(nodos_clase)
    else:
        dot.node(str(node.value['id']),f'{llave[0]} < {node.value[llave[0]]}')

    if parentNode != None:
        dot.edges([ (str(parentNode.value['id']), str(node.value['id'])) ])

    try:
        graficar(node.hijoI, node, False)
    except:
        pass
    try:
        graficar(node.hijoD, node, False)
    except:
        pass

    if isGraficable:
        # Añadir un label para la convención en la esquina inferior derecha
        dot.attr(label='Convenciones: \nIzquierda = True\nDerecha = False', 
         labelloc='t',  # 't' para parte superior, 'b' para inferior
         labeljust='l', # 'l' para alinear a la izquierda, 'r' para la derecha
         fontsize='15')
        # Guardar el gráfico en formato PNG
        dot.format = 'svg'  # Especificar el formato PNG
        dot.render('arbol_grafico', view=True)  # Guarda el archivo como 'arbol_grafico.png' y lo muestra

def encontrar_caminos(raiz):
    # Lista que almacenará todos los caminos desde la raíz hasta las hojas
    caminos = []

    # Función auxiliar para recorrer el árbol y encontrar los caminos
    def dfs(nodo, camino_actual):
        # Agregamos el nodo actual al camino
        camino_actual.append(nodo.value)
        
        # Si el nodo no tiene hijos, es una hoja, añadimos el camino a la lista de caminos
        if not hasattr(nodo, 'hijoD') and not hasattr(nodo, 'hijoI'):
            caminos.append(list(camino_actual))  # Hacemos una copia del camino actual
        else:
            # Si tiene hijos, seguimos recorriendo los hijos
            if nodo.hijoD is not None:
                dfs(nodo.hijoI, camino_actual)
                pass
            if nodo.hijoI is not None:
                dfs(nodo.hijoD, camino_actual)
                pass
        
        # Al terminar de explorar este nodo, lo eliminamos del camino actual (backtracking)
        camino_actual.pop()

    # Iniciamos la búsqueda desde la raíz
    dfs(raiz, [])
    
    return caminos

def crearReglasTxt(reglas, data):
    # Crear y escribir en un archivo
    with open("reglas.txt", "w") as archivo:
        for regla in reglas:
            siguiente = regla[-1]['dir']
            archivo.write("\n SI: \n")
            for condicion in reversed(regla):
                if list(condicion.keys())[0] != 'class':
                    if siguiente:
                        archivo.write("\t"+list(condicion.keys())[0]+" < ")
                    else:
                        archivo.write("\t"+list(condicion.keys())[0]+" > ")
                    archivo.write(str( condicion[list(condicion.keys())[0]] )+"\n")
                    try:
                        siguiente = condicion['dir']
                    except:
                        pass
            archivo.write("ENTONCES: \n")
            archivo.write("\tclase: ")
            archivo.write(regla[-1]['class']+"\n")
            archivo.write("\n")

        # Prueba de reescritura
        archivo.write("\n")
        archivo.write("-------------- RESULTADO PRUEBA DE REESCRITURA --------------\n")
        archivo.write("\tAccuracy: "+str(iterar(nodo,data))+"\n")

        archivo.write("\tInformacion de los elementos mal clasificados: \n \t"+
                      str(falsos_positivos).replace(" ","").replace("\n"," | ").replace(",","\n \t"))

def iterar(nodo,df):
    def reescritura(raiz, df):
        if list(raiz.value.keys())[0] == 'class':
            if (raiz.value['class'] != df['class']):
                print(raiz.value['class'] + ":" + df['class'])
                falsos_positivos.append(df)
                return 0
                
        
        if df[list(raiz.value.keys())[0]] <= raiz.value[list(raiz.value.keys())[0]]:
            try:
                reescritura(raiz.hijoI, df)
            except:
                pass
        else:
            try:
                reescritura(raiz.hijoD, df)
            except:
                pass
    for index, row in df.iterrows():
        reescritura(nodo,row)
    print(falsos_positivos)
    return 1 - len(falsos_positivos)/len(df)

def main():
    '''
    https://archive.ics.uci.edu/dataset/545/rice+cammeo+and+osmancik
    Link del set de Datos
    '''
    data = pd.read_csv('./datos.csv')
    TreeKD(data,0,nodo,None)
    graficar(nodo, None, True)
    #print(f'cantidad de nodos clase: {next(nodos_clase)}')
    reglas = encontrar_caminos(nodo)
    crearReglasTxt(reglas, data)
    

if __name__ == '__main__':
    main()