import Pyro4  

# Creamos un Proxy usando el nombre registrado en el Name Server
calculadora = Pyro4.Proxy("PYRONAME:Calculadora")

# Ciclo para solicitar el primer número y validar que no se ingresen letras
while True:
  try:
    # Intentamos convertir la entrada a un número entero
    a = int(input("Primer número: "))
    break  # Si se convierte con éxito, salimos del ciclo
  except ValueError:
    # Si ocurre un error (el usuario escribió letras u otros caracteres), mostramos el error y repetimos
    print("Error: Solo se permiten números enteros.")

# Ciclo para solicitar el segundo número con la misma validación
while True:
  try:
    b = int(input("Segundo número: "))
    break
  except ValueError:
    print("Error: Solo se permiten números enteros.")

# Solicitamos la operación deseada y eliminamos espacios en blanco con .strip()
op = input("Operación (+, -, *, /): ").strip()

# Evaluamos la operación elegida y llamamos al método correspondiente en el servidor a través del proxy
if op == "+":
  print(calculadora.sumar(a, b))
elif op == "-":
  print(calculadora.restar(a, b))
elif op == "*":
  print(calculadora.multiplicar(a, b))
elif op == "/":
  print(calculadora.dividir(a, b))
else:
  print("Operación no válida")