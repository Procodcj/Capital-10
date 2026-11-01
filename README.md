# Capital 10

Aplicación de escritorio para la gestión, registro y seguimiento de hábitos de lectura personal, desarrollada en Python con una interfaz gráfica basada en CustomTkinter y persistencia de datos local en SQLite.

---

## Características

- **Gestión de biblioteca:** Registro de libros con título, autor, páginas totales, formato y estado de lectura.
- **Seguimiento de avance:** Registro cronológico de sesiones de lectura y cálculo de porcentajes.
- **Notas y reflexiones:** Bitácora integrada para guardar citas, ideas clave y comentarios por título.
- **Exportación de reportes:** Generación de resúmenes de lectura en formato PDF.
- **Privacidad total:** Los datos se almacenan exclusivamente de forma local en la máquina del usuario (`capital10.db`).

---

## Instalación y uso (Ejecutable para Windows)

No se requiere tener Python instalado para usar la aplicación terminada:

1. Ve a la sección de [Releases](https://github.com/Procodcj/Capital-10/releases) en este repositorio.
2. Descarga el archivo comprimido más reciente (`Capital 10.zip`).
3. Extrae la carpeta completa en la ubicación de tu preferencia.
4. Ejecuta el archivo `Capital 10.exe`.

> **Nota para actualización de versión:** Si ya usabas la aplicación y quieres conservar tus libros y notas, copia tu archivo existente `capital10.db` y pégalo dentro de la nueva carpeta descomprimida, al lado de `Capital 10.exe`, antes de abrirlo.

---

## Ejecución en entorno de desarrollo

Para clonar y ejecutar el código fuente directamente desde la terminal:

### Prerrequisitos

- Python 3.10 o superior
- Git

### Pasos

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/Procodcj/Capital-10.git](https://github.com/Procodcj/Capital-10.git)
   cd Capital-10
   ```

2. Crear y activar un entorno virtual:
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install customtkinter pillow reportlab
   ```

4. Iniciar la aplicación:
   ```bash
   python main.py
   ```

---

## Estructura del proyecto

```text
Capital 10/
├── base_datos/        # Configuración de SQLite, esquema y migraciones
├── modulos/           # Módulos de interfaz, lógica de vistas y navegación
├── LICENSE            # Licencia MIT
├── main.py            # Punto de entrada de la aplicación
├── README.md          # Documentación del proyecto
└── .gitignore         # Exclusiones de Git
```

---

## Licencia

Distribuido bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.