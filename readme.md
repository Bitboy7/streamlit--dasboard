# Sistema de Gestión de Gastos

Este proyecto es un sistema de gestión de gastos desarrollado con Streamlit, diseñado para facilitar el seguimiento y control de los gastos e ingresos en una empresa agrícola. Permite a los usuarios ingresar, visualizar, y gestionar pagos a productores, gastos generales, y generar reportes detallados.

## Características

- **Gestión de Pagos a Productores**: Permite ingresar y visualizar los pagos realizados a los productores, incluyendo detalles como el productor, el estado del pago, la fecha, y el monto.
- **Gestión de Gastos Generales**: Facilita el registro y seguimiento de los gastos generales de la empresa.
- **Generación de Reportes**: Ofrece la capacidad de generar reportes detallados sobre los gastos e ingresos, permitiendo una mejor toma de decisiones.
- **Catálogo de Clientes**: Gestiona un catálogo de clientes, incluyendo operaciones como inserción y eliminación de clientes.
## Tecnologías Utilizadas

- <img src="https://yt3.googleusercontent.com/ytc/AIdro_m3Dbjaq8CDkal5bP6rJ-IRDj2JTH5OlWM9-HAAWbeym0I=s900-c-k-c0x00ffffff-no-rj" alt="Python" width="20" height="20"> **Streamlit**: Para la creación de la interfaz de usuario y la interacción con el sistema.
- <i class="fab fa-python"></i> **Pandas y Plotly**: Para el manejo de datos y la generación de gráficos.
- <i class="fab fa-python"></i> **Python**: Lenguaje de programación utilizado para el desarrollo del backend.

![Pandas](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRXCDD7q7wCVdRNtROzgtARnDThPmab6k2x7Q&s)
![Plotly](https://upload.wikimedia.org/wikipedia/commons/8/8a/Plotly-logo.png)
![Python](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ1N0T5J0KTvMHIjtWt-wFzZWCaCScrYLpkeg&s)

<div style="background-color: #f2f2f2; padding: 10px;">
    <i class="fas fa-info-circle"></i> **Nota**: Para personalizar el diseño de la interfaz de usuario, puedes utilizar CSS y aplicar estilos a los elementos HTML.
</div>

## Estructura del Proyecto

El proyecto está organizado en varias carpetas y archivos clave:

- `app.py`: Punto de entrada principal de la aplicación Streamlit.
- `views/`: Contiene los módulos de Python para cada una de las páginas de la aplicación (Catálogo, Pagos a productores, Gastos generales, Reportes).
- `models/`: Define la lógica para interactuar con la base de datos.
- `helpers/`: Incluye funciones de ayuda para tareas comunes como la carga de estilos CSS.
- `static/`: Almacena archivos estáticos como imágenes y CSS.
- `.streamlit/pages.toml`: Configuración de las páginas de Streamlit.

## Instalación

Para ejecutar este proyecto, asegúrate de tener instalado Python y Streamlit. Luego, sigue estos pasos:

1. Clona este repositorio.
2. Instala las dependencias utilizando `pip install -r requirements.txt`.
3. Ejecuta el proyecto con `streamlit run app.py`.

## Contribuir

Si deseas contribuir a este proyecto, por favor, considera forkear el repositorio y enviar tus pull requests. Todas las contribuciones son bienvenidas.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.