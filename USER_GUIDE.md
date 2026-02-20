# Olympus Smart Gov - Guía de Usuario Detallada 🏛️

Bienvenido a la plataforma de gestión administrativa inteligente de **Olympus Tech**. Este manual le guiará a través de las funcionalidades clave del sistema.

## 1. Acceso y Seguridad (SSO)
La plataforma utiliza **Keycloak** para garantizar la máxima seguridad y Single Sign-On (SSO).

1.  **Acceso:** Diríjase a `http://localhost:3000`.
2.  **Inicio de Sesión:** Será redirigido automáticamente al portal de identidad.
    *   **Usuario de Prueba:** `funcionario1`
    *   **Contraseña:** `password123`
3.  **Cierre de Sesión:** Utilice el botón "Logout" en la barra de navegación para finalizar su sesión de forma segura.

## 2. Gestión de Expedientes Administrativos
El núcleo del sistema es la gestión de trámites (Expedientes).

### 2.1. Crear un Expediente
1.  En el menú principal, haga clic en **Expedientes**.
2.  Pulse el botón **"Nuevo Expediente"**.
3.  Asigne un **Número de Expediente** único y un **Asunto**.
4.  El sistema asignará automáticamente su usuario como responsable.

### 2.2. Motor de Tramitación (Workflows)
Dentro del detalle de cada expediente, encontrará el motor de flujos:
*   **Iniciar Trámite:** Haga clic en "Iniciar Tramitación" para pasar de estado `ABIERTO` a `EN_PROCESO`.
*   **Gestión de Pasos:** En la pestaña **"Pasos"**, verá la secuencia de tareas.
    *   Haga clic en **"Marcar como completado"** al finalizar cada tarea.
    *   El sistema registrará automáticamente la fecha y hora de finalización.
    *   Al completar el último paso, el expediente se cerrará automáticamente (`CERRADO`).

## 3. Gestión Documental e Inteligencia Artificial
### 3.1. Subida y OCR Automático
1.  Vaya a la pestaña **"Documentos"** de un expediente.
2.  Haga clic en **"Subir Documento"** y seleccione un archivo **PDF**.
3.  **Análisis IA:** El sistema extraerá automáticamente el texto y generará metadatos (Emisor, Fecha, Montos, Resumen) mediante el modelo de IA local (Ollama). Verá estos datos en un recuadro azul bajo el nombre del archivo.

### 3.2. Firma Digital Inmutable
1.  Si un documento está "Pendiente de firma", aparecerá un botón **"Firmar Digitalmente"**.
2.  Introduzca su nombre o cargo.
3.  El sistema generará un **Hash SHA-256** único que garantiza que el documento no ha sido alterado. Esta firma es visible y queda registrada en el historial de trazabilidad.

## 4. Control Económico-Financiero
### 4.1. Presupuestos
*   En la sección **"Presupuestos"**, podrá ver el estado de las partidas:
    *   **Presupuestado:** Dinero total asignado.
    *   **Comprometido:** Gasto reservado para expedientes en trámite.
    *   **Pagado:** Gasto real ejecutado.
    *   **Disponible:** Crédito real restante.

### 4.2. Registro de Facturas
1.  Dentro de un expediente, vaya a la pestaña **"Finanzas"**.
2.  Haga clic en **"+ Registrar Factura"**.
3.  El sistema asociará la factura al expediente y actualizará la ejecución presupuestaria.

## 5. Asistente IA ✨ (Búsqueda Semántica y RAG)
Esta es la funcionalidad más avanzada de la plataforma, accesible desde el menú **"Asistente IA"**.

*   **Búsqueda Semántica:** No busque solo por palabras; busque por significado. (Ej: "Documentos sobre construcción en el norte").
*   **Preguntas al Asistente (RAG):** Puede preguntar directamente sobre sus expedientes.
    *   *Ejemplo:* "¿Qué facturas tenemos pendientes de pago?"
    *   La IA buscará en todos sus documentos, encontrará la información relevante y le responderá citando las fuentes utilizadas.

## 6. Auditoría y Trazabilidad
En la pestaña **"Trazabilidad"** de cada expediente, podrá consultar un historial inmutable de:
*   Quién inició el trámite.
*   Cuándo se completó cada paso.
*   Quién firmó cada documento.
*   Registros de auditoría de la IA.

---

**Nota:** Para cualquier incidencia técnica, contacte con el equipo de soporte de **Olympus Tech**.
