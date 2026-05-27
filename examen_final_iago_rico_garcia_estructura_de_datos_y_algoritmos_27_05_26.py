

from collections import deque
import heapq
import json
import matplotlib.pyplot as plt
import networkx as nx

# =====================================================================
# CLASE PARA LA LÓGICA DEL GRAFO Y ALGORITMOS
# =====================================================================
class GrafoRutas:
    def __init__(self):
        # Implementación mediante Lista de Adyacencia usando Diccionarios
        self.adyacencias = {}

    def cargar_desde_archivo(self, ruta_archivo):
        """Persistencia (Lectura): Carga los datos del grafo desde cualquier archivo JSON."""
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                self.adyacencias = json.load(f)
            print(f"[OK] Red cargada correctamente desde '{ruta_archivo}'.")
            return True
        except FileNotFoundError:
            print(f"[INFO] El archivo '{ruta_archivo}' no existe aún. Se iniciará un grafo vacío.")
            return False
        except Exception as e:
            print(f"[ERROR] Ocurrió un problema al leer el archivo: {e}")
            return False

    def guardar_en_archivo(self, ruta_archivo):
        """Persistencia (Escritura): Guarda el estado actual del grafo en un archivo JSON."""
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(self.adyacencias, f, indent=4)
            print(f"[OK] Datos guardados permanentemente en '{ruta_archivo}'.")
        except Exception as e:
            print(f"[ERROR] Ocurrió un problema al guardar los datos: {e}")

    def agregar_nodo(self, nodo):
        """Añade un nuevo vértice al grafo."""
        if nodo not in self.adyacencias:
            self.adyacencias[nodo] = {}
            print(f"[OK] Nodo '{nodo}' agregado con éxito.")
        else:
            print(f"[INFO] El nodo '{nodo}' ya existe en el sistema.")

    def agregar_arista(self, origen, destino, peso):
        """Añade una arista ponderada no dirigida entre dos nodos."""
        try:
            peso = float(peso)
            if origen not in self.adyacencias:
                self.agregar_nodo(origen)
            if destino not in self.adyacencias:
                self.agregar_nodo(destino)
            
            # Grafo no dirigido: conexión bidireccional
            self.adyacencias[origen][destino] = peso
            self.adyacencias[destino][origen] = peso
            print(f"[OK] Ruta agregada: {origen} <-> {destino} (Peso: {peso})")
            
        except ValueError:
            print("[ERROR] El peso de la ruta debe ser un valor numérico válido.")

    def dijkstra(self, origen, destino):
        """Algoritmo de Dijkstra para encontrar el camino más corto."""
        if origen not in self.adyacencias or destino not in self.adyacencias:
            print("[ERROR] El origen o el destino especificados no existen en el grafo.")
            return None, float('inf')

        distancias = {nodo: float('inf') for nodo in self.adyacencias}
        distancias[origen] = 0
        padres = {nodo: None for nodo in self.adyacencias}
        
        # Min-Heap para la cola de prioridad (distancia, nodo)
        cola_prioridad = [(0, origen)]
        visitados = set()

        while cola_prioridad:
            distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)

            if nodo_actual in visitados:
                continue
            visitados.add(nodo_actual)

            if nodo_actual == destino:
                break

            for vecino, peso_arista in self.adyacencias[nodo_actual].items():
                distancia_nueva = distancia_actual + peso_arista
                if distancia_nueva < distancias[vecino]:
                    distancias[vecino] = distancia_nueva
                    padres[vecino] = nodo_actual
                    heapq.heappush(cola_prioridad, (distancia_nueva, vecino))

        camino = []
        nodo_paso = destino
        while nodo_paso is not None:
            camino.append(nodo_paso)
            nodo_paso = padres[nodo_paso]
        camino.reverse()

        if distancias[destino] == float('inf'):
            print(f"[INFO] No existe un camino posible entre {origen} y {destino}.")
            return [], float('inf')

        return camino, distancias[destino]

    def estan_conectados_bfs(self, origen, destino):
        """Algoritmo BFS para verificar si existe al menos un camino entre dos nodos."""
        if origen not in self.adyacencias or destino not in self.adyacencias:
            print("[ERROR] Uno o ambos nodos no existen en la red.")
            return False
            
        if origen == destino:
            return True

        # Cola FIFO (collections.deque) y conjunto de visitados
        cola = deque([origen])
        visitados = set([origen])

        while cola:
            nodo_actual = cola.popleft()

            if nodo_actual == destino:
                return True

            for vecino in self.adyacencias[nodo_actual].keys():
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(vecino)

        return False

    def mostrar_distribucion_red(self):
        """Genera una representación visual del grafo usando NetworkX y Matplotlib."""
        if not self.adyacencias:
            print("[INFO] El grafo está vacío. No hay nada que dibujar.")
            return

        G = nx.Graph()
        for origen, conexiones in self.adyacencias.items():
            for destino, peso in conexiones.items():
                G.add_edge(origen, destino, weight=peso)

        pos = nx.spring_layout(G, seed=42) 
        plt.figure(figsize=(8, 6))
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2500, 
                edge_color='gray', font_size=10, font_weight='bold')

        etiquetas_aristas = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=etiquetas_aristas, font_color='red')

        plt.title("Distribución de la Red de Rutas", fontsize=14, fontweight='bold')
        plt.show()


# =====================================================================
# CLASE PARA LA INTERFAZ DE USUARIO (MENÚ INTERACTIVO)
# =====================================================================
class MenuInteractivo:
    def __init__(self):
        self.grafo = GrafoRutas()
        self.archivo_datos = "sistema_rutas.json"  # Archivo por defecto

    def cargar_red_personalizada(self):
        """NUEVA FUNCIÓN: Permite al usuario escribir el nombre de cualquier archivo para cargarlo."""
        print("\n--- Cargar Archivo de Red Personalizado ---")
        nombre_archivo = input("Ingrese el nombre o ruta del archivo (.json): ").strip()
        
        if not nombre_archivo:
            print("[ERROR] El nombre del archivo no puede estar vacío.")
            return
            
        # Intentamos cargar el archivo solicitado
        exito = self.grafo.cargar_desde_archivo(nombre_archivo)
        if exito:
            # Si se cargó bien, actualizamos la variable para que los futuros guardados vayan a este archivo
            self.archivo_datos = nombre_archivo
            print(f"[INFO] Archivo de trabajo actual cambiado a: '{self.archivo_datos}'")

    def iniciar(self):
        print("Iniciando Sistema de Optimización de Rutas...")
        # Carga automática inicial del archivo por defecto
        self.grafo.cargar_desde_archivo(self.archivo_datos)
        
        while True:
            print("\n" + "="*30)
            print("         MENÚ PRINCIPAL")
            print("="*30)
            print("1. Agregar una nueva ubicación (Nodo)")
            print("2. Agregar una nueva ruta (Arista y Peso)")
            print("3. Calcular ruta más corta (Dijkstra)")
            print("4. Verificar conexión entre dos ubicaciones (BFS)")
            print("5. Mostrar todas las conexiones actuales (Texto)")
            print("6. Visualizar distribución de la red (Gráfico 2D)")
            print("7. Cargar una red desde un archivo cualquiera (.json) ")
            print("8. Guardar datos y Salir")
            print("="*30)
            
            opcion = input("Seleccione una opción (1-8): ").strip()
            
            try:
                if opcion == '1':
                    nodo = input("Ingrese el nombre de la ubicación: ").strip().upper()
                    if nodo:
                        self.grafo.agregar_nodo(nodo)
                    else:
                        print("[ERROR] El nombre no puede estar vacío.")
                        
                elif opcion == '2':
                    origen = input("Ingrese la ubicación de origen: ").strip().upper()
                    destino = input("Ingrese la ubicación de destino: ").strip().upper()
                    peso = input("Ingrese la distancia o coste: ").strip()
                    if origen and destino:
                         self.grafo.agregar_arista(origen, destino, peso)
                    else:
                         print("[ERROR] Los nombres no pueden estar vacíos.")
                    
                elif opcion == '3':
                    origen = input("Ingrese el punto de partida: ").strip().upper()
                    destino = input("Ingrese el destino final: ").strip().upper()
                    camino, coste = self.grafo.dijkstra(origen, destino)
                    if camino:
                        print("\n" + "-"*30)
                        print("🚀 RUTA ÓPTIMA ENCONTRADA")
                        print(f"Camino: {' -> '.join(camino)}")
                        print(f"Coste total: {coste}")
                        print("-"*30)
                        
                elif opcion == '4':
                    origen = input("Ingrese la ubicación de origen: ").strip().upper()
                    destino = input("Ingrese la ubicación de destino a verificar: ").strip().upper()
                    if origen and destino:
                        conectados = self.grafo.estan_conectados_bfs(origen, destino)
                        if conectados:
                            print(f"\n[✔️] SÍ, existe conexión entre {origen} y {destino}.")
                        else:
                            print(f"\n[❌] NO existe ningún camino entre {origen} y {destino}.")
                    else:
                        print("[ERROR] Los nombres no pueden estar vacíos.")
                        
                elif opcion == '5':
                    print("\n--- Estado Actual de la Red ---")
                    if not self.grafo.adyacencias:
                        print("El grafo está vacío.")
                    for nodo, conexiones in self.grafo.adyacencias.items():
                        print(f"{nodo} se conecta con: {conexiones}")

                elif opcion == '6':
                    print("\n[INFO] Abriendo ventana de visualización...")
                    self.grafo.mostrar_distribucion_red()  

                elif opcion == '7':
                    # Llamamos a nuestra nueva función dinámica
                    self.cargar_red_personalizada()

                elif opcion == '8':
                    self.grafo.guardar_en_archivo(self.archivo_datos)
                    print(f"\nSaliendo del sistema. Datos guardados en '{self.archivo_datos}'. ¡Hasta pronto!")
                    break
                    
                else:
                    print("[ERROR] Opción no válida. Ingrese un número del 1 al 8.")
                    
            except KeyboardInterrupt:
                print("\n[INFO] Ejecución interrumpida. Guardando datos por seguridad...")
                self.grafo.guardar_en_archivo(self.archivo_datos)
                break
            except Exception as e:
                print(f"\n[ERROR INESPERADO]: {e}")

# =====================================================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# =====================================================================
if __name__ == "__main__":
    app = MenuInteractivo()
    app.iniciar()