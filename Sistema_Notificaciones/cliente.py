import Pyro4

# Localiza el servicio a través del Name Server, gestiona el chat y notifica la salida.
try:
    ns = Pyro4.locateNS()
    uri = ns.lookup("practica.mensajeria")
    print(f"Servicio encontrado en URI: {uri}")
    servicio = Pyro4.Proxy(uri)
    remitente = input("Ingresa tu nombre de usuario: ")
    # Notifica la conexión inicial del usuario al servidor.
    respuesta_conexion = servicio.conectar(remitente)
    print(f"Servidor -> {respuesta_conexion}")
    try:
        while True:
            texto = input("Escribe tu mensaje (o escribe 'salir' para terminar): ")
            if texto.lower() == 'salir':
                break
            # Envía el mensaje mediante una llamada remota al servidor.
            respuesta = servicio.enviar_mensaje(remitente, texto)
            print(f"Respuesta del servidor -> {respuesta}")
    finally:
        # Garantiza la notificación de desconexión al salir del bucle.
        respuesta_desconexion = servicio.desconectar(remitente)
        print(f"Servidor -> {respuesta_desconexion}")

except Exception as e:
    print(f"Error al conectar con el servicio: {e}")