# Workflow Definition Format

## Simple Linear Workflow

```json
{
  "id": "solicitud_licencia",
  "name": "Solicitud de Licencia",
  "description": "Workflow para solicitud y aprobación de licencias",
  "pasos": [
    {
      "id": "paso_1",
      "numero": 1,
      "nombre": "Registro Solicitud",
      "descripcion": "Usuario registra solicitud",
      "tipo": "sistema",
      "duracion_estimada_dias": 1,
      "siguiente": "paso_2"
    },
    {
      "id": "paso_2",
      "numero": 2,
      "nombre": "Validación Documentos",
      "descripcion": "Se validan documentos requeridos",
      "tipo": "validacion",
      "documentos_requeridos": ["certificado", "planos", "presupuesto"],
      "duracion_estimada_dias": 3,
      "siguiente": "paso_3"
    },
    {
      "id": "paso_3",
      "numero": 3,
      "nombre": "Evaluación Técnica",
      "tipo": "evaluacion",
      "asignado_a_rol": "TECNICO",
      "siguiente": "paso_4"
    },
    {
      "id": "paso_4",
      "numero": 4,
      "nombre": "Aprobación",
      "tipo": "aprobacion",
      "asignado_a_rol": "DIRECTOR",
      "siguiente": None
    }
  ]
}
```

## Conditional Workflows

```json
{
  "pasos": [
    {
      "id": "validar",
      "nombre": "Validar",
      "siguiente_si_valido": "aprobacion",
      "siguiente_si_invalido": "rechazo"
    },
    {
      "id": "aprobacion",
      "nombre": "Aprobación"
    },
    {
      "id": "rechazo",
      "nombre": "Rechazo"
    }
  ]
}
```

## Step Types

| Tipo | Descripción | Requerimientos |
|------|------------|-----------------|
| `sistema` | Acción automática | handler Python |
| `validacion` | Validar documentos/datos | reglas de negocio |
| `evaluacion` | Revisión manual | asignado a rol |
| `aprobacion` | Aprobación final | firma digital |
| `notificacion` | Enviar notificación | template email |
