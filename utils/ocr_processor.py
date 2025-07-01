import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import os
from config import get_tesseract_config, get_poppler_config, OCR_CONFIG

class OCRProcessor:
    def __init__(self):
        # Configurar Tesseract
        tesseract_cmd, tessdata_prefix = get_tesseract_config()
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        os.environ["TESSDATA_PREFIX"] = tessdata_prefix
        
        # Configurar Poppler
        self.poppler_path = get_poppler_config()
    
    def preprocess_image(self, image):
        """Aplica pré-processamento na imagem para melhorar OCR"""
        if not OCR_CONFIG["preprocessing"]:
            return image
        
        # Converter PIL para OpenCV
        img_array = np.array(image)
        
        # Converter para escala de cinza se necessário
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Aplicar denoising
        denoised = cv2.medianBlur(gray, 3)
        
        # Aplicar threshold adaptativo
        thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # Converter de volta para PIL
        processed_image = Image.fromarray(thresh)
        
        # Melhorar contraste
        enhancer = ImageEnhance.Contrast(processed_image)
        enhanced = enhancer.enhance(1.5)
        
        # Aplicar filtro de nitidez
        sharpened = enhanced.filter(ImageFilter.SHARPEN)
        
        return sharpened
    
    def extract_text_from_pdf(self, pdf_file):
        """Extrai texto de PDF usando OCR"""
        try:
            # Converter PDF para imagens
            if self.poppler_path:
                images = convert_from_bytes(pdf_file.read(), poppler_path=self.poppler_path)
            else:
                images = convert_from_bytes(pdf_file.read())
            
            all_text = ""
            confidence_scores = []
            
            for i, image in enumerate(images):
                # Pré-processar imagem
                processed_image = self.preprocess_image(image)
                
                # Configurar OCR
                custom_config = f'--oem 3 --psm 6 -l {"+".join(OCR_CONFIG["languages"])}'
                
                # Extrair texto com dados de confiança
                try:
                    data = pytesseract.image_to_data(processed_image, config=custom_config, 
                                                   output_type=pytesseract.Output.DICT)
                    
                    # Filtrar por confiança
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > OCR_CONFIG["confidence_threshold"]]
                    words = [data['text'][i] for i, conf in enumerate(data['conf']) 
                           if int(conf) > OCR_CONFIG["confidence_threshold"] and data['text'][i].strip()]
                    
                    page_text = ' '.join(words)
                    all_text += f"\n--- Página {i+1} ---\n{page_text}\n"
                    
                    if confidences:
                        confidence_scores.extend(confidences)
                
                except Exception as e:
                    # Fallback para OCR simples
                    page_text = pytesseract.image_to_string(processed_image, lang='por+eng')
                    all_text += f"\n--- Página {i+1} ---\n{page_text}\n"
            
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            return {
                "text": all_text,
                "pages": len(images),
                "confidence": avg_confidence,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "text": "",
                "pages": 0,
                "confidence": 0,
                "status": "error",
                "error": str(e)
            }
    
    def extract_text_from_image(self, image_file):
        """Extrai texto de imagem usando OCR"""
        try:
            image = Image.open(image_file)
            processed_image = self.preprocess_image(image)
            
            custom_config = f'--oem 3 --psm 6 -l {"+".join(OCR_CONFIG["languages"])}'
            
            # Extrair texto com dados de confiança
            data = pytesseract.image_to_data(processed_image, config=custom_config, 
                                           output_type=pytesseract.Output.DICT)
            
            # Filtrar por confiança
            confidences = [int(conf) for conf in data['conf'] if int(conf) > OCR_CONFIG["confidence_threshold"]]
            words = [data['text'][i] for i, conf in enumerate(data['conf']) 
                   if int(conf) > OCR_CONFIG["confidence_threshold"] and data['text'][i].strip()]
            
            text = ' '.join(words)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "text": text,
                "pages": 1,
                "confidence": avg_confidence,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "text": "",
                "pages": 0,
                "confidence": 0,
                "status": "error",
                "error": str(e)
            } 