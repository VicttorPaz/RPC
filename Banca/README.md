# Banco Distribuido y Control de Estado (Stateful Services)

Simulación de una cuenta bancaria por consola en la que el cliente consulta su saldo, deposita y retira dinero mediante llamadas a métodos remotos. Cada cliente que se conecta recibe su propia cuenta en el servidor.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![Pyro4](https://img.shields.io/badge/Pyro4-objetos%20remotos-informational?style=for-the-badge)
![Name Server](https://img.shields.io/badge/Pyro4-Name%20Server-informational?style=for-the-badge)
![Sesiones](https://img.shields.io/badge/instancia-por%20sesi%C3%B3n-informational?style=for-the-badge)
![Serializador](https://img.shields.io/badge/serializador-serpent-orange?style=for-the-badge)
![Arquitectura](https://img.shields.io/badge/arquitectura-cliente--servidor-green?style=for-the-badge)
![RPC](https://img.shields.io/badge/comunicaci%C3%B3n-llamadas%20remotas-green?style=for-the-badge)
![Interfaz](https://img.shields.io/badge/interfaz-consola-lightgrey?style=for-the-badge)


## Tabla de contenido

- [Descripción general](#descripción-general)
- [Características](#características)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Cómo funciona](#cómo-funciona)
- [Capturas de pantalla](#capturas-de-pantalla)

## Descripción general

Este proyecto es una práctica de sistemas distribuidos que muestra cómo manejar estado por cliente en un servidor Pyro4. El servidor define la clase `CuentaBancaria`, con un saldo que empieza en cero y tres operaciones: consultar, depositar y retirar. El cliente muestra un menú en la terminal y envía cada acción al servidor.

El servidor usa el modo de instancia por sesión de Pyro4. Cuando un cliente se conecta, se crea una cuenta nueva para él con un identificador aleatorio del tipo `Cliente-472`, y esa cuenta se elimina cuando el cliente cierra su sesión. Así, dos clientes conectados al mismo tiempo no comparten saldo. Para que el cliente encuentre al servidor sin conocer su dirección, ambos usan el Name Server de Pyro4, donde el servicio queda publicado como `banco.cuenta`.

## Características

- Consulta de saldo, depósito y retiro desde un menú interactivo.
- Una cuenta independiente por cliente, con saldo inicial de 0.0 y un identificador aleatorio entre `Cliente-100` y `Cliente-999`.
- Validación en el servidor: los montos deben ser mayores a cero y no se puede retirar más de lo que hay en la cuenta.
- Las validaciones lanzan una excepción que viaja hasta el cliente, donde se muestra el mensaje de error.
- El servidor imprime en su consola cada conexión, acción, cambio de saldo, advertencia y desconexión, identificadas con el nombre del cliente.
- Ambos programas usan el serializador `serpent`, que no ejecuta código arbitrario al deserializar como sí puede hacerlo `pickle`.

## Requisitos previos

- Python 3 [COMPLETAR: versión exacta usada]
- pip
- Pyro4

Tanto el servidor como los clientes necesitan tener Pyro4 instalado. Si se ejecutan en equipos distintos dentro de la misma red, todos deben poder alcanzar al Name Server.

## Instalación

Guarda los archivos `servidor.py` y `cliente.py` en una misma carpeta y abre una terminal dentro de ella.

Instala Pyro4:

```bash
pip install Pyro4
```

Si prefieres aislar las dependencias en un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate
pip install Pyro4
```

## Uso

Se necesitan al menos tres terminales abiertas. El orden importa: primero el Name Server, después el servidor y al final uno o más clientes.

### 1. Iniciar el Name Server

```bash
python -m Pyro4.naming
```

Salida esperada:

```text
Not starting broadcast server for localhost.
NS running on localhost:9090 (127.0.0.1)
Warning: HMAC key not set. Anyone can connect to this server!
URI = PYRO:Pyro.NameServer@localhost:9090
```

Deja esta terminal abierta mientras uses el sistema.

### 2. Iniciar el servidor

```bash
python servidor.py
```

Salida esperada:

```text
Servidor de CuentaBancaria activo y esperando conexiones...
```

El servidor queda esperando peticiones. Tampoco debes cerrar esta terminal.

### 3. Ejecutar un cliente

```bash
python cliente.py
```

Ejemplo de una sesión con un depósito, un retiro y una consulta:

```text
--- BANCO DISTRIBUIDO ---
1. Consultar saldo
2. Depositar
3. Retirar
4. Salir
Seleccione una opción: 2
Ingrese monto a depositar: 500
Depósito exitoso.

--- BANCO DISTRIBUIDO ---
1. Consultar saldo
2. Depositar
3. Retirar
4. Salir
Seleccione una opción: 3
Ingrese monto a retirar: 120
Retiro exitoso.

--- BANCO DISTRIBUIDO ---
1. Consultar saldo
2. Depositar
3. Retirar
4. Salir
Seleccione una opción: 1
Saldo actual: 380.0

--- BANCO DISTRIBUIDO ---
1. Consultar saldo
2. Depositar
3. Retirar
4. Salir
Seleccione una opción: 4
Saliendo del sistema...
```

Lo que se ve al mismo tiempo en la terminal del servidor:

```text
[CONEXIÓN] ¡Cliente-472 se ha conectado al servidor!
[ACCIÓN - Cliente-472] Solicitó DEPÓSITO de: 500.0
[ESTADO - Cliente-472] Saldo actualizado: 500.0
[ACCIÓN - Cliente-472] Solicitó RETIRO de: 120.0
[ESTADO - Cliente-472] Saldo actualizado: 380.0
[ACCIÓN - Cliente-472] Consultó su SALDO.
[DESCONEXIÓN] Cliente-472 ha cerrado la sesión.
```

Ejemplo de un retiro mayor al saldo disponible:

```text
Seleccione una opción: 3
Ingrese monto a retirar: 1000
Ocurrió un error: Error: Saldo insuficiente para realizar el retiro.
```

En la terminal del servidor aparece además la línea `[ADVERTENCIA - Cliente-472] Retiro fallido: Saldo insuficiente.`

El cliente atrapa los errores con un único `try/except` que rodea todo el menú. Por eso, cualquier error termina el programa después de mostrar el mensaje, y el saldo de esa sesión se pierde. Esto aplica tanto a los montos inválidos como a escribir letras en lugar de un número.

Para probar con varios usuarios, abre otra terminal y ejecuta `python cliente.py` de nuevo. Cada cliente verá su propio saldo.


## Cómo funciona

El proyecto usa Pyro4 (Python Remote Objects), una biblioteca que permite llamar métodos de un objeto que vive en otro proceso, o incluso en otro equipo, como si fuera local. Hay tres piezas:

1. Name Server. Es un directorio que relaciona nombres con direcciones de objetos remotos. Se inicia con `python -m Pyro4.naming` y escucha por defecto en el puerto 9090.
2. Servidor (`servidor.py`). Define la clase `CuentaBancaria`, marcada con `@Pyro4.expose` para que sus métodos se puedan llamar desde fuera y con `@Pyro4.behavior(instance_mode="session")` para que Pyro4 cree una instancia por cada conexión de cliente. Después del código de la clase, el script crea un `Pyro4.Daemon`, localiza el Name Server, registra la clase en el demonio y publica la URI resultante con el nombre `banco.cuenta`. Al final, `daemon.requestLoop()` deja el proceso atendiendo llamadas.
3. Cliente (`cliente.py`). Crea un `Pyro4.Proxy("PYRONAME:banco.cuenta")`, un objeto intermediario que consulta al Name Server la dirección real y reenvía cada llamada al servidor. Muestra el menú en un ciclo y, al elegir la opción 4, llama a `_pyroRelease()` para cerrar la conexión y termina.

Métodos que expone la cuenta:

| Método | Qué hace | Devuelve |
|---|---|---|
| `depositar(monto)` | Suma el monto al saldo. Lanza `ValueError` si el monto es menor o igual a cero | Saldo actualizado |
| `retirar(monto)` | Resta el monto del saldo. Lanza `ValueError` si el monto es menor o igual a cero o si supera el saldo | Saldo actualizado |
| `consultar_saldo()` | Consulta el saldo actual | Saldo |

Flujo de una operación:

```text
cliente.py  ->  Name Server: "¿dónde está banco.cuenta?"
Name Server ->  cliente.py:  URI del objeto en el servidor
cliente.py  ->  servidor.py: depositar(500.0)
servidor.py ->  cliente.py:  500.0
```

## Capturas de pantalla

Name Server y servidor en ejecución:

<img width="1211" height="552" alt="imagen" src="https://github.com/user-attachments/assets/ac51d818-f734-4bb7-b973-8052f35ae6d3" />

Cliente usando el menú:

<img width="1211" height="552" alt="imagen" src="https://github.com/user-attachments/assets/9ce61152-2536-4305-af19-be7ae91e3bc7" />
