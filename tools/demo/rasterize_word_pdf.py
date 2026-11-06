"""Use the packaged render_docx.py rasterizer with a native Word PDF fallback."""
from pathlib import Path
import importlib.util
import tempfile

root = Path(__file__).resolve().parents[2]
qa = root / "outputs/demo/docx-qa"
source = root / "outputs/Kich_ban_trinh_bay_demo_Web_RentalSystem.docx"
pdf = qa / "Kich_ban_trinh_bay_demo_Web_RentalSystem.pdf"
packaged = Path.home() / ".codex/plugins/cache/openai-primary-runtime/documents/26.1030.10813/skills/documents/render_docx.py"
if not pdf.exists() or pdf.stat().st_mtime < source.stat().st_mtime:
    raise RuntimeError("Export the latest Word document before rasterizing")
spec = importlib.util.spec_from_file_location("packaged_render_docx", packaged)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
# The container has no bundled Windows LibreOffice. Conversion is provided by
# Word's document API; all image rasterization/renaming stays in the skill helper.
renderer.convert_to_pdf = lambda *args, **kwargs: (str(pdf), "Native Microsoft Word PDF export")
qa_temp = qa / "temp"
qa_temp.mkdir(exist_ok=True)
tempfile.tempdir = str(qa_temp)
pages = renderer.rasterize(str(source), str(qa), dpi=130, verbose=False, emit_pdf=False)
for page in pages:
    print(page)
