'''
Tài liệu tĩnh văn bản (đen trắng): Khoảng 3 MB-6 MB (trung bình ~100 – 200 KB/trang).
'''
import fitz  # PyMuPDF

def convert_to_lightweight_scanned_pdf(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    new_doc = fitz.open()

    for page in doc:
        # DPI=150 là mức chuẩn vàng cho OCR
        pix = page.get_pixmap(dpi=150, colorspace=fitz.csGRAY) # csGRAY giúp chuyển sang ảnh xám để tối ưu dung lượng
        
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        
        # Nén JPEG chất lượng 75%
        img_bytes = pix.tobytes("jpeg", jpg_quality=75)
        new_page.insert_image(page.rect, stream=img_bytes)

    # Bật nén luồng nén tối đa
    new_doc.save(output_pdf, deflate=True, garbage=4)
    new_doc.close()
    doc.close()

convert_to_lightweight_scanned_pdf("file_goc_400kb.pdf", "file_scan_nhe.pdf")
