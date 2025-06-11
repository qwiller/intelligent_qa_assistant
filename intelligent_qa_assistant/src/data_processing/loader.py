import os
from typing import List, Dict, Any, Optional

# 第三方库，用于PDF文本提取
# 确保这些库在 requirements.txt 中
try:
    import fitz  # PyMuPDF for PDF text extraction
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("Warning: PyMuPDF (fitz) not installed. PDF text extraction will be limited.")

class DocumentLoader:
    """加载不同格式的文档并提取文本内容 (不含OCR功能)"""

    def __init__(self):
        """初始化文档加载器。"""
        pass # 目前不需要特殊初始化

    def load_document(self, file_path: str) -> str:
        """
        根据文件类型加载文档并提取文本。
        对于无法直接提取文本的图片或扫描型PDF，将返回提示信息。

        Args:
            file_path (str): 文档的路径。

        Returns:
            str: 提取的文本内容，如果无法处理则返回提示。
        
        Raises:
            FileNotFoundError: 如果文件未找到。
            ValueError: 如果文件类型明确不被支持 (非图片/扫描PDF)。
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件未找到: {file_path}")

        _, file_extension = os.path.splitext(file_path.lower())

        if file_extension == '.txt':
            return self._load_txt(file_path)
        elif file_extension == '.md':
            return self._load_markdown(file_path) # Markdown可以视为纯文本加载
        elif file_extension == '.pdf':
            return self._load_pdf(file_path)
        elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            return "[不支持处理图片文件，因为OCR功能未启用]"
        # 可以根据需要添加对 .doc, .docx 等格式的支持 (需要相应库)
        # elif file_extension == '.docx':
        #     return self._load_docx(file_path) # 需要 python-docx
        else:
            # 对于其他未知类型，可以尝试作为文本读取，或直接标记为不支持
            # raise ValueError(f"不支持的文件类型: {file_extension}")
            print(f"警告: 未知文件类型 {file_extension}，将尝试作为纯文本读取。")
            try:
                return self._load_txt(file_path) # 尝试作为文本文件处理
            except Exception as e:
                return f"[无法处理文件类型 {file_extension}: {e}]"

    def _load_txt(self, file_path: str) -> str:
        """加载TXT文件"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _load_markdown(self, file_path: str) -> str:
        """加载Markdown文件 (作为纯文本)"""
        return self._load_txt(file_path)

    def _load_pdf(self, file_path: str) -> str:
        """
        加载PDF文件，尝试提取内嵌文本。
        如果PDF是扫描件或无法提取文本，则返回提示。
        """
        text_content = ""
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text_content += page.get_text()
                doc.close()
                if text_content.strip(): # 如果提取到文本
                    return text_content
                else:
                    return "[PDF中未找到可选中文本，可能为扫描件或图片PDF，OCR功能未启用]"
            except Exception as e:
                print(f"使用PyMuPDF提取PDF文本时出错: {e}")
                return f"[处理PDF时出错: {e}，OCR功能未启用]"
        else:
            return "[无法处理PDF文件：PyMuPDF (fitz) 库未安装，OCR功能未启用]"

    # 如果将来要支持DOCX等，可以取消注释并实现
    # def _load_docx(self, file_path: str) -> str:
    #     """加载DOCX文件"""
    #     try:
    #         import docx
    #         doc = docx.Document(file_path)
    #         full_text = []
    #         for para in doc.paragraphs:
    #             full_text.append(para.text)
    #         return '\n'.join(full_text)
    #     except ImportError:
    #         return "[无法处理DOCX文件：python-docx库未安装]"
    #     except Exception as e:
    #         return f"[处理DOCX文件时出错: {e}]"

# --- 示例用法 ---
def main():
    loader = DocumentLoader()

    sample_docs_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_docs")
    os.makedirs(sample_docs_dir, exist_ok=True)
    
    txt_file_path = os.path.join(sample_docs_dir, "sample.txt")
    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write("这是一个来自TXT文件的示例文本。\nHello from a TXT file.")

    md_file_path = os.path.join(sample_docs_dir, "sample.md")
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write("# Markdown 示例\n这是一个Markdown文件。")

    # 您需要准备一个包含可选中文本的PDF (e.g., sample_text.pdf)
    # 和一个扫描版PDF (e.g., sample_scan.pdf) 放入 data/sample_docs/ 目录进行测试
    pdf_text_file_path = os.path.join(sample_docs_dir, "sample_text.pdf") 
    pdf_scan_file_path = os.path.join(sample_docs_dir, "sample_scan.pdf") 
    img_file_path = os.path.join(sample_docs_dir, "sample.png") # 假设存在此图片

    test_files = {
        "TXT": txt_file_path,
        "Markdown": md_file_path,
        "Text PDF": pdf_text_file_path, # 需要您提供此文件
        "Scanned PDF": pdf_scan_file_path, # 需要您提供此文件
        "Image": img_file_path # 需要您提供此文件
    }

    for file_type, file_path in test_files.items():
        print(f"\n--- 测试 {file_type} 文件 ({file_path}) ---")
        if not os.path.exists(file_path) and file_type not in ["Text PDF", "Scanned PDF", "Image"]:
             print(f"测试文件 {file_path} 不存在，跳过。") # 对于非手动创建的示例文件，如果不存在则跳过
             continue
        elif not os.path.exists(file_path) and file_type in ["Text PDF", "Scanned PDF", "Image"]:
            print(f"提示: 测试文件 {file_path} 不存在。请创建该文件以进行完整测试。")
            # 即使文件不存在，也调用load_document来测试其文件未找到的异常处理
            try:
                loader.load_document(file_path)
            except FileNotFoundError as e:
                print(f"预期错误: {e}")
            except Exception as e:
                print(f"加载失败: {e}")
            continue

        try:
            content = loader.load_document(file_path)
            print(f"提取内容:\n{content}")
        except Exception as e:
            print(f"加载失败: {e}")

if __name__ == '__main__':
   main()