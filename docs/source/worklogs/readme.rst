===========================
Uso de bitácoras de trabajo
===========================

Existe un repositorio llamadado ``worklogs`` donde cada persona deberá llevar
sus bitácoras de trabajo en todos los proyectos, las que usarán para calcular
los resultados en tiempo.


Estructura del repositorio y nombre de los archivos
===================================================

Este repositorio tendrá la estructura de un proyecto de Sphinx. En la carpeta
``source/current``, se pondrán las :term:`bitácoras de trabajo actual
<bitácora de trabajo actual>`. En la carpeta ``source/archives`` se
archivarán las bitácoras que ya hayan sido procesadas. Los detalles del flujo
de trabajo se explican :ref:`más abajo <flujo-de-trabajo>`.

Cada bitácora de trabajo se crea en un rama particular del desarrollador como
explica en el :ref:`flujo <flujo-de-trabajo>`, y en la carpeta
``source/current``, se irán poniendo las bitácoras por día con el nombre del
fichero usando los siguientes conceptos separados por guiones ("-"):

- La fecha del día que se reporta en formato «YYYYMMDD».

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
línea)::

    .. dedicated time:: «horas en formato decimal»

Ejemplos::

    .. dedicated time:: 4:15
    .. dedicated time:: 4h 15min

Se pueden expresar valores negativos con el objetivo de corregir resultados
que se hayan reportando pero que en análisis posteriores se plantee que las
tareas o avances merecían menos tiempo::

    .. dedicated time:: -1h



.. todo:: Voy trabajar un poco en el ``xit`` para esto. Para ponerlo en los
	  commits y generar backlogs automáticos.

.. _flujo-de-trabajo:

Uso de GIT y los reportes de trabajo
====================================

Cada bitácora y reporte de tiempo se comienza en una rama cuyo nombre es el
nombre del desarrollador, por ejemplo «manu». Los reportes de tiempo se
consideran efectivos *cuando se mezclan para la rama* «develop».

Por lo tanto, se sugiere el siguiente flujo de trabajo:

- Comenzar la bitácora de trabajo

.. note:

   Este formato se debe respetar para cuando estos ficheros se puedan procesar
   de forma automatizada.
