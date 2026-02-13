import pypdfium2 as pdfium
import os
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    def generate_screenshots(file_path: str, output_dir: str, page_indices: List[int] = None, max_pages: int = 3) -> List[str]:
        """
        Generate screenshots for specific pages or first N pages.
        Returns list of relative paths to the screenshots.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return []

        try:
            pdf = pdfium.PdfDocument(file_path)
            total_pages = len(pdf)
            
            if page_indices:
                # Use specific pages, filter out invalid ones
                pages_to_render = [p for p in page_indices if 0 <= p < total_pages]
            else:
                # Use first N pages
                pages_to_render = list(range(min(max_pages, total_pages)))
            
            screenshot_paths = []
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            for i in pages_to_render:
                page = pdf[i]
                # Render page to bitmap
                bitmap = page.render(scale=2.0) # Scale 2.0 for better quality
                pil_image = bitmap.to_pil()
                
                # Save image
                image_filename = f"{base_name}_page_{i+1}.jpg"
                image_path = os.path.join(output_dir, image_filename)
                pil_image.save(image_path)
                
                # Return path relative to static/uploads or similar
                # Assuming output_dir is .../static/screenshots
                # We return "screenshots/filename.jpg"
                rel_dir = os.path.basename(output_dir)
                screenshot_paths.append(f"{rel_dir}/{image_filename}")
                
            return screenshot_paths
            
        except Exception as e:
            logger.error(f"Error generating screenshots: {e}")
            return []

    @staticmethod
    def extract_text(file_path: str, max_pages: int = 5) -> str:
        """
        Extract text from first N pages for AI analysis.
        """
        if not os.path.exists(file_path):
            return ""
            
        try:
            pdf = pdfium.PdfDocument(file_path)
            text_content = []
            
            for i in range(min(max_pages, len(pdf))):
                page = pdf[i]
                textpage = page.get_textpage()
                text_content.append(textpage.get_text_range())
                
            return "\n".join(text_content)
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""

pdf_service = PDFService()
