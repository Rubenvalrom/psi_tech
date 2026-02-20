import { z } from "zod";

// Expediente schemas
export const expedienteSchema = z.object({
  id: z.number(),
  numero: z.string(),
  asunto: z.string(),
  estado: z.enum(["ABIERTO", "EN_PROCESO", "CERRADO"]),
  responsable_id: z.number().optional().nullable(),
  fecha_creacion: z.string().datetime().or(z.string()),
  fecha_actualizacion: z.string().datetime().or(z.string()),
  documentos: z.array(z.object({
    id: z.number(),
    nombre: z.string(),
    tipo: z.string(),
    hash_firma: z.string().optional().nullable(),
    firmado_por: z.string().optional().nullable(),
    metadatos_extraidos: z.string().optional().nullable(),
  })).optional().nullable(),
});

export const expedienteListSchema = z.object({
  items: z.array(expedienteSchema),
  total: z.number(),
});

// Paso (step) schemas
export const pasoSchema = z.object({
  id: z.number(),
  numero_paso: z.number(),
  titulo: z.string(),
  descripcion: z.string(),
  estado: z.enum(["PENDIENTE", "EN_PROGRESO", "COMPLETADO"]),
  datetime_fin: z.string().datetime().or(z.string()).optional().nullable(),
});

// Trazabilidad schema
export const trazabilidadSchema = z.object({
  id: z.number(),
  accion: z.string(),
  descripcion: z.string(),
  timestamp: z.string().datetime().or(z.string()),
});

// Factura schema
export const facturaSchema = z.object({
  id: z.number(),
  numero: z.string(),
  proveedor: z.string(),
  fecha_emision: z.string().datetime().or(z.string()),
  monto: z.number(),
  estado: z.enum(["PENDIENTE", "PAGADA"]),
});

// AI/Search schemas
export const aiAnswerSchema = z.object({
  answer: z.string(),
  sources: z.array(z.object({
    id: z.number(),
    nombre: z.string(),
    expediente_id: z.number(),
  })).optional().default([]),
});

export const semanticSearchResultSchema = z.object({
  id: z.number(),
  nombre: z.string(),
  tipo: z.string(),
  expediente_id: z.number(),
  metadatos: z.object({
    resumen: z.string().optional(),
  }).optional().nullable(),
});

// Safe parsing helpers
export const safeParse = (schema, data) => {
  const result = schema.safeParse(data);
  return {
    success: result.success,
    data: result.success ? result.data : null,
    error: result.success ? null : result.error.errors,
  };
};
