import Pyro4

# Configuración del serializador a 'serpent' (más seguro y compatible que pickle)
Pyro4.config.SERIALIZER = "serpent"

try:
    # Se crea un proxy dinámico utilizando el Name Server buscando el objeto registrado como "banco.cuenta"
    cuenta = Pyro4.Proxy("PYRONAME:banco.cuenta")
    # Bucle principal para mostrar el menú interactivo al usuario
    while True:
        print("\n--- BANCO DISTRIBUIDO ---")
        print("1. Consultar saldo")
        print("2. Depositar")
        print("3. Retirar")
        print("4. Salir")
        opcion = input("Seleccione una opción: ")

        # Opción 1: Llama al método remoto para obtener el saldo actual
        if opcion == "1":
            print(f"Saldo actual: {cuenta.consultar_saldo()}")
        # Opción 2: Solicita un monto al usuario y llama al método remoto de depósito
        elif opcion == "2":
            monto = float(input("Ingrese monto a depositar: "))
            cuenta.depositar(monto)
            print("Depósito exitoso.")
        # Opción 3: Solicita un monto y llama al método remoto de retiro
        elif opcion == "3":
            monto = float(input("Ingrese monto a retirar: "))
            cuenta.retirar(monto)
            print("Retiro exitoso.")
        # Opción 4: Libera la conexión con el servidor y rompe el ciclo para finalizar
        elif opcion == "4":
            cuenta._pyroRelease()
            print("Saliendo del sistema...")
            break
        # Manejo de opción no contemplada en el menú
        else:
            print("Opción inválida.")
# Captura cualquier excepción remota o local (como errores de conexión o validaciones) y la muestra en pantalla
except Exception as e:
    print(f"Ocurrió un error: {e}")