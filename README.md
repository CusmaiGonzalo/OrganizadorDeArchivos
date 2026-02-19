ORGANIZADOR DE ARCHIVOS

Este es un proyecto de software de uso libre.
La idea es aplicar Automatización con python utilizando una interfaz gráfica amigable al usuario.
Dentro de este proyecto se utilizo:
  - Python
  - PyQt6
  - SQLite

Todo esto en conjunto nos permite realizar un programa  para organizar archivos en cualquier pc y en cualquier carpeta donde se desee.

*INSTRUCCIONES*

1- Seleccionar la carpeta donde se desea realizar la organización.
2- Presionar el botonn de Ordenar para organizar los archivos en nuevas o ya creadas carpetas que aparecen en la caja superior al boton.

*HERRAMIENTAS*

En la seccion de herramientas tenemos una ventana para gestionar que carpetas queremos que se utilizen para organizar los archivos.
Tenemos la opcion de crear, borrar o editar las carpetas con nombres y extenciones a gusto del usuario.
Se recomienda revisar esta sección antes de proceder con el ordenado.

*CATEGORIAS POR DEFECTO*

En caso de no modificar las carpetas a utilizar, las carpetas que utilizara por defecto son:
("Documentos PDF",       [".pdf"],                          True),
("Documentos Word",      [".doc", ".docx"],                 True),
("Hojas de Cálculo",     [".xls", ".xlsx"],                 True),
("Presentaciones",       [".ppt", ".pptx"],                 True),
("Imágenes",             [".jpg", ".jpeg", ".png", ".gif"], True),
("Videos",               [".mp4", ".avi", ".mkv"],          True),
("Audio",                [".mp3", ".wav", ".aac"],          True),
("Archivos Comprimidos", [".zip", ".rar", ".7z"],           True),
("Código Fuente",        [".py", ".java", ".cpp", ".js"],   True),
("Ejecutables",          [".exe", ".msi"],                  True),
("Otros",                [],                                True),

En la primera columna definimos el nombre de las carpetas, en la segunda las extenciones que guardaran las mismas, y en la tercera si se utilizaran o no (por defecto es si).

Proyecto realizado por: Gonzalo Cusmai
Libre de uso y modificación
