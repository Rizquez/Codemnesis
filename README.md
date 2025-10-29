# 🤖 AutoDocMind - v.0.0.1

## 🧾 Descripcion del proyecto

**AutoDocMind** es una herramienta que analiza automaticamente repositorios de codigo para generar documentacion clara y util.

Su objetivo es ahorrar tiempo a los desarrolladores creando de forma automatica archivos como el README, diagramas de flujo y explicaciones de cada modulo, sin depender de la redaccion manual.

Combina analisis estatico del codigo con procesamiento de lenguaje natural para ofrecer una vision comprensible del proyecto, sus dependencias y su estructura interna.

## 📑 Contexto

La documentacion tecnica suele quedarse atras frente al ritmo de desarrollo, generando tres problemas comunes: **curvas de entrada altas**, **conocimiento disperso** y **mantenimiento costoso**. Actualizar manualmente READMEs, diagramas y docstrings no escala y termina desincronizado del codigo.

**AutoDocMind** nace para automatizar ese *trabajo invisible*: analiza un repositorio y genera **documentacion explicativa** directamente desde el codigo, describiendo flujos, dependencias, responsabilidades y posibles mejoras.

### ¿Para quien es util?

- **Equipos** que necesitan onboardings rapidos y documentacion viva.  
- **Freelancers o consultoras** que entregan proyectos con README profesionales.  
- **Mantenedores o revisores** que buscan detectar acoplamientos o puntos fragiles.  
- **Portafolios tecnicos** que quieren reflejar arquitectura y decisiones de diseño.

### Ejemplos de uso

- Heredar un proyecto sin documentacion y obtener una **radiografia tecnica inicial**.  
- Preparar una **release** y validar documentacion y dependencias.  
- Realizar **revisiones tecnicas** automatizadas para identificar funciones “magicas” o modulos poco cohesionados.

## 🛠️ Funcionalidades clave

...

## 💽 Instalacion

Clona este repositorio (ssh):
```sh
git clone git@github.com:Rizquez/AutoDocMind.git
```

Accede al directorio del proyecto:
```sh
cd AutoDocMind
```

Crea un entorno de desarrollo utilizando la libreria **virtualenv**:
```sh
virtualenv venv
```

Si no tienes la libreria instalada, puedes ejecutar:
```sh
python -m venv env
```

Activa el entorno de desarrollo:
```sh
venv\Scripts\activate
```

Una vez activado el entorno, instala las dependencias:
```sh
pip install -r requirements.txt
```

## 🚀 Ejecucion

### Consola

Para ejecutar la aplicacion por consola podras utilizar el siguiente comando que se muestra como ejemplo:

```sh
python main.py --lang=... --repo=... --output=...
```

Donde:

- **lang:** Lenguajes de programacion soportados por el algoritmo.
- **repo:** Directorio del respositorio que alberga el proyecto.
- **output (opcional):** Directorio donde se guardaran los archivos generados, de no indicarse, el carpeta donde se almacenran los archivos se creara en la *raiz de este proyecto*.

> [!NOTE]
> Para conocer mas **detalles sobre los parametros y argumentos de ejecucion**, consulta el archivo ubicado en: *handlers/console.py*

## 📂 Estructura del proyecto

Los archivos principales se encuentran organizados en:

```
AutoDocMind/
├── handlers
│   └── console.py
├── helpers
│   ├── loggers.py
│   └── trace.py
├── settings
│   ├── algorithm.py
│   └── constants.py
├── .gitignore
├── LICENSE
├── main.py
├── README.md
└── requirements.txt
```

## 🎯 Consideraciones adicionales para desarrolladores

### Forward References (PEP 484)

El proyecto utiliza `Forward References` segun la `PEP 484`. Mediante el uso de `TYPE_CHECKING`, la importacion de una clase se realiza unicamente en tiempo de chequeo estatico de tipos (por ejemplo, con `mypy`). Durante la ejecucion, `TYPE_CHECKING` evalua como `False`, evitando la importacion real. Esto optimiza el rendimiento y permite referencias adelantadas a clases.

Ejemplo:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import MyFirstClass

class MySecondClass:
    def do_something(self, first: 'MyFirstClass') -> None:
        pass
```

### Convencion para atributos y metodos privados (Name mangling)

En Python, no existe una verdadera encapsulacion como en otros lenguajes (Java, C++), pero se puede simular mediante convenciones. En este proyecto, se utiliza el mecanismo conocido como `Name Mangling` para nombrar atributos y metodos privados, lo cual implica el uso de doble guion bajo (__) al inicio del nombre.

Este mecanismo no solo indica la intencion de mantener estos elementos como privados, sino que Python modifica internamente sus nombres para evitar colisiones, especialmente en clases heredadas.

¿Como funciona? Cuando se define un atributo como `__mi_atributo` dentro de una clase, Python lo convierte internamente a `_NombreClase__mi_atributo`, dificultando el acceso externo accidental o no deseado.

Ejemplo:

```python
class Motor:
    def __init__(self):
        self.__estado = "apagado"

    def encender(self):
        self.__estado = "encendido"

    def estado(self):
        return self.__estado

m = Motor()
print(m.estado())          # ✔️ Salida: encendido
print(m.__estado)          # ❌ Error: AttributeError
print(m._Motor__estado)    # ✔️ Acceso posible, pero no recomendado (Salida: encendido)
```
> [!WARNING]
> Aunque tecnicamente es accesible mediante el nombre mangled, su uso directo esta desaconsejado fuera del contexto de la propia clase.

## 📖 Documentacion adicional

...

## 🔒 Licencia

Este proyecto esta bajo la licencia `MIT`, lo que permite su uso, distribucion y modificacion con las condiciones especificadas en el archivo `LICENSE`.

## ⚙ Contacto, soporte y desarrollo

- Pedro Rizquez: pedro.rizquez.94@hotmail.com