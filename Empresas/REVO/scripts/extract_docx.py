import zipfile
import xml.etree.ElementTree as ET
import sys
import glob

def extract_docx_text(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as docx:
            xml_content = docx.read('word/document.xml')
        tree = ET.XML(xml_content)
        
        NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        TEXT = NAMESPACE + 't'
        PARA = NAMESPACE + 'p'
        
        paragraphs = []
        for paragraph in tree.iter(PARA):
            texts = [node.text for node in paragraph.iter(TEXT) if node.text]
            if texts:
                paragraphs.append(''.join(texts))
        return '\n\n'.join(paragraphs)
    except Exception as e:
        return f"Error reading {docx_path}: {e}"

files = [
    "/Users/regisprado/Downloads/New/Modelos/NaFazendaPontoCom - Comercial copy.docx",
    "/Users/regisprado/Downloads/New/Modelos/NaFazendaPontoCom _ Perpétuo copy.docx",
    "/Users/regisprado/Downloads/New/Modelos/NaFazendaPontoCom _ Interno copy.docx"
]

out_paths = [
    "/Users/regisprado/Downloads/New/Skills/strategic-clone/assets/template_REGIS_roteiro_comercial.md",
    "/Users/regisprado/Downloads/New/Skills/strategic-clone/assets/template_REGIS_copy_perpetuo.md",
    "/Users/regisprado/Downloads/New/Skills/strategic-clone/assets/template_REGIS_copy_interno.md"
]

for in_f, out_f in zip(files, out_paths):
    text = extract_docx_text(in_f)
    if "Error" not in text:
        with open(out_f, "w", encoding="utf-8") as f:
            f.write(f"# Template de Copy/Estratégia: {in_f.split('/')[-1]}\n\n")
            f.write(text)
        print(f"Success: {out_f}")
    else:
        print(text)
