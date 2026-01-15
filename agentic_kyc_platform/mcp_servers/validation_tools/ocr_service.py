import cv2
import numpy as np
import fitz # PyMuPDF
import logging
import re
import os

logger = logging.getLogger("OCRServices")

class OCRServices:
    @staticmethod
    def check_image_quality(file_path: str) -> dict:
        """
        Uses OpenCV to calculate Laplacian Variance (Blur detection).
        Returns {'score': float, 'is_blurry': bool}
        """
        try:
            # Read image
            if file_path.lower().endswith('.pdf'):
                return {"score": 100.0, "is_blurry": False, "note": "PDF, assumed clear"}

            img = cv2.imread(file_path)
            if img is None:
                return {"score": 0.0, "is_blurry": True, "error": "Could not read image"}

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Threshold: < 100 is usually considered blurry
            return {
                "score": score,
                "is_blurry": score < 100.0,
                "note": "Blur score calculated via Laplacian Variance"
            }
        except Exception as e:
            logger.error(f"CV Error: {e}")
            return {"score": 0, "is_blurry": True, "error": str(e)}

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Route to PyMuPDF (PDF) or Tesseract (Image).
        """
        text = ""
        try:
            if file_path.lower().endswith('.pdf'):
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text()
            else:
                # Fallback / Placeholder for Tesseract
                # import pytesseract
                # text = pytesseract.image_to_string(cv2.imread(file_path))
                text = "[OCR Placeholder: Image text extraction requires Tesseract binary installed]"
                
        except Exception as e:
            text = f"[Extraction Error: {str(e)}]"
            
        return text

    @staticmethod
    def parse_kyc_data(raw_text: str) -> dict:
        """
        Regex Heuristics to find Name/ID/DOB.
        """
        data = {}
        
        # Heuristic: Look for "ID: APP..." or "P<USA..." codes
        id_match = re.search(r'(ID|No\.|Number)[:\s]+([A-Z0-9]{5,15})', raw_text, re.IGNORECASE)
        if id_match:
            data['id_number'] = id_match.group(2)
            
        # Heuristic: Look for Date "DD/MM/YYYY" or "YYYY-MM-DD"
        dob_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})', raw_text)
        if dob_match:
            data['dob'] = dob_match.group(1)
            
        # VERY Naive Name Logic: First all-caps line or whatever
        # In prod this uses Named Entity Recognition (NER)
        lines = [l.strip() for l in raw_text.split('\n') if len(l.strip()) > 5]
        if lines:
            data['full_name'] = lines[0] # Assume first significant line is Name header
            
        return data
