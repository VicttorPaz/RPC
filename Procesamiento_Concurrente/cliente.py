import time
import Pyro4


def al_terminar(resultado):
    print("[callback] Fibonacci calculado:", resultado)
    return resultado


proxy = Pyro4.Proxy("PYRONAME:practica.procesador")
Pyro4.asyncproxy(proxy)  # modifica el proxy, no devuelve nada

# No espera: devuelve un future al instante
futuro = proxy.fibonacci(35)
futuro.then(al_terminar)

print("Trabajo enviado, el cliente sigue libre")

# Mientras el servidor trabaja, el cliente hace otras cosas
contador = 0
while not futuro.ready:
    contador += 1
    print(f"Haciendo otra tarea ({contador})...")
    time.sleep(1)

print("Resultado final:", futuro.value)