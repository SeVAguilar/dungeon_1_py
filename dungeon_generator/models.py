from __future__ import annotations #Para referencias futuras
from dataclasses import dataclass

@dataclass
class Habitacion:
    id: int   #Identificador unico de la habitacion
    x: int    #coordenadas en el mapa 2D
    y: int
    inicial: bool   #Indica si es la habitacion de inicio
    contenido: ContenidoHabitacion | None #Vacia, tesoro, monstruo o jefe
    conexiones: dict[str, "Habitacion"] 
    visitada: bool   #Indica si fue visitada
@dataclass
class Mapa:
    ancho: int 
    alto: int  #dimensiones del mapa
    habitaciones: dict[tuple[int, int], Habitacion] 
    # diccionario de habitaciones indexado por 
    # coordenadas (x, y)
    habitacion_inicial: Habitacion 
    #referencia a la habitación de inicio
@dataclass
class Objeto:
    nombre: str # nombre del objeto
    valor: int  # valor del objeto
    descripcion: str # descripción del objeto
@dataclass
class Explorador:
    vida: int # puntos de vida del explorador (por defecto 5)
    inventario: list[Objeto] # lista de objetos recolectados
    posicion_actual: tuple[int, int] # coordenadas actuales en el mapa
    mapa: Mapa # referencia al mapa que está explorando
@dataclass
class ContenidoHabitacion:
    pass
@dataclass
class Tesoro(ContenidoHabitacion):
    recompensa: Objeto
@dataclass
class Monstruo(ContenidoHabitacion):
    nombre:str 
    vida: float
    ataque: int

@dataclass
class Jefe(Monstruo):
    recompensa_especial: Objeto

