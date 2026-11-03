# Procesamiento Concurrente y Callback Asíncrono

Servicio remoto que calcula números de Fibonacci con recursión, una tarea pesada a propósito, y un cliente que lo llama sin quedarse bloqueado. El cliente envía el trabajo, sigue haciendo otras cosas y recupera el resultado cuando el servidor termina.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![Pyro4](https://img.shields.io/badge/Pyro4-objetos%20remotos-informational?style=for-the-badge)
![Name Server](https://img.shields.io/badge/Pyro4-Name%20Server-informational?style=for-the-badge)
![Async](https://img.shields.io/badge/Pyro4-asyncproxy-informational?style=for-the-badge)
![Futures](https://img.shields.io/badge/resultado-futures%20y%20callback-orange?style=for-the-badge)
![Sesiones](https://img.shields.io/badge/instancia-por%20sesi%C3%B3n-informational?style=for-the-badge)
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

Este proyecto es una práctica de sistemas distribuidos sobre procesamiento concurrente y callbacks asíncronos. El servidor define la clase `Procesador`, que calcula el número de Fibonacci de un entero con una función recursiva. Esa versión repite muchos cálculos y tarda varios segundos con valores como 35, así que sirve como ejemplo de trabajo intensivo.

Con una llamada normal, el cliente se quedaría esperando sin hacer nada hasta que el servidor responda. Aquí el cliente usa `Pyro4.asyncproxy`, que hace que cada llamada remota devuelva al instante un objeto `future`. El cliente envía el cálculo, sigue ejecutando otras tareas mientras el servidor trabaja, y obtiene el resultado de dos formas: con una función callback que se ejecuta al terminar y consultando el future. Para que el cliente encuentre al servidor sin conocer su dirección, ambos usan el Name Server de Pyro4, donde el servicio queda publicado como `practica.procesador`.

## Características

- Cálculo de Fibonacci con recursión en el servidor, como tarea pesada.
- Llamada asíncrona desde el cliente: `proxy.fibonacci(35)` no espera y devuelve un future.
- Callback registrado con `futuro.then(...)`, que se ejecuta cuando llega el resultado.
- El cliente sigue trabajando mientras espera y puede consultar `futuro.ready` para saber si el resultado ya llegó.
- Una instancia de `Procesador` por cada cliente conectado, con el modo de instancia por sesión.
- El servidor muestra la IP y el puerto del cliente en cada aviso: conexión, petición recibida y trabajo terminado.
- El método auxiliar `_fib` empieza con guion bajo, por lo que Pyro4 no lo expone al cliente.

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
Servidor listo
```

El servidor queda esperando peticiones. Tampoco debes cerrar esta terminal.

### 3. Ejecutar el cliente

```bash
python cliente.py
```

Ejemplo de salida en la terminal del cliente. La cantidad de líneas "Haciendo otra tarea" depende de cuántos segundos tarde el cálculo en tu equipo:

```text
Trabajo enviado, el cliente sigue libre
Haciendo otra tarea (1)...
Haciendo otra tarea (2)...
Haciendo otra tarea (3)...
[callback] Fibonacci calculado: 9227465
Resultado final: 9227465
```

La línea del callback puede aparecer antes o después de "Resultado final", porque se ejecuta en otro hilo en cuanto llega la respuesta.

Lo que se ve al mismo tiempo en la terminal del servidor:

```text
Cliente conectado: 127.0.0.1:52814
127.0.0.1:52814 pidió fibonacci de 35
Trabajo terminado para 127.0.0.1:52814
```

El número 35 está escrito directamente en `cliente.py`. Si lo modificas, el tiempo de espera cambia mucho: el costo de la recursión crece muy rápido con cada unidad que se sube. Valores como 30 responden casi de inmediato y valores como 40 pueden tardar bastante más.

Para probar con varios clientes, abre otra terminal y ejecuta `python cliente.py` de nuevo. En el servidor, cada uno aparece con su propia IP y puerto.

## Cómo funciona

El proyecto usa Pyro4 (Python Remote Objects), una biblioteca que permite llamar métodos de un objeto que vive en otro proceso, o incluso en otro equipo, como si fuera local. Hay tres piezas:

1. Name Server. Es un directorio que relaciona nombres con direcciones de objetos remotos. Se inicia con `python -m Pyro4.naming` y escucha por defecto en el puerto 9090.
2. Servidor (`servidor.py`). Define la clase `Procesador`, marcada con `@Pyro4.expose` para que sus métodos se puedan llamar desde fuera y con `@Pyro4.behavior(instance_mode="session")` para que Pyro4 cree una instancia por cada conexión de cliente. En el constructor, `Pyro4.current_context.client_sock_addr` entrega la IP y el puerto del cliente, que se guardan para usarlos en los avisos. Después de la clase, el script crea un `Pyro4.Daemon`, localiza el Name Server, registra la clase en el demonio y publica la URI resultante con el nombre `practica.procesador`. Al final, `daemon.requestLoop()` deja el proceso atendiendo llamadas.
3. Cliente (`cliente.py`). Crea un `Pyro4.Proxy("PYRONAME:practica.procesador")` y lo convierte en asíncrono con `Pyro4.asyncproxy(proxy)`, que modifica el proxy y no devuelve nada. Desde ese momento, cada llamada remota devuelve un future en lugar del resultado. El cliente registra un callback con `futuro.then(al_terminar)`, imprime un contador en un ciclo mientras `futuro.ready` sea falso y, al final, lee `futuro.value`, que contiene el resultado.

Método que expone el servicio:

| Método | Qué hace | Devuelve |
|---|---|---|
| `fibonacci(n)` | Imprime la petición en el servidor, calcula el Fibonacci de `n` con `_fib` e imprime que terminó | El número de Fibonacci de `n` |

Flujo de una operación:

```text
cliente.py  ->  Name Server: "¿dónde está practica.procesador?"
Name Server ->  cliente.py:  URI del objeto en el servidor
cliente.py  ->  servidor.py: fibonacci(35)
cliente.py  <-  future entregado al instante, el cliente sigue ejecutando su ciclo
servidor.py ->  cliente.py:  9227465 (cuando termina el cálculo)
cliente.py:                  se ejecuta al_terminar(9227465) y futuro.ready pasa a True
```

## Capturas de pantalla

Name Server y servidor en ejecución:

<img width="1209" height="370" alt="imagen" src="https://github.com/user-attachments/assets/35753d15-8f0c-442e-b13e-cca284b7390a" />


Cliente con el contador y el callback:

<img width="1209" height="355" alt="imagen" src="https://github.com/user-attachments/assets/4af6c6cc-6bf0-4406-85b8-a8c3a59d09fd" />
