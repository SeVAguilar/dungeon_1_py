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
        # Valida que el numero de habitaciones tenga sentido con el tamaño del mapa
        
        max_habitaciones = self.ancho * self.alto
        
        # Verifica que no haya mas habitaciones que celdas disponibles
        if n_habitaciones > max_habitaciones:
            raise ValueError(
                f"No se pueden crear {n_habitaciones} habitaciones en un mapa de {self.ancho}x{self.alto}"
            )
        if n_habitaciones < 1:
            raise ValueError("Debe haber al menos 1 habitacion")
        
        # Limpia habitaciones previas para empezar de 0
        self.habitaciones.clear()
        self.habitacion_inicial = None

        # Crea una lista con todas las posiciones posibles del mapa
        todas_posiciones = [(x, y) for x in range(self.ancho) for y in range(self.alto)]
        # Seleciona las posiciones aleatorias donde habra habitaciones
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

        # Crear las habitaciones y las asigna al diccionario
        for i, (x, y) in enumerate(posiciones_habitaciones):
            es_inicial = (x, y) == pos_inicial
            habitacion = Habitacion(
                id=i,
                x=x,
                y=y,
                inicial=es_inicial
            )
            self.habitaciones[(x, y)] = habitacion

            # Referencia a la habitacion inicial
            if es_inicial:
                self.habitacion_inicial = habitacion

        # Conectar habitaciones adyacentes
        direcciones = {
            'norte': (0, -1),
            'sur': (0, 1),
            'este': (1, 0),
            'oeste': (-1, 0)
        }

        # Conecta cada habitacion con su vecino 
        for (x, y), habitacion in self.habitaciones.items():
            for direccion, (dx, dy) in direcciones.items():
                vecino_pos = (x + dx, y + dy)
                if vecino_pos in self.habitaciones:
                    habitacion.conexiones[direccion] = self.habitaciones[vecino_pos]
        
        # Verifica que se establecio la habitacio inicial
        if self.habitacion_inicial is None:
            raise Exception("No se pudo establecer la habitación inicial")

        #Verifica que todas las habitaciones son accesibles
        visitadas = set() # Conjunto de habitaciones visitadas
        cola = [self.habitacion_inicial] # Cola para el recorrido

        while cola:
            habitacion_actual = cola.pop(0) # Toma el primer elemento
            pos_actual = (habitacion_actual.x, habitacion_actual.y)

            # Si no se ha visitado la posicion
            if pos_actual not in visitadas:
                visitadas.add(pos_actual) #Se marca como visitada

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
        
        # Obtener habitaciones que no son iniciales
        habitaciones_disponibles = [h for h in self.habitaciones.values() if not h.inicial]
        
        if not habitaciones_disponibles:
            return  # No hay habitaciones disponibles -> termina
        
        # Colocar al menos un jefe en una esquina
        esquinas = self._obtener_esquinas()
        if esquinas:
            jefe_pos = random.choice(esquinas) # Elige una esquina aleatoria
            # Verifica que existe una habitacion en la esquina
            if jefe_pos in self.habitaciones:
                jefe = self._crear_jefe_aleatorio() # Crea jefe aleatorio
                self.habitaciones[jefe_pos].contenido = jefe # Asigna jefe a la habitacion
        
        # Colocar algunos monstruos (25% de habitaciones restantes)
        habitaciones_restantes = [
                h for h in habitaciones_disponibles if h.contenido is None
            ]
        num_monstruos = max(1, len(habitaciones_restantes) // 4) # Calculo de 25%
        
        # Colocar los monstruos aleatoriamente
        for _ in range(min(num_monstruos, len(habitaciones_restantes))):
            habitacion = random.choice(habitaciones_restantes) # Habitacion al azar
            habitacion.contenido = self._crear_monstruo_aleatorio() # Asignar monstruo
            habitaciones_restantes.remove(habitacion) # Quitar habitacion disponible
        
        # Colocar tesoros (20% de habitaciones restantes)
        num_tesoros = max(1, len(habitaciones_restantes) // 5) # Calcula 20%
        
        # Colocar los tesoros aleatoriamnete
        for _ in range(min(num_tesoros, len(habitaciones_restantes))):
            habitacion = random.choice(habitaciones_restantes) # Habitacion al azar
            habitacion.contenido = self._crear_tesoro_aleatorio() # Asignar tesoro
            habitaciones_restantes.remove(habitacion) # Quitar habitacion disponible

    def _obtener_esquinas(self) -> list[tuple[int, int]]:
        # Retorna las posiciones de las esquinas del mapa.
        return [
            (0, 0),                  # Esquina superior izquierda
            (0, self.alto-1),         # Esquina inferior izquierda
            (self.ancho-1, 0),         # Esquina superior derecha
            (self.ancho-1, self.alto-1) # Esquina inferior derecha
        ]

    def _crear_jefe_aleatorio(self) -> "Jefe":
        # Crea un jefe aleatorio y su recompenza
        nombres = ["Rey Goblin", "Dragon Antiguo", "Rey Lich"]
        recompensas = [
            Objeto("Corona Dorada", 100, "Corona del rey Goblin que ha sido derrotado por un poderoso guerrero."),
            Objeto("Gema del Poder", 250, "Gema mágica muy valiosa hecha de las escamas de un dragon"),
            Objeto("Espada Legendaria", 200, "Arma de gran poder de un monarca de la noche")
        ]
        
        # Selecciona aleatoriamente nombre y recompenza 
        nombre = random.choice(nombres)
        recompensa = random.choice(recompensas)
        # Crea jefe con estadisticas fijas (vida, ataque)
        return Jefe(nombre=nombre, vida=5, ataque=2, recompensa_especial=recompensa)
        
    
    def _crear_monstruo_aleatorio(self) -> "Monstruo":
        # Crea un monstruo aleatorio.
        nombres = ["Goblin", "Orco", "Esqueleto", "Araña Gigante", "Ghoul"]
        nombre = random.choice(nombres) # Elije nombre aleatorio
        vida = random.randint(2, 4) # Vida entre 2 y 4 puntos
        ataque = random.randint(1, 2) # Ataque entre 1 y 2 puntos
        # Crea un monstruo con estadisticas variables
        return Monstruo(nombre=nombre, vida=vida, ataque=ataque)

    def _crear_tesoro_aleatorio(self) -> "Tesoro":
        # Crea un tesoro aleatorio.
        objetos = [
            Objeto("Monedas de Oro", 25, "Monedas brillantes"),
            Objeto("Poción de Vida", 15, "Restaura energía"),
            Objeto("Gema Preciosa", 50, "Una gema valiosa"),
            Objeto("Espada de Hierro", 30, "Arma básica pero útil")
        ]
        
        objeto = random.choice(objetos)  # Selecciona objeto aleatorio
        return Tesoro(recompensa=objeto)  # Crear tesoro con ese objeto



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
        
        # Obtener habitacion actual
        habitacion_actual = self.mapa.habitaciones.get(self.posicion_actual)

        if habitacion_actual is None:
            return "No hay habitacion en esta posicion"
        
        # Marcar como visitada
        habitacion_actual.visitada = True

        # Si no hay habitacion
        if habitacion_actual.contenido is None:
            return "La habitacion esta vacia... solo hay polvo."
        
        # Interactuar con el contenido
        resultado = habitacion_actual.contenido.interactuar(self)

        # Limpiar el contenido despues de interctuar
        if isinstance(habitacion_actual.contenido, (Tesoro, Monstruo, Jefe)):
            habitacion_actual.contenido = None

        return resultado

    
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
    def interactuar(self, explorador) -> str:
        # Permite al explorador recoger el tesoro.
        # Agregar la recompensa al inventario del explorador
        explorador.inventario.append(self.recompensa)
        
        return f"Has encontrado un tesoro! Obtuviste -> {self.recompensa.nombre}"

    @property
    def descripcion(self) -> str:
        return f"Un gran tesoro que contiene: {self.recompensa.nombre}"

    @property
    def tipo(self) -> str:
        return "Tesoro"

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

    def interactuar(self, explorador) -> str:
        # Simula el combate del enemigo vs el explorador
        # Crea una lista que guarda la historia del combate
        resultado = []
        monstruo_vida = self.vida

        # Registro inicial del combate
        resultado.append(f"Alerta, te enfrentas a {self.nombre} :o")

        # Bucle del combate: continua hasta que uno muera
        while monstruo_vida > 0 and explorador.esta_vivo:
            # 60% de que el explorador logre atacar exitosamente 
            if random.random() < 0.6:
                monstruo_vida -= 1 # Monstruo recibe daño
                resultado.append(f"Atacas a {self.nombre}. Vida del enemigo: {monstruo_vida}")
        
            else:
                explorador.recibir_dano(self.ataque) # Explorador recibe daño
                resultado.append(f"{self.nombre} te inflinge {self.ataque} de daño. Tu vida: {explorador.vida}")

        # Determina el resultado del combate
        if not explorador.esta_vivo: # Explorador pierde
            resultado.append(f"Has perdido... {self.nombre} te ha derrotado :()")
        else:                        # Explorador gana
            resultado.append(f"Has derrotado a {self.nombre} :3")

        # Se agrega al registro del combate
        return "\n".join(resultado)
    

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


    def interactuar(self, explorador) -> str:
        # Simula el combate contra un jefe del dungeon

        # Crea una lista que guarda la historia del combate
        resultado = []
        jefe_vida = self.vida

        # Registro inicial del combate contra el jefe
        resultado.append(f"PELIGRO! Te enfrentas a uno de los jefes de la mazmorra, {self.nombre} :o")

        # Bucle del combate: continua hasta que uno muere 
        while jefe_vida > 0 and explorador.esta_vivo:
            # 40% de probabilidad 
            if random.random() < 0.4:
                jefe_vida -= 1; # El jefe recibe daño
                resultado.append(f"Atacaste a {self.nombre}. Vida del jefe: {jefe_vida}")

            else:
                explorador.recibir_dano(self.ataque) # El explorador recibe MAS daño
                resultado.append(f"El jefe {self.nombre} te inflinge {self.ataque} de daño. Tu vida: {explorador.vida}")

        # Determina el resultado con recompensas
        if not explorador.esta_vivo:
            resultado.append(f"Has sido derrotado por el jefe {self.nombre}!!")
        else:
            # Si gana obtiene su recompensa 
            explorador.inventario.append(self.recompensa_especial)
            resultado.append(f"¡Has derrotado al jefe {self.nombre}!")
            resultado.append(f"Felicidades, obtuviste una recompensa especial ---> <{self.recompensa_especial.nombre}>!")
            
            # 30% probabilidad de una segunda recompensa
            if random.random() < 0.3:
                explorador.inventario.append(self.recompensa_especial)
                resultado.append("¡BONIFICACIÓN! ¡Obtuviste una segunda recompensa especial!")
        
        # Se agrega al registro del combate
        return "\n".join(resultado)