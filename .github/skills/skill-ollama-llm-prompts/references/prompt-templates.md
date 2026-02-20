# Prompt Templates for Olympus Use Cases

## 1. Auto-Rellenado de Expedientes (OCR → JSON)

**Goal**: Extract structured metadata from scanned/uploaded documents.

**Template**:
```
You are a document extraction expert. Analyze the following document text 
and extract the following fields in JSON format:
- solicitante (requester name)
- tipo_tramite (procedure type)
- monto (amount in EUR, null if not applicable)
- articulos_clave (relevant legal articles)
- fecha_solicitud (request date, ISO format or null)
- descripcion (summary in 1-2 sentences)

Document text:
{OCR_TEXT}

Return ONLY valid JSON, no markdown:
```

**Validation**: 
```python
from pydantic import BaseModel, validator
from typing import Optional

class ExtractedMetadata(BaseModel):
    solicitante: str
    tipo_tramite: str
    monto: Optional[float] = None
    articulos_clave: list[str]
    fecha_solicitud: Optional[str] = None
    descripcion: str
    
    @validator('monto')
    def validate_monto(cls, v):
        if v is not None and v < 0:
            raise ValueError("Amount must be positive")
        return v
```

**Example Output**:
```json
{
  "solicitante": "María García López",
  "tipo_tramite": "Licencia de construcción",
  "monto": 50000.0,
  "articulos_clave": ["Art.23 Código Técnico", "Art.47 Ley 38/1988"],
  "fecha_solicitud": "2024-02-15",
  "descripcion": "Solicitud para ampliación de vivienda en zona urbana consolidada."
}
```

---

## 2. Asistente Virtual (Context-Aware Recommendations)

**Goal**: Recommend next steps in expediente workflow based on history.

**Template**:
```
You are a legal/administrative assistant for government processes (Spain).
Given the following expediente context, recommend the next procedural step 
and relevant legal references.

Current status:
- Expediente #: {EXPEDIENTE_NUM}
- Type: {TIPO_TRAMITE}
- Current step: {PASO_ACTUAL}
- History: {HISTORIAL_PASOS}
- Uploaded documents: {DOCUMENTOS}

Provide:
1. Recommended next step (name, description)
2. Required documents (if any)
3. Relevant legal articles (Spain, autonomous community)
4. Estimated duration

Be concise and practical. Use Spanish for references.

Response format:
**Siguiente Paso:** <name>
**Descripción:** <description>
**Documentos Requeridos:** <list>
**Artículos Aplicables:** <list>
**Duración Estimada:** <days/weeks>
```

**Example Output**:
```
**Siguiente Paso:** Validación técnica
**Descripción:** El expediente requiere evaluación técnica del proyecto adjunto.
**Documentos Requeridos:** 
  - Planos técnicos (ya adjuntos)
  - Informe de impacto ambiental
**Artículos Aplicables:** Art.47 Ley 38/1988, Art.9.3 LRJPAC
**Duración Estimada:** 5-10 días laborales
```

---

## 3. Predicción de Tendencias de Gasto

**Goal**: Forecast budget trends from historical data.

**Template**:
```
You are a financial analyst for government budgets (Spain).
Analyze the following 6-month spending history and predict the next 3 months.

Data (CSV format):
{CSV_GASTO_HISTORICO}

Provide:
1. Trend analysis (increasing, stable, decreasing)
2. Predicted spending for next 3 months
3. Risk factors (if overspending likely)
4. Recommendations (controls to implement)

Use EUR currency. Be data-driven.
```

**Example CSV Input**:
```
month,category,amount_eur
2023-08,personal,150000
2023-08,supplies,45000
2023-09,personal,151000
2023-09,supplies,46000
2023-10,personal,150500
2023-10,supplies,44500
2023-11,personal,152000
2023-11,supplies,47000
2023-12,personal,153000
2023-12,supplies,46500
2024-01,personal,154000
2024-01,supplies,48000
```

**Example Output**:
```
**Análisis de Tendencia:**
- Personal: +0.5-1% mensual (tendencia ligera al alza)
- Supplies: ±2% (variable pero estable)

**Predicción Próximos 3 Meses:**
- Feb 2024: €155,500 personal + €47,500 supplies = €203,000
- Mar 2024: €156,000 personal + €48,000 supplies = €204,000
- Apr 2024: €156,500 personal + €48,200 supplies = €204,700

**Factores de Riesgo:**
- Personal costs trending up (0.5-1%/month) → May exceed budget if trend continues
- No seasonal variation detected → hard to anticipate spikes

**Recomendaciones:**
- Implement freeze on new hires to control personal costs
- Monitor supplies for potential suppliers issues
```

---

## 4. Clasificación Legal (Cláusulas Aplicables)

**Goal**: Identify relevant legal framework for a procedure.

**Template**:
```
You are a legal research assistant specializing in Spanish administrative law.
Given a procedure type and context, identify applicable laws and regulations.

Procedure: {TIPO_TRAMITE}
Context: {CONTEXTO}

Provide:
1. Applicable national laws (with articles)
2. Applicable autonomous community regulations (if any)
3. EU regulations (if applicable)
4. Municipal ordinances (if applicable)

Format as hierarchical list with brief descriptions.
```

**Example Output**:
```
**Normativa Aplicable:**

1. **Nacional**
   - Ley 39/2015 de Procedimiento Administrativo Común (LPAC)
     Art.14 (Negociación previa), Art.42 (Iniciación), Art.89 (Silencio administrativo)
   - Ley 38/1988 de Ordenación de la Edificación
     Art.47 (Licencias de obra)

2. **Autonómica (Madrid)**
   - Decreto 73/2011 de Régimen de Suelo
   - Orden 26/2021 de Licencias Urbanísticas

3. **UE**
   - Directiva 2014/24/UE (Contratación pública)

4. **Municipal (Madrid)**
   - Ordenanza de Licencias Urbanísticas (vigente desde 2022)
```

---

## Best Practices

**Do's**:
- ✓ Include specific instructions (e.g., "Return ONLY JSON")
- ✓ Provide examples for expected format
- ✓ Set context clearly (role, domain, constraints)
- ✓ Validate outputs with Pydantic schemas
- ✓ Test with real data before production

**Don'ts**:
- ✗ Assume model understands implicit formatting (be explicit)
- ✗ Ask open-ended questions (be specific)
- ✗ Use prompts longer than 2000 tokens (truncate context)
- ✗ Trust model output without validation (always parse/validate)

---

## Prompt Iteration Workflow

1. **Draft**: Write prompt, identify required fields
2. **Test**: Run with 5-10 real examples, measure accuracy
3. **Refine**: Adjust instructions based on errors
4. **Validate**: Check output matches Pydantic schema
5. **Production**: Use with monitoring (log failures)
