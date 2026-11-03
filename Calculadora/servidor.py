import Pyro4  


@Pyro4.expose
class Calculadora(object):

  def sumar(self, a, b):
    return a + b

  def restar(self, a, b):
    return a - b

  def multiplicar(self, a, b):
    return a * b

  def dividir(self, a, b):
    # Validamos que no se intente dividir entre cero
    if b == 0:
      return "Error: no se puede dividir entre cero"
    return a / b


# Inicializamos el daemon (demonio) de Pyro4 para escuchar solicitudes
daemon = Pyro4.Daemon()

# Localizamos el servidor de nombres (Name Server) de Pyro4
ns = Pyro4.locateNS()

# Registramos la clase Calculadora en el daemon para obtener su URI
uri_calculadora = daemon.register(Calculadora)

# Registramos esa URI en el Name Server con un nombre lógico ("Calculadora")
ns.register("Calculadora", uri_calculadora)

print("Servidor local listo.")

# Entramos en el bucle de solicitudes para atender las peticiones de los clientes
daemon.requestLoop()