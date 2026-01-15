from ..core.base_agent import BaseAgent
from ..core.state import KYCCaseState, CaseStatus, ExtractedData
from ..mcp_servers.validation_tools.ocr_service import OCRServices
import os

class DocumentAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DocumentAnalysisAgent",
            role_description="Extracts structured text from raw ID documents using OCR/CV."
        )

    async def process(self, state: KYCCaseState) -> KYCCaseState:
        if state.status != CaseStatus.NEW and state.status != CaseStatus.ANALYZING_DOCS:
            return state

        state.status = CaseStatus.ANALYZING_DOCS
        self.log_action(state, "START", "Beginning document analysis")

        if not state.documents:
            self.log_action(state, "ERROR", "No documents found to analyze")
            return state

        # Pick first document
        doc = state.documents[0]
        
        # 1. Computer Vision Check (Blurry?)
        qual_report = OCRServices.check_image_quality(doc.file_path)
        if qual_report.get('is_blurry'):
             self.log_action(state, "WARNING", f"Document might be blurry. Score: {qual_report['score']}")
        
        # 2. Text Extraction
        raw_text = OCRServices.extract_text(doc.file_path)
        
        # 3. Parsing
        parsed = OCRServices.parse_kyc_data(raw_text)
        
        # fallback if parsing fails completely
        if not parsed.get('full_name'):
            parsed['full_name'] = "UNKNOWN_NAME"
        if not parsed.get('id_number'):
            parsed['id_number'] = "UNKNOWN_ID"
            
        extracted = ExtractedData(
            full_name=parsed.get('full_name'),
            dob=parsed.get('dob', '1900-01-01'),
            id_number=parsed.get('id_number'),
            nationality="US", # Mocking nationality detection for now
            address="Not Extracted",
            confidence_score=0.9 if not qual_report.get('is_blurry') else 0.4
        )
        
        # Update State - Stop at REVIEW gate
        state.extracted_data = extracted
        state.status = CaseStatus.REVIEW_DOCS
        
        self.log_action(
            state, 
            "EXTRACT_DATA", 
            f"OCR Results: Name={extracted.full_name}, ID={extracted.id_number}", 
            reasoning=f"CV Quality Score: {qual_report['score']}. Raw Text Length: {len(raw_text)}",
            tools=[{"tool": "OCRServices", "input": doc.filename, "output": parsed}]
        )
        
        return state
