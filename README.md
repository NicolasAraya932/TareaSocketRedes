Tarea Realizada con : [Bastián Rubio](https://github.com/Zb4sty)

Un chat online es un método de comunicación digital vía Internet que realiza intercambio de mensajes de forma instantánea, enviando mensajes de texto entre un emisor a un receptor, generalmente
mediante un servidor. Es quizá la aplicación más conocida de los sockets TCP/IP.
El objetivo de esta tarea es implementar un chat para granjeros de Stardew Fridi a través del cual, además de poder conversar, se puedan intercambiar artefactos coleccionables, 
así como consultar los artefactos que cada granjero tiene. Este chat debe seguir la arquitectura cliente-servidor

## Pasos para ejecutar la tarea
1) Ejecute el servidor que está en el archivo main.py
2) Para cada cliente ejecute client.py

## Guía de comandos implementados:

• **:help or :h or :?** 
  - Permite ver los comandos disponibles.

• **:q** 
  - Permite que el usuario se desconecte del chat.
    
• **:p <Identificador> <Mensaje>**
  - Envía un mensaje privado al usuario. Este mensaje sólo debe ser recibido por este usuario, y desplegado en su chat. Ejemplo, `:p nombre_granjero_conectado mensaje`, otro ejemplo `:p fulanito Hola, Como estas?`
             
• **:u** 
  - Muestra los usuarios que se encuentran conectados actualmente al chat.
     
• **:smile** 
  - Envía la carita feliz :) a los demás usuarios conectados.
     
• **:angry** 
  - Envía la carita enojada >:( a los demás usuarios conectados. 

• **:combito** 
  - Envía un emoticón bélico Q(’- ’Q) a los demás usuarios conectados. 

• **:larva** 
  - Envía una Larva (:o)OOOooo a los demás usuarios conectados.
    
• **:artefactos**
  - Entrega una lista de los artefactos que el usuario tiene en su cuenta. Esta información solo es visible para quien envía el comando.

• **:artefacto <ArtefactoId>**
  - Obtiene el nombre del artefacto identificado por ArtefactoId. Ejemplo, `:artefacto 22` es respondido por el servidor con Trocitos de cristal. (Esta información solo es visible para quien envía el comando.)

• **:offer <Identificador> <MiArtefactoId> <SuArtefactoId>**
  - Este comando inicia un intercambio con el usuario <Identificador>. A este usuario se le ofrece <MiArtefactoId> a cambio de <SuArtefactoId>. Ejemplo, `:offer Gus 32 12` equivale a querer intercambiar una Espuela prehistórica por el Disco raro de Gus

• **:accept**
  - Acepta la oferta recibida y realiza el intercambio de artefactos, actualizando las listas de artefactos de cada usuario involucrado. En ambos chats se muestra ¡Intercambio realizado!

• **:reject**
  - Rechaza la oferta. En ambos chats involucrados se muestra Intercambio rechazado.

El listado de objetos disponibles se encuentra en  artefactos.JSON
