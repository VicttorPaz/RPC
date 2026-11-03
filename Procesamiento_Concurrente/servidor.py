import Pyro4


@Pyro4.expose
@Pyro4.behavior(instance_mode="session")
class Procesador:
    def __init__(self):
        # Se ejecuta cuando un cliente nuevo se conecta
        # Aquí se guarda su IP y puerto para mostrarlos en los avisos
        ip, puerto = Pyro4.current_context.client_sock_addr[:2]
        self.cliente = f"{ip}:{puerto}"
        print("Cliente conectado:", self.cliente)

    def fibonacci(self, n):
        # Este es el método que el cliente llama de forma remota
        print(self.cliente, "pidió fibonacci de", n)
        resultado = self._fib(n)
        print("Trabajo terminado para", self.cliente)
        return resultado

    def _fib(self, n):
        # La recursión repite muchos cálculos, por eso tarda y es una tarea pesada
        if n < 2:
            return n
        return self._fib(n - 1) + self._fib(n - 2)


daemon = Pyro4.Daemon()  # el servidor que atiende las peticiones
ns = Pyro4.locateNS()  # busca el name server que ya está corriendo
uri = daemon.register(Procesador)  # publica la clase y obtiene su dirección
ns.register("practica.procesador", uri)  # el cliente la encuentra con este nombre
print("Servidor listo")
daemon.requestLoop()  # se queda esperando clientes hasta que lo detengas