# Sistema de mensajería distribuida con Pyro4

Servicio de mensajería por consola en el que varios clientes se conectan a un servidor, envían mensajes y se desconectan, todo mediante llamadas a métodos remotos con Pyro4.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![Pyro4](https://img.shields.io/badge/Pyro4-objetos%20remotos-informational?style=for-the-badge)
![Name Server](https://img.shields.io/badge/Pyro4-Name%20Server-informational?style=for-the-badge)
![Arquitectura](https://img.shields.io/badge/arquitectura-cliente--servidor-green?style=for-the-badge)
![RPC](https://img.shields.io/badge/comunicaci%C3%B3n-llamadas%20remotas-green?style=for-the-badge)
![TCP](https://img.shields.io/badge/transporte-TCP-lightgrey?style=for-the-badge)
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

Este proyecto es una práctica de sistemas distribuidos que muestra cómo un cliente puede usar los métodos de un objeto que vive en otro proceso. El servidor define una clase `ServicioMensajes` que lleva el registro de los clientes conectados y guarda los mensajes que reciben. El cliente le pide un nombre de usuario a la persona, avisa al servidor que se conectó, envía los mensajes que se escriban en la terminal y, al escribir `salir`, avisa de su desconexión.

Para que el cliente encuentre al servidor sin conocer su dirección, ambos usan el Name Server de Pyro4. El servidor publica el servicio con el nombre `practica.mensajeria` y el cliente lo busca por ese nombre. Con esto se practican cuatro ideas: exponer una clase para uso remoto, registrar un servicio por nombre, consumirlo desde otro proceso y avisar al servidor cuando una sesión termina.

## Características

- Registro de conexión: el cliente se identifica con un nombre de usuario y el servidor responde con un saludo de bienvenida.
- Envío de mensajes: cada mensaje se manda al servidor, que lo guarda con el formato `[usuario]: texto` y lo imprime en su consola.
- Desconexión controlada: al escribir `salir`, el cliente notifica al servidor y este elimina al usuario de la lista de clientes activos.
- La notificación de desconexión está dentro de un bloque `finally`, por lo que se envía aunque el cliente termine por un error.
- El cliente atrapa los errores de conexión e imprime el motivo en lugar de cerrarse con un traceback.
- El servicio también ofrece el método `obtener_mensajes`, que devuelve el historial guardado.

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
Servidor de Mensajeria listo y registrado en el Name Server.
```

El servidor queda esperando peticiones. Tampoco debes cerrar esta terminal.

### 3. Ejecutar un cliente

```bash
python cliente.py
```

Ejemplo de una sesión completa en la terminal del cliente:

```text
Servicio encontrado en URI: PYRO:obj_3f2a9c1e5b7d4e6f8a0b1c2d3e4f5a6b@localhost:51234
Ingresa tu nombre de usuario: Ana
Servidor -> Bienvenido al sistema, Ana.
Escribe tu mensaje (o escribe 'salir' para terminar): Hola a todos
Respuesta del servidor -> Mensaje guardado exitosamente por el servidor.
Escribe tu mensaje (o escribe 'salir' para terminar): salir
Servidor -> Desconectado exitosamente.
```

Lo que se ve al mismo tiempo en la terminal del servidor:

```text
[+] ¡Cliente conectado!: Ana
Mensaje recibido de Ana: Hola a todos

[-] ¡Cliente desconectado!: Ana
```

Para probar con varios usuarios, abre otra terminal y ejecuta `python cliente.py` de nuevo con un nombre distinto.



## Cómo funciona

El proyecto usa Pyro4 (Python Remote Objects), una biblioteca que permite llamar métodos de un objeto que vive en otro proceso, o incluso en otro equipo, como si fuera local. Hay tres piezas:

1. Name Server. Es un directorio que relaciona nombres con direcciones de objetos remotos. Se inicia con `python -m Pyro4.naming` y escucha por defecto en el puerto 9090.
2. Servidor (`servidor.py`). Define la clase `ServicioMensajes`, marcada con `@Pyro4.expose` para que sus métodos se puedan llamar desde fuera. Dentro de `main()` crea un `Pyro4.Daemon`, localiza el Name Server, registra la clase en el demonio y publica la URI resultante con el nombre `practica.mensajeria`. Al final, `daemon.requestLoop()` deja el proceso atendiendo llamadas.
3. Cliente (`cliente.py`). Localiza el Name Server con `Pyro4.locateNS()`, obtiene la URI con `ns.lookup("practica.mensajeria")` y crea un `Pyro4.Proxy`, un objeto intermediario que reenvía cada llamada al servidor. Después pide el nombre de usuario, se conecta y entra en un ciclo que envía cada línea escrita hasta que se teclea `salir`.

Métodos que expone el servicio:

| Método | Qué hace | Devuelve |
|---|---|---|
| `conectar(nombre_cliente)` | Agrega al usuario al conjunto de clientes activos e imprime el aviso en el servidor | Saludo de bienvenida |
| `enviar_mensaje(remitente, texto)` | Guarda `[remitente]: texto` en la lista de mensajes e imprime el mensaje en el servidor | Confirmación de que se guardó |
| `obtener_mensajes()` | Consulta el historial almacenado | Lista de mensajes |
| `desconectar(nombre_cliente)` | Quita al usuario del conjunto de clientes activos e imprime el aviso en el servidor | Confirmación de desconexión |

Flujo de una sesión:

```text
cliente.py  ->  Name Server: "¿dónde está practica.mensajeria?"
Name Server ->  cliente.py:  URI del objeto en el servidor
cliente.py  ->  servidor.py: conectar("Ana")
cliente.py  ->  servidor.py: enviar_mensaje("Ana", "Hola a todos")
cliente.py  ->  servidor.py: desconectar("Ana")
```

Nota sobre las instancias: el servidor registra la clase y no un objeto ya creado, así que Pyro4 usa su modo de instancia por defecto, que es una instancia nueva de `ServicioMensajes` por cada conexión de un cliente. Por eso la lista de mensajes y el conjunto de clientes activos pertenecen a cada sesión y no se comparten entre clientes. Lo que sí se ve de forma global son las impresiones en la consola del servidor. El cliente actual tampoco llama a `obtener_mensajes`.

Nota sobre seguridad: el servidor no usa clave HMAC, como avisa el propio Name Server al iniciar. Para pruebas en una red local es suficiente. No lo expongas a internet.

## Capturas de pantalla

Name Server y servidor en ejecución:

<img width="1182" height="331" alt="imagen" src="https://github.com/user-attachments/assets/41e023e0-8ead-4859-8b49-5c524410f6ae" />


Cliente enviando mensajes:

<img width="1182" height="247" alt="imagen" src="https://github.com/user-attachments/assets/80885479-0fdd-4736-bc02-93e6600a67a4" />
