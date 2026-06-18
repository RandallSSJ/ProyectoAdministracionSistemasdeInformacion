SISMOS es un sistema de información desarrollado para la consulta, procesamiento y visualización de datos relacionados con eventos sísmicos. La aplicación permite obtener información de sismos mediante el consumo de una API externa, procesar los datos obtenidos y mostrarlos al usuario de una forma organizada, facilitando la consulta de información como magnitud, ubicación, fecha, profundidad y coordenadas geográficas.

El proyecto fue desarrollado utilizando una Arquitectura Hexagonal, también conocida como arquitectura de puertos y adaptadores, con el objetivo de separar la lógica principal del sistema de los componentes externos como APIs e interfaces gráficas. Esta arquitectura permite que la aplicación sea más organizada, flexible y fácil de mantener, ya que cada parte del sistema tiene una responsabilidad específica.

La lógica del sistema se basa en obtener información desde una fuente externa, procesarla y presentarla al usuario. La capa de infraestructura se encarga de comunicarse con la API sísmica para obtener los datos, la capa de aplicación administra el flujo de información y la capa de presentación, desarrollada con Streamlit, permite mostrar los resultados mediante una interfaz sencilla e interactiva.

La arquitectura implementada permite que el sistema pueda crecer en el futuro agregando nuevas funcionalidades como almacenamiento en bases de datos, generación de reportes, gráficos o integración con nuevas fuentes de información sin modificar completamente la estructura del proyecto.

Para el desarrollo de SISMOS1 se utilizó Python como lenguaje principal, Streamlit para la creación de la interfaz y Git junto con GitHub para el control de versiones y administración del código fuente. El uso de estas tecnologías permite construir una aplicación organizada y preparada para futuras mejoras.






SISMOS es un proyecto enfocado en la creación de un sistema capaz de gestionar y mostrar información relacionada con fenómenos sísmicos de una manera eficiente y accesible. La aplicación permite obtener datos provenientes de fuentes externas y convertirlos en información útil para el usuario, facilitando la consulta de eventos sísmicos y permitiendo visualizar los registros de una forma más ordenada. El sistema busca mejorar la manera en que se presenta la información, evitando que el usuario tenga que interpretar datos sin procesar directamente desde una fuente externa.

El propósito principal del proyecto es aplicar conocimientos de desarrollo de software para construir una solución organizada que permita manejar datos dinámicos y trabajar con servicios externos. Mediante el uso de una API, el sistema puede obtener información actualizada sobre sismos y utilizar estos datos dentro de la aplicación para generar una experiencia más sencilla y comprensible para el usuario.

La aplicación utiliza una estructura basada en una arquitectura hexagonal, lo que permite que los diferentes componentes del sistema trabajen de manera independiente. Esta organización ayuda a que el proyecto tenga una mejor distribución de responsabilidades, donde cada módulo cumple una función específica y evita que todo el código se encuentre concentrado en una sola parte de la aplicación.

La lógica del sistema se enfoca en recibir información, analizarla y transformarla antes de ser presentada. Los datos obtenidos pasan por un proceso donde se organizan los valores necesarios para que puedan ser utilizados correctamente dentro de la aplicación. Esto permite que la información final sea más clara y útil, mejorando la interacción del usuario con el sistema.

Una de las ventajas principales del proyecto es que su estructura permite realizar modificaciones y ampliaciones con mayor facilidad. Al mantener separadas las funciones del sistema, es posible agregar nuevas herramientas o mejorar procesos existentes sin afectar completamente el funcionamiento actual de la aplicación.

SISMOS representa una aplicación orientada al análisis y manejo de información sísmica, aplicando principios de diseño que buscan crear software más ordenado y preparado para futuras mejoras. El proyecto demuestra la importancia de utilizar arquitecturas adecuadas para desarrollar sistemas que puedan mantenerse, evolucionar y adaptarse a nuevas necesidades.
