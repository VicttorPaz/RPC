import random
import Pyro4

# Configuración del serializador compartido con el cliente
Pyro4.config.SERIALIZER = "serpent"


# Define el comportamiento por sesión: se crea una instancia única de la clase por cada cliente conectado
@Pyro4.behavior(instance_mode="session")
@Pyro4.expose  # Expone la clase y sus métodos para que puedan ser invocados de forma remota vía Pyro4
class CuentaBancaria(object):
    def __init__(self):
        # Asigna un identificador único aleatorio al cliente al establecer la sesión
        self.id_cliente = f"Cliente-{random.randint(100, 999)}"
        self.saldo = 0.0
        print(f"[CONEXIÓN] ¡{self.id_cliente} se ha conectado al servidor!")

    def __del__(self):
        # Destructor ejecutado cuando la sesión del cliente finaliza o se libera el objeto
        print(f"[DESCONEXIÓN] {self.id_cliente} ha cerrado la sesión.")

    def depositar(self, monto):
        print(f"[ACCIÓN - {self.id_cliente}] Solicitó DEPÓSITO de: {monto}")
        # Valida que el monto ingresado sea estrictamente mayor a cero
        if monto <= 0:
            raise ValueError("El monto a depositar debe ser mayor a cero.")
        self.saldo += monto
        print(f"[ESTADO - {self.id_cliente}] Saldo actualizado: {self.saldo}")
        return self.saldo

    def retirar(self, monto):
        print(f"[ACCIÓN - {self.id_cliente}] Solicitó RETIRO de: {monto}")
        # Valida que el monto a retirar sea positivo
        if monto <= 0:
            raise ValueError("El monto a retirar debe ser mayor a cero.")
        # Valida que exista suficiente saldo para cubrir el retiro
        if monto > self.saldo:
            print(f"[ADVERTENCIA - {self.id_cliente}] Retiro fallido: Saldo insuficiente.")
            raise ValueError("Error: Saldo insuficiente para realizar el retiro.")
        self.saldo -= monto
        print(f"[ESTADO - {self.id_cliente}] Saldo actualizado: {self.saldo}")
        return self.saldo

    def consultar_saldo(self):
        print(f"[ACCIÓN - {self.id_cliente}] Consultó su SALDO.")
        return self.saldo


# Inicializa el daemon de Pyro4 para escuchar solicitudes remotas
daemon = Pyro4.Daemon()
# Localiza el servidor de nombres (Name Server) en la red local o localhost
ns = Pyro4.locateNS()
# Registra la clase CuentaBancaria en el daemon obteniendo su URI interna
uri = daemon.register(CuentaBancaria)
# Publica el objeto en el Name Server bajo el nombre lógico "banco.cuenta"
ns.register("banco.cuenta", uri)
print("Servidor de CuentaBancaria activo y esperando conexiones...")
# Inicia el bucle de atención permanente para procesar las peticiones entrantes
daemon.requestLoop()