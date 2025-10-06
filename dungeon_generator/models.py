from dataclasses import dataclass, field
import random 

@dataclass
class Habitacion:
    """
    Representa una habitación en el dungeon.

    Attributes:
        id: Identificador unico de la habitación
        x, y: Coordenadas en el mapa 2D
        inicial: Indica si es la habitación de inicio
        contenido: Contenido de la habitacion (tesoro, monstruo, etc)
        conexiones: Diccionario de conexiones con otras habitaciones
        visitada: Indica si fue visitada por el explorador
    """
    id: int   
    x: int   
    y: int    
    inicial: bool = False    
    contenido: "ContenidoHabitacion | None" = None 
    conexiones: dict[str, "Habitacion"] = field(default_factory=dict)
    visitada: bool = False 


@dataclass
class Mapa:
    """
    Representa el mapa completo del dungeon con sus habitaciones.

    Attributes:
        ancho, alto: Dimensiones del mapa en celdas
        habitaciones: Diccionario de habitaciones indexadas 
                      por coordenadas (x,y)
        habitacion_inicial: Referencia a la habitacion donde inicia el explorador
    """
    ancho: int 
    alto: int  
    habitaciones: dict[tuple[int, int], Habitacion] = field(default_factory=dict)
    habitacion_inicial: Habitacion | None = None

    def generar_estructura(self, n_habitaciones: int):
        # Metodo que genera la estructura del mapa con conexiones aleatorias
        max_habitaciones = self.ancho * self.alto
        
        
        if n_habitaciones > max_habitaciones:
            raise ValueError(
                f"No se pueden crear {n_habitaciones} habitaciones en un mapa de {self.ancho}x{self.alto}"
            )
        if n_habitaciones < 1:
            raise ValueError("Debe haber al menos 1 habitacion")
        
        # Limpiar habitaciones
        self.habitaciones.clear()
        self.habitacion_inicial = None

        # Generar posiciones aleatorias
        todas_posiciones = [(x, y) for x in range(self.ancho) for y in range(self.alto)]
        posiciones_habitaciones = random.sample(todas_posiciones, n_habitaciones)

        # Elegir habitacion inicial en el borde
        posiciones_borde = [
            pos for pos in posiciones_habitaciones
            if pos[0] == 0 or pos[0] == self.ancho-1 
            or pos[1] == 0 or pos[1] == self.alto-1
        ]

        if posiciones_borde:
            pos_inicial = random.choice(posiciones_borde)
        else:
            pos_inicial = posiciones_habitaciones[0]

        # Crear las habitaciones
        for i, (x, y) in enumerate(posiciones_habitaciones):
            es_inicial = (x, y) == pos_inicial
            habitacion = Habitacion(
                id=i,
                x=x,
                y=y,
                inicial=es_inicial
            )
            self.habitaciones[(x, y)] = habitacion

            if es_inicial:
                self.habitacion_inicial = habitacion

        # Conectar habitaciones adyacentes
        direcciones = {
            'norte': (0, -1),
            'sur': (0, 1),
            'este': (1, 0),
            'oeste': (-1, 0)
        }

        for (x, y), habitacion in self.habitaciones.items():
            for direccion, (dx, dy) in direcciones.items():
                vecino_pos = (x + dx, y + dy)
                if vecino_pos in self.habitaciones:
                    habitacion.conexiones[direccion] = self.habitaciones[vecino_pos]
        
        if self.habitacion_inicial is None:
            raise Exception("No se pudo establecer la habitación inicial")

        visitadas = set()
        cola = [self.habitacion_inicial]

        while cola:
            habitacion_actual = cola.pop(0)
            pos_actual = (habitacion_actual.x, habitacion_actual.y)

            if pos_actual not in visitadas:
                visitadas.add(pos_actual)

                # Agregar vecinos a la cola
                for vecino in habitacion_actual.conexiones.values():
                    pos_vecino = (vecino.x, vecino.y)
                    if pos_vecino not in visitadas:
                        cola.append(vecino)

        # Verifica que todas las habitaciones son accesibles
        if len(visitadas) != n_habitaciones:
            raise Exception(f"Solo {len(visitadas)} de {n_habitaciones} habitaciones son accesibles desde la habitacion inicial.")


    def colocar_contenido(self):
        # Metodo que coloca el contenido de manera aleatoria en las habitaciones
        pass


@dataclass
class Objeto:
    """
    Representa un objeto que puede ser recolectado por el explorador.

    Attributes:
        nombre: Nombre descriptivo del objeto
        valor: Valor numérico del objeto
        descripcion: Descripción textual del objeto
    """
    nombre: str # Nombre del objeto
    valor: int  # Valor del objeto
    descripcion: str # Descripción del objeto


@dataclass
class Explorador:
    """
    Representa al explorador que navega por el dungeon.

    Attributes:
        mapa: Referencia al mapa que esta explorando
        posicion_actual: Coordenadas actuales en el mapa
        vida: Puntos de vida del explorador (por defecto 5)
        inventario: Lista de objetos recolectados
    """
    mapa: Mapa # Referencia al mapa que está explorando
    posicion_actual: tuple[int, int] # Coordenadas actuales en el mapa

    vida: int = 5 # Puntos de vida del explorador (por defecto 5)
    inventario: list[Objeto] = field(default_factory=list) # Lista de objetos recolectados

  
    def mover(self, direccion: str) -> bool:
        # Metodo para moverse entre habitaciones conectadas, retorna True si el 
        # movimiento fue exitoso y actualiza la posicion_actual
        
        # Obtener posicion actual
        habitacion_actual = self.mapa.habitaciones.get(self.posicion_actual)

        if habitacion_actual is None:
            return False # No hay habitacion en la pocision actual
        
        # verificar si la direccion existe en las conexiones
        if direccion not in habitacion_actual.conexiones:
            return False # No hay conexiones en esa direccion     
        
        # Obtener la habitacion destino
        habitacion_destino = habitacion_actual.conexiones[direccion]

        # Actualizar la posicion actual
        self.posicion_actual = (habitacion_destino.x, habitacion_destino.y)

        return True # Movimiento realizado


    def explorar_habitacion(self) -> str:     
        # Interactuar con el contenido de la habitación actual y marcarla 
        # como visitada
        pass

    
    def obtener_habitaciones_adyacentes(self) -> list[str]:
        # Metodo para listar direcciones disponibles desde la posición actual
        habitacion_actual = self.mapa.habitaciones.get(self.posicion_actual)

        if habitacion_actual is None:
            return [] # En la posicion actual no hay habitacion
        
        # Retorna las claves del diccionario de "conexiones"
        return list(habitacion_actual.conexiones.keys())
    
    
    def recibir_dano(self, cantidad: int):
        # Metodo para reducir la vida del explorador
        self.vida -= cantidad
        if self.vida < 0:
            self.vida = 0 # Evita que la vida sea negativa

    @property
    def esta_vivo(self) -> bool:
        # Metodo para verificar si el explorador tiene vida restante
        return self.vida > 0
    
@dataclass
class ContenidoHabitacion:
    """
    Clase base abstracta para todos los contenidos de la habitación.
    """
    
    @property
    def descripcion(self) -> str:
        # Metodo que describe la habitacion
        return "Contenido generico"

    @property
    def tipo(self) -> str:
        # Metodo que indica el tipo de contenido de la habitacion
        return "Generico"

    def interactuar(self) -> str:
        # Metodo para interactuar con elementos de la habitacion
        return "No pasa nada :3"

@dataclass
class Tesoro(ContenidoHabitacion):
    """
    Representa un tesoro que puede ser recolectado.

    Attributes:
        recompensa: Objeto que se obtiene al recoger el tesoro
    """
    recompensa: Objeto
@dataclass
class Monstruo(ContenidoHabitacion):
    """
    Representa un monstruo que se puede combatir con el explorador.

    Attributes:
        nombre: Nombre del monstruo
        vida: Puntos de vida del monstruo
        ataque: Poder de ataque del monstruo    
    """
    nombre: str 
    vida: int
    ataque: int

@dataclass
class Jefe(Monstruo):
    """
    Representa un jefe final, mas fuerte que un monstruo normal.

    Inherits from:
        Monstruo: Caracteristicas basicas de combate

    Attributes:
        recompensa_especial: Objeto especial que otorga al ser derrotado
    """
    recompensa_especial: Objeto

