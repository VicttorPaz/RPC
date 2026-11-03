# Calculadora Remota Básica

Calculadora de cuatro operaciones (suma, resta, multiplicación y división) en la que las operaciones se ejecutan en un servidor y el cliente las invoca de forma remota con Pyro4.

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

Este proyecto es una práctica de sistemas distribuidos que muestra cómo dos programas separados pueden comunicarse mediante llamadas a métodos remotos. El servidor guarda una clase `Calculadora` con las cuatro operaciones básicas, y el cliente le pide al usuario dos números enteros y una operación, y envía la petición al servidor para mostrar el resultado en pantalla.

Para que el cliente encuentre al servidor sin conocer su dirección, ambos usan el Name Server de Pyro4, que funciona como una agenda de nombres. El servidor se anota ahí como `Calculadora` y el cliente lo busca por ese nombre. Con esto se practican tres ideas: exponer una clase para uso remoto, registrar un servicio por nombre y consumirlo desde otro proceso.

## Características

- Cuatro operaciones: suma, resta, multiplicación y división.
- La lógica de cálculo vive en el servidor, en la clase `Calculadora`, y el cliente la usa como si fuera un objeto local.
- El servidor se registra en el Name Server de Pyro4 con el nombre `Calculadora`, así que el cliente lo encuentra por nombre y no necesita conocer su dirección.
- El cliente valida que los dos números sean enteros y vuelve a preguntar si el usuario escribe letras u otros caracteres.
- La división entre cero devuelve un mensaje de error y no detiene el servidor.

## Requisitos previos

- Python 3
- pip
- Pyro4

Tanto el servidor como el cliente necesitan tener Pyro4 instalado. Si se ejecutan en equipos distintos dentro de la misma red, ambos deben poder alcanzar al Name Server.

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

Se necesitan tres terminales abiertas, una para cada proceso. El orden importa: primero el Name Server, después el servidor y al final el cliente.

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

Deja esta terminal abierta mientras uses la calculadora.

### 2. Iniciar el servidor

```bash
python servidor.py
```

Salida esperada:

```text
Servidor local listo.
```

El servidor queda esperando peticiones. Tampoco debes cerrar esta terminal.

### 3. Ejecutar el cliente

```bash
python cliente.py
```

Ejemplo de ejecución con una suma:

```text
Primer número: 12
Segundo número: 8
Operación (+, -, *, /): +
20
```

Ejemplo con una división:

```text
Primer número: 15
Segundo número: 4
Operación (+, -, *, /): /
3.75
```

Ejemplo de división entre cero:

```text
Primer número: 9
Segundo número: 0
Operación (+, -, *, /): /
Error: no se puede dividir entre cero
```

Ejemplo de entrada inválida, donde el cliente vuelve a pedir el dato:

```text
Primer número: abc
Error: Solo se permiten números enteros.
Primer número: 7
Segundo número: 3
Operación (+, -, *, /): *
21
```

## Cómo funciona

El proyecto usa Pyro4 (Python Remote Objects), una biblioteca que permite llamar métodos de un objeto que vive en otro proceso, o incluso en otro equipo, como si fuera local. Hay tres piezas:

1. Name Server. Es un directorio que relaciona nombres con direcciones de objetos remotos. Se inicia con `python -m Pyro4.naming` y escucha por defecto en el puerto 9090.
2. Servidor (`servidor.py`). Define la clase `Calculadora` con los métodos `sumar`, `restar`, `multiplicar` y `dividir`. El decorador `@Pyro4.expose` marca la clase como accesible desde fuera. Después crea un `Pyro4.Daemon`, registra la clase en él, obtiene su URI y la publica en el Name Server con el nombre `Calculadora`. Por último, `daemon.requestLoop()` deja el proceso atendiendo llamadas.
3. Cliente (`cliente.py`). Crea un `Pyro4.Proxy("PYRONAME:Calculadora")`, un objeto intermediario que consulta al Name Server la dirección real y reenvía cada llamada al servidor. Antes de operar, pide dos números enteros con validación por `try/except` y pide el símbolo de la operación.

Flujo de una operación:

```text
cliente.py  ->  Name Server: "¿dónde está Calculadora?"
Name Server ->  cliente.py:  URI del objeto en el servidor
cliente.py  ->  servidor.py: calculadora.sumar(12, 8)
servidor.py ->  cliente.py:  20
```

La división devuelve un número decimal. Cuando el divisor es cero, el método devuelve un texto de error en lugar de lanzar una excepción, así que el cliente lo imprime tal cual.


## Capturas de pantalla

Name Server y servidor en ejecución:

<img width="775" height="385" alt="imagen" src="https://github.com/user-attachments/assets/e7fc07ac-b03f-4530-9f1c-2def2d4be8a9" />


Cliente realizando operaciones:


<img width="379" height="385" alt="imagen" src="https://github.com/user-attachments/assets/e2121504-cbc4-4cd1-8d84-ebceebb2d19a" />


