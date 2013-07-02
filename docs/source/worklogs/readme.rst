===========================
Uso de bitácoras de trabajo
===========================


En todos los proyectos de desarrollo de `Merchise` se llevarán bitácoras de
trabajo que servirán de base para calcular los resultados en tiempo.


Nombre de los archivos
======================

En cada una de estas carpetas por proyectos, se irán poniendo las bitácoras
por día con el nombre del fichero usando los siguientes conceptos separados
por guiones ("-"):

- La fecha del día que se reporta en formato «YYYYMMDD»

- El tipo de documento, en este caso «worklog».

- El identificador del desarrollador, por ejemplo «med».

- Opcionalmente palabras claves que pudieran servir de base para búsquedas
  rápidas desde el sistema de ficheros.

Por ejemplo: «**20130702-worklog-med-methodology.rst**»


Estructura de los documentos
============================

Dentro de cada archivo `.RST` se organiza el documento por secciones con la
siguiente estructura por niveles de epígrafes:

- Título: Separado por « / »

  - Nombre formal del Proyecto.

  - Identificador del desarrollador.

  - Fecha en formato ISO.

  Por ejemplo: Xoutil / med / 2013-07-02

- Capítulos: Se definen con el nombre formalizado para los hitos en los
  *Backlogs*.

- Secciones: El nombre que el desarrollador le da a cada tarea, resultado o
  avance específico.


Reportes de tiempo
------------------

Al final de cada una se pone el balance analizado de tiempo para terminar el
hito, resultado o avance que se reporta en el siguiente formato (en una única
línea):

**Time Spent**: «horas en formato decimal»

Se puede emplear también «**Tiempo dedicado**: <horas>»

.. note:

   Este formato se debe respetar para cuando estos ficheros se puedan procesar
   de forma automatizada.
