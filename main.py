from dungeon_generator.models import Mapa, Explorador
import random


def mostrar_titulo(titulo: str):
    print(f"\n{'='*50}")
    print(f"  {titulo}")
    print(f"{'='*50}\n")

def mostrar_estado_explorador(explorador: Explorador):
    # Muestra el estado actual del explorador
    print(f"ESTADO DEL EXPLORADOR")
    print(f"-Vida: {explorador.vida}")
    print(f"-Posición: {explorador.posicion_actual}")
    print(f"-Inventario ({len(explorador.inventario)} objetos):")

    valor_total = 0
    for obj in explorador.inventario:
        print(f"      📦 {obj.nombre} (Valor: {obj.valor}) - {obj.descripcion}")
        valor_total += obj.valor
    
    if valor_total > 0:
        print(f"Inventario: {valor_total}")
    else:
        print(f"Inventario vacío")

def mostrar_info_mapa(mapa: Mapa):
    # Muestra información del mapa.
    print(f"====INFORMACIÓN DEL MAPA====")
    print(f"-Dimensiones: {mapa.ancho}x{mapa.alto}")
    print(f"-Total de habitaciones: {len(mapa.habitaciones)}")
    if mapa.habitacion_inicial:
        print(f"-Habitación inicial: ({mapa.habitacion_inicial.x}, {mapa.habitacion_inicial.y})")
    else:
        print(f"-Habitación inicial: No establecida")    
    # Contar tipos de contenido
    tesoros = sum(1 for h in mapa.habitaciones.values() if h.contenido and h.contenido.tipo == "Tesoro")
    monstruos = sum(1 for h in mapa.habitaciones.values() if h.contenido and h.contenido.tipo == "Monstruo")
    jefes = sum(1 for h in mapa.habitaciones.values() if h.contenido and h.contenido.tipo == "Jefe")
    vacias = len(mapa.habitaciones) - tesoros - monstruos - jefes
    
    print(f"====Distribución de contenido====")
    print(f"-Tesoros: {tesoros}")
    print(f"-Monstruos: {monstruos}")
    print(f"-Jefes: {jefes}")
    print(f"-Vacías: {vacias}")

def modo_exploracion(explorador: Explorador, max_movimientos: int = 15):
    #Modo de exploración interactiva automática.
    print(f"INICIANDO EXPLORACIÓN AUTOMÁTICA (máximo {max_movimientos} movimientos)")
    
    movimientos = 0
    habitaciones_visitadas = set()
    
    while explorador.esta_vivo and movimientos < max_movimientos:
        print(f"\n-----<Movimiento {movimientos + 1}>-----")
        
        # Explorar habitación actual
        pos_actual = explorador.posicion_actual
        if pos_actual not in habitaciones_visitadas:
            print(f"+Llegaste a una nueva habitación en {pos_actual}")
            resultado_exploracion = explorador.explorar_habitacion()
            print(f"<<{resultado_exploracion}>>")
            habitaciones_visitadas.add(pos_actual)
        else:
            print(f"--Ya habías visitado esta habitación en {pos_actual}--")
        
        # Verificar si sigue vivo después de explorar
        if not explorador.esta_vivo:
            print(f"\n-------<El explorador ha muerto durante la exploración...>--------")
            break
        
        # Obtener direcciones disponibles
        direcciones = explorador.obtener_habitaciones_adyacentes()
        if direcciones:
            print(f"===Direcciones disponibles: {', '.join(direcciones)}===")
            
            # Elegir dirección / se prioriza direcciones no visitadas
            direccion_elegida = None
            for direccion in direcciones:
                # Simular hacia dónde llevaría cada dirección
                habitacion_actual = explorador.mapa.habitaciones[pos_actual]
                if direccion in habitacion_actual.conexiones:
                    destino = habitacion_actual.conexiones[direccion]
                    pos_destino = (destino.x, destino.y)
                    if pos_destino not in habitaciones_visitadas:
                        direccion_elegida = direccion
                        break
            
            # Si no hay direcciones nuevas, elegir cualquiera
            if not direccion_elegida:
                direccion_elegida = random.choice(direcciones)
            
            # Moverse
            print(f"-Intentando moverse hacia: {direccion_elegida}-")
            if explorador.mover(direccion_elegida):
                print(f"+Movimiento exitoso!+")
            else:
                print(f"-No se pudo mover hacia {direccion_elegida}-")
                break
        else:
            print(f"<>---No hay direcciones disponibles. Exploración terminada.---<>")
            break
            
        movimientos += 1
        
        # Pequeña pausa para lectura
        if movimientos % 3 == 0:
            input("|Presiona |Enter| para continuar...|")
    
    return habitaciones_visitadas

def main():
    #Función principal del "demo".
    mostrar_titulo("GENERADOR DE DUNGEONS - DEMO COMPLETO")
    
    try:
        # Configuración del demo
        ANCHO_MAPA = 5
        ALTO_MAPA = 5
        NUM_HABITACIONES = 10
        
        print(f"<>===Configuración del demo:")
        print(f"   •-Mapa: {ANCHO_MAPA}x{ALTO_MAPA}")
        print(f"   •-Habitaciones: {NUM_HABITACIONES}")
        
        # 1: Crear y generar mapa
        mostrar_titulo("1: GENERACIÓN DEL MAPA")
        
        print(f">Creando mapa de {ANCHO_MAPA}x{ALTO_MAPA}...")
        mapa = Mapa(ancho=ANCHO_MAPA, alto=ALTO_MAPA)
        
        print(f"> Generando estructura con {NUM_HABITACIONES} habitaciones...")
        mapa.generar_estructura(NUM_HABITACIONES)
        print(f"< Estructura generada exitosamente!")
        
        print(f"> Colocando contenido (tesoros, monstruos, jefes)...")
        mapa.colocar_contenido()
        print(f"< Contenido distribuido!")
        
        mostrar_info_mapa(mapa)
        
        # 2: Crear explorador
        mostrar_titulo("2: CREACIÓN DEL EXPLORADOR")
        
        if mapa.habitacion_inicial is None:
            raise Exception("No se pudo generar la habitación inicial")

        pos_inicial = (mapa.habitacion_inicial.x, mapa.habitacion_inicial.y)
        explorador = Explorador(mapa=mapa, posicion_actual=pos_inicial)
        
        print(f"< Explorador creado exitosamente!")
        mostrar_estado_explorador(explorador)
        
        input("\n|Presiona |Enter| para comenzar la exploración...|")
        
        # 3: Exploración
        mostrar_titulo("3: EXPLORACIÓN DEL DUNGEON")
        
        habitaciones_visitadas = modo_exploracion(explorador)
        
        #  4: Resultados finales
        mostrar_titulo("4: RESULTADOS FINALES")
        
        print(f"====ESTADÍSTICAS DE LA AVENTURA:")
        print(f"   -Habitaciones visitadas: {len(habitaciones_visitadas)}/{len(mapa.habitaciones)}")
        print(f"   -Estado final: {'VIVO' if explorador.esta_vivo else 'MUERTO'}")
        
        mostrar_estado_explorador(explorador)
        
        # Mostrar habitaciones no visitadas
        no_visitadas = len(mapa.habitaciones) - len(habitaciones_visitadas)
        if no_visitadas > 0:
            print(f"\n-Quedan {no_visitadas} habitaciones por explorar.")
            print(f"   |...El dungeon aún guarda secretos...|")
        else:
            print(f"\n  |FELICIDADES! Exploraste todo el dungeon|")
        
        # Mensaje final
        if explorador.esta_vivo:
            if len(explorador.inventario) > 0:
                print(f"\nAventura exitosa! Sobreviviste y volviste con tesoros :3")
            else:
                print(f"\nRegresaste vivo, pero sin tesoros... Inténtalo otra vez :T")
        else:
            print(f"\nEl explorador pereció en el dungeon... Sus tesoros se perdieron para siempre :()")
        
        print(f"\n---<Gracias por probar el Generador de Dungeons!>---")
        
    except ValueError as e:
        print(f"Error de configuración: {e}")
    except Exception as e:
        print(f"Error durante la demo: {e}")
        print(f"Verifica que todas las clases estén implementadas correctamente.")

if __name__ == "__main__":
    main()