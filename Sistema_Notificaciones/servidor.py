import Pyro4


@Pyro4.expose
class ServicioMensajes:
    def __init__(self):
        # Inicializa las estructuras locales para los mensajes y los clientes activos.
        self.mensajes = []
        self.clientes_activos = set()

    def conectar(self, nombre_cliente):
        # Registra la conexión del cliente y devuelve un saludo de bienvenida.
        self.clientes_activos.add(nombre_cliente)
        print(f"\n[+] ¡Cliente conectado!: {nombre_cliente}")
        return f"Bienvenido al sistema, {nombre_cliente}."

    def desconectar(self, nombre_cliente):
        # Remueve al cliente del conjunto de activos al finalizar su sesión.
        if nombre_cliente in self.clientes_activos:
            self.clientes_activos.remove(nombre_cliente)
        print(f"\n[-] ¡Cliente desconectado!: {nombre_cliente}")
        return "Desconectado exitosamente."

    def enviar_mensaje(self, remitente, texto):
        # Almacena el mensaje recibido en la lista y lo muestra en la consola.
        mensaje_completo = f"[{remitente}]: {texto}"
        self.mensajes.append(mensaje_completo)
        print(f"Mensaje recibido de {remitente}: {texto}")
        return "Mensaje guardado exitosamente por el servidor."

    def obtener_mensajes(self):
        # Retorna el historial completo de mensajes almacenados en el servidor.
        return self.mensajes


# Configura el demonio, localiza el Name Server y publica el servicio de mensajería.
daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(ServicioMensajes)
ns.register("practica.mensajeria", uri)
print("Servidor de Mensajeria listo y registrado en el Name Server.")
daemon.requestLoop()