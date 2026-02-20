# OCR Quality Checks & Validation

## Quality Metrics

```python
from dataclasses import dataclass
from enum import Enum


class QualityLevel(str, Enum):
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"  # 70-90%
    FAIR = "fair"  # 50-70%
    POOR = "poor"  # <50%


@dataclass
class QualityMetrics:
    character_confidence: float  # 0-100
    word_count: int
    line_count: int
    error_pattern_count: int
    compression_ratio: float
    language_detection: str
    orientation: int  # 0, 90, 180, 270
    skew_angle: float
    
    def calculate_score(self) -> float:
        """Calculate overall quality score"""
        score = self.character_confidence
        
        # Penalize for errors
        error_penalty = min(self.error_pattern_count * 5, 20)
        score -= error_penalty
        
        return max(0, min(100, score))
    
    def get_quality_level(self) -> QualityLevel:
        """Categorize quality"""
        score = self.calculate_score()
        
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 70:
            return QualityLevel.GOOD
        elif score >= 50:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR
```

## Common OCR Errors

### Confidence Thresholds

```python
CONFIDENCE_THRESHOLDS = {
    "accept": 90,  # Automatically accept
    "review": 70,  # Manual review needed
    "reject": 50,  # Likely reject
}

# Common character confusions
CHARACTER_CONFUSIONS = {
    "0": ["O"],
    "1": ["l", "I"],
    "5": ["S"],
    "8": ["B"],
    "l": ["1", "I"],
    "O": ["0"],
    "S": ["5"],
}
```

### Error Detection Patterns

```python
import re


class ErrorDetector:
    """Detect common OCR errors"""
    
    @staticmethod
    def detect_line_breaks(text: str) -> int:
        """False line breaks detection"""
        # Look for broken words (word-\\n word)
        pattern = r'(\w+)-\n(\w+)'
        matches = re.findall(pattern, text)
        return len(matches)
    
    @staticmethod
    def detect_low_confidence_chars(text: str) -> int:
        """Detect confidence-sensitive characters"""
        # Common character substitutions
        suspicious_patterns = [
            r'0+[OO]',  # "000O" suspicious
            r'1+[lI]',  # "111l" suspicious
            r'[|!][\w]',  # Pipe character before word
        ]
        
        count = 0
        for pattern in suspicious_patterns:
            count += len(re.findall(pattern, text))
        
        return count
    
    @staticmethod
    def detect_diacritics_loss(text: str) -> int:
        """Detect missing Spanish diacritics"""
        # Common replacements: á→a, é→e, etc
        suspicious = ['a', 'e', 'i', 'o', 'u', 'n']
        accented = ['á', 'é', 'í', 'ó', 'ú', 'ñ']
        
        # Count potential diacritic errors
        count = 0
        # This is simplified; in production, use NLP
        return count
    
    @staticmethod
    def validate_language(text: str, expected_lang: str = "es") -> bool:
        """Validate text language matches expected"""
        try:
            import langdetect
            detected = langdetect.detect(text[:200])
            
            lang_map = {
                "es": "es",
                "en": "en",
                "fr": "fr",
                "de": "de",
            }
            
            return lang_map.get(detected) == expected_lang
        except Exception:
            return True  # Assume valid if detection fails
```

## Document-Specific Validation

### Invoice Validation

```python
import re


class InvoiceValidator:
    """Validate extracted invoice data"""
    
    @staticmethod
    def validate_invoice_number(number: str) -> bool:
        """Validate invoice number format"""
        # Spanish invoice format: SERIES/SEQUENTIAL
        pattern = r'^[A-Z0-9]{1,3}/\d{6,8}$'
        return bool(re.match(pattern, number))
    
    @staticmethod
    def validate_nif(nif: str) -> bool:
        """Validate Spanish NIF (Tax ID)"""
        pattern = r'^[0-9]{8}[TRWAGMYFPDXBNJZSQVHLCKE]$'
        return bool(re.match(pattern, nif.upper()))
    
    @staticmethod
    def validate_amount(amount: str) -> bool:
        """Validate amount format"""
        pattern = r'^\d+[.,]\d{2}$'
        return bool(re.match(pattern, amount))
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format"""
        import datetime
        
        for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
            try:
                datetime.datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue
        
        return False
    
    @staticmethod
    def validate_invoice_structure(extracted_data: dict) -> dict:
        """Validate complete invoice structure"""
        
        required_fields = [
            "invoice_number",
            "date",
            "supplier",
            "supplier_nif",
            "amount"
        ]
        
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        for field in required_fields:
            if field not in extracted_data:
                results["errors"].append(f"Missing field: {field}")
                results["valid"] = False
        
        # Validate formats
        if "supplier_nif" in extracted_data:
            if not InvoiceValidator.validate_nif(extracted_data["supplier_nif"]):
                results["warnings"].append("Invalid NIF format")
        
        if "amount" in extracted_data:
            if not InvoiceValidator.validate_amount(str(extracted_data["amount"])):
                results["warnings"].append("Invalid amount format")
        
        return results
```

### Contract Validation

```python
class ContractValidator:
    """Validate extracted contract data"""
    
    @staticmethod
    def validate_party_info(party_name: str, nif: str) -> bool:
        """Validate party information"""
        if not party_name or len(party_name) < 3:
            return False
        
        if nif and not InvoiceValidator.validate_nif(nif):
            return False
        
        return True
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> bool:
        """Validate date range validity"""
        import datetime
        
        try:
            start = datetime.datetime.strptime(start_date, "%d/%m/%Y")
            end = datetime.datetime.strptime(end_date, "%d/%m/%Y")
            
            return start < end
        except ValueError:
            return False
```

## Confidence Scoring

```python
class ConfidenceScore:
    """Calculate confidence score for OCR results"""
    
    @staticmethod
    def calculate_field_confidence(
        extracted_value: str,
        field_type: str
    ) -> float:
        """Calculate confidence for specific field"""
        
        # Base confidence from OCR
        base_confidence = 85
        
        # Adjust based on validation
        if field_type == "invoice_number":
            if InvoiceValidator.validate_invoice_number(extracted_value):
                return base_confidence + 10
            else:
                return base_confidence - 30
        
        elif field_type == "nif":
            if InvoiceValidator.validate_nif(extracted_value):
                return base_confidence + 10
            else:
                return base_confidence - 30
        
        elif field_type == "amount":
            if InvoiceValidator.validate_amount(extracted_value):
                return base_confidence + 5
            else:
                return base_confidence - 20
        
        return max(0, min(100, base_confidence))
```

## Human Review Workflow

```python
class ReviewWorkflow:
    """Route low-confidence documents for review"""
    
    HIGH_CONFIDENCE_THRESHOLD = 90  # Auto-accept
    REVIEW_THRESHOLD = 70  # Manual review
    REJECT_THRESHOLD = 50  # Auto-reject
    
    @staticmethod
    def get_action(confidence_score: float) -> str:
        """Determine action based on confidence"""
        
        if confidence_score >= ReviewWorkflow.HIGH_CONFIDENCE_THRESHOLD:
            return "auto_accept"
        elif confidence_score >= ReviewWorkflow.REVIEW_THRESHOLD:
            return "send_to_review"
        else:
            return "reject"
    
    @staticmethod
    async def route_for_review(
        document_id: str,
        confidence: float,
        extracted_data: dict,
        db: AsyncSession
    ):
        """Route document to review queue"""
        
        review_task = ReviewTask(
            document_id=document_id,
            confidence=confidence,
            extracted_data=extracted_data,
            status="pending_review",
            assigned_to=None
        )
        
        db.add(review_task)
        await db.commit()
```
