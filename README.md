# Fase-4-Componente-practico-Practicas-simuladas
# Sistema Integral de Gestión de Clientes, Servicios y Reservas (Software FJ)

Aplicación desarrollada en **Python** basada en Programación Orientada a Objetos (POO), diseñada para gestionar clientes, servicios y reservas empresariales de forma modular, extensible y sin utilizar bases de datos.

##  Integrantes del Equipo
* Nicol Alexandra Calderin Avila
* Juan Sebastian Cardenas Guerrero
* Alexander Daniel Cuadro Pallares 
* Osnayder Perez Molina
* Jeffrey Salazar Contreras

##  Características Principales
* **Arquitectura POO:** Uso de clases abstractas (`EntidadSistema`, `Servicio`), herencia, polimorfismo y encapsulación con validaciones mediante propiedades (`@property`).
* **Manejo Avanzado de Excepciones:** Excepciones personalizadas, bloques `try/except/else/finally` y encadenamiento de excepciones (`from e`).
* **Sistema de Logs:** Registro automático de eventos, advertencias y errores en un archivo físico (`sistema_eventos.log`) en lugar de bases de datos.
* **Simulación de Operaciones:** Ejecución automática de múltiples escenarios válidos e inválidos para demostrar la estabilidad de la aplicación.

##  Cómo Ejecutar el Programa
1. Clona este repositorio o descarga los archivos en tu computadora.
2. Abre una terminal en la carpeta raíz del proyecto.
3. Ejecuta el archivo principal con el siguiente comando:
   ```bash
   python sistema_reservas.py