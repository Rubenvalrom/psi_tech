# RFP: Hackathon "Olympus Smart Gov" - Plataforma Inteligente de Gestión Administrativa

**Olympus Tech**  
Innovando para el Norte.

## 1. Introducción y Contexto

Olympus Tech es una empresa pública de servicios tecnológicos que da soporte a diversos organismos gubernamentales en el norte de España. Nuestra misión es liderar la transformación digital del sector público, mejorando la eficiencia operativa y la experiencia del ciudadano a través de la innovación constante.

En el marco de nuestra estrategia **"Norte Digital 2030"**, lanzamos esta Hackathon para identificar la mejor solución tecnológica que integre la gestión de expedientes administrativos con una gestión económico-financiera moderna, impulsada por Inteligencia Artificial.

## 2. Objeto del Reto

El objetivo es el diseño, desarrollo y prototipado de una **Plataforma Inteligente e Integral de Expedientes Administrativos y Gestión Económico-Financiera**.

La solución debe ser capaz de:

1. **Tramitación Inteligente**: Automatizar y optimizar flujos de trabajo administrativos.
2. **Gestión Financiera**: Integrar el control presupuestario y contable.
3. **Capas Cognitivas**: Aplicar IA para la toma de decisiones, extracción de datos y asistencia al usuario.

## 3. Requisitos Técnicos (Stack Tecnológico Obligatorio)

Para garantizar la soberanía tecnológica y la escalabilidad, Olympus Tech requiere que la solución se base **exclusivamente** en tecnologías **Open Source**:

- **Base de Datos Relacional y Vectorial**: PostgreSQL con extensión **pgvector** para el almacenamiento de metadatos y embeddings.
- **Inteligencia Artificial (LLM)**: Orquestación mediante **Ollama** para la ejecución de modelos de lenguaje locales (ej. Llama 3, Mistral) que garanticen la privacidad de los datos.
- **Gestión de Identidad y Acceso (IAM)**: Implementación de **Keycloak** para la autenticación única (SSO) y control de acceso basado en roles (RBAC).
- **Backend**: Preferiblemente tecnologías basadas en  
  - Java (**Spring Boot**)  
  - o Python (**FastAPI** / **Django**).
- **Frontend**: Frameworks modernos como **React** o **Angular**, con diseño responsive y accesibilidad **WCAG 2.1**.
- **Despliegue**: Contenerización mediante **Docker** / **Kubernetes**.

## 4. Requerimientos Funcionales

La propuesta debe cubrir los siguientes módulos (equivalentes a los requisitos operativos de Olympus Tech):

### 4.1. Módulo de Tramitación Inteligente [TRA]

- Gestor de expedientes con capacidad de versionado de documentos.
- Motor de flujos (**BPMN**) para la automatización de pasos administrativos.
- Firma electrónica integrada y sellado de tiempo.

### 4.2. Módulo Económico-Financiero [ECO]

- Gestión de partidas presupuestarias y ejecución del gasto.
- Integración de facturación electrónica.
- Control de contabilidad pública y generación de informes oficiales.

### 4.3. Inteligencia Artificial Aplicada [IA]

- **Auto-rellenado**: Extracción automática de metadatos de documentos escaneados (OCR + IA).
- **Asistente Virtual**: Copiloto para funcionarios que recomiende el siguiente trámite o artículo legal aplicable.
- **Analítica Predictiva**: Detección de cuellos de botella en la tramitación y previsión de ingresos/gastos.

## 5. Entregables Obligatorios

Las empresas participantes deberán entregar los siguientes elementos bajo su propio **branding corporativo**:

1. **Repositorio de Código**  
   Enlace a GitHub/GitLab con:  
   - Código fuente completo  
   - Archivos de configuración (Docker Compose)  
   - Archivo **README.md** detallado para el despliegue

2. **Oferta Técnica (PDF)**  
   Documento formal con una extensión máxima de **15 páginas** que incluya:  
   - Arquitectura de la solución  
   - Plan de implantación y metodología (**Agile**)  
   - Estrategia de gestión del cambio y formación  
   - Detalle de los casos de uso de IA implementados

3. **Presentación Ejecutiva (PDF)**  
   Máximo **10 diapositivas** que resuman la propuesta de valor y las ventajas competitivas.

4. **Vídeo Demostrativo**  
   Un clip de máximo **1 minuto (60 segundos)** mostrando las funcionalidades clave de la plataforma y la interfaz de usuario.

## 6. Criterios de Evaluación

Las ofertas serán evaluadas según los siguientes pesos:

| Criterio                                                      | Peso   |
|---------------------------------------------------------------|--------|
| Calidad Técnica y Arquitectura: Uso correcto del stack Open Source y robustez del sistema | 30%    |
| Funcionalidad e Innovación IA: Valor aportado por los casos de uso de IA y automatización | 30%    |
| Experiencia de Usuario (UX/UI): Facilidad de uso y diseño orientado al empleado público | 30%    |
| Calidad de los Entregables: Claridad en la oferta, presentación y vídeo | 10%    |

## 7. Propiedad Intelectual

Al tratarse de una solución para Olympus Tech basada en Open Source, el código resultante deberá ser entregado bajo licencia **Apache 2.0** o **MIT**, permitiendo a la empresa pública su evolución y mantenimiento futuro.

---

**Olympus Tech**  
Innovando para el Norte.