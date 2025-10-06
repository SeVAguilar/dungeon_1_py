from dataclasses import dataclass, field

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
        # Metodo que genera la estructura del mapa
        pass

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

