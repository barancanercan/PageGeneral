"""
PageGeneral - Tümen Çıkarıcı
Sol: Kitaplar | Sağ: Paragraflar (scroll ile)
"""

# PyTorch DLL fix
try:
    import torch
except ImportError:
    pass

import gradio as gr
import json
import pandas as pd
from pathlib import Path

import config
from src.ingest import IngestPipeline
from src.query import DivisionQuery

# Global
pipeline = IngestPipeline()
query = DivisionQuery()


def get_books():
    """VectorDB'deki kitapları getir"""
    books = query.list_books()
    if not books:
        return []
    return [f"{b['title']} ({b['paragraphs']} paragraf)" for b in books]


def get_paragraphs(book_selection, only_divisions):
    """Seçilen kitabın paragraflarını getir"""
    if not book_selection:
        return pd.DataFrame(), "Kitap seç", ""

    # Book ID bul
    books = query.list_books()
    book_id = None
    for b in books:
        if book_selection.startswith(b['title']):
            book_id = b['id']
            break

    if not book_id:
        return pd.DataFrame(), "Kitap bulunamadı", ""

    # Paragrafları al
    paragraphs = query.get_all_paragraphs(
        book_id=book_id,
        only_with_divisions=only_divisions,
        include_embeddings=False  # UI'da embedding gösterme
    )

    if not paragraphs:
        return pd.DataFrame(), "Paragraf bulunamadı", ""

    # DataFrame oluştur
    rows = []
    for p in paragraphs:
        rows.append({
            "ID": p["id"],
            "Sayfa": p["metadata"]["source_page"],
            "Tümen": ", ".join(p["metadata"]["division"]) if p["metadata"]["division"] else "-",
            "Güven": f"{p['metadata']['confidence']:.2f}",
            "Metin": p["document"][:150] + "..." if len(p["document"]) > 150 else p["document"]
        })

    df = pd.DataFrame(rows)

    # Özet
    divisions = set()
    for p in paragraphs:
        divisions.update(p["metadata"]["division"])

    summary = f"Toplam: {len(paragraphs)} paragraf | Tümenler: {sorted(divisions, key=lambda x: int(x) if x.isdigit() else 0)}"

    return df, summary, book_id


def export_to_json(book_id, only_divisions):
    """JSON'a export et"""
    if not book_id:
        return "Önce kitap seç"

    result = query.export_json(
        book_id=book_id,
        only_with_divisions=only_divisions,
        include_embeddings=True
    )

    if result["status"] == "success":
        return f"✓ Kaydedildi: {result['output_file']}\n  {result['total_paragraphs']} paragraf"
    else:
        return f"Hata: {result.get('message')}"


def upload_book(file):
    """Yeni kitap yükle"""
    if file is None:
        return "PDF seç", gr.update()

    result = pipeline.ingest_pdf(Path(file.name), force=True)

    if result["status"] == "success":
        msg = f"✓ Yüklendi: {result['paragraphs']} paragraf"
        return msg, gr.update(choices=get_books())
    else:
        return f"Hata: {result.get('message')}", gr.update()


# UI
with gr.Blocks(title="PageGeneral", theme=gr.themes.Soft()) as app:
    gr.Markdown("# PageGeneral - Tümen Çıkarıcı")

    # Gizli state
    current_book_id = gr.State("")

    with gr.Row():
        # SOL: Kitaplar
        with gr.Column(scale=1):
            gr.Markdown("### 📚 Kitaplar")
            book_list = gr.Radio(
                choices=get_books(),
                label="VectorDB'deki kitaplar",
                interactive=True
            )
            only_div = gr.Checkbox(label="Sadece tümen içerenler", value=True)

            refresh_btn = gr.Button("🔄 Yenile")

            gr.Markdown("---")
            gr.Markdown("### 📤 Yeni Yükle")
            upload_file = gr.File(label="PDF", file_types=[".pdf"])
            upload_btn = gr.Button("Yükle", variant="primary")
            upload_status = gr.Textbox(label="Durum", interactive=False, lines=1)

        # SAĞ: Paragraflar
        with gr.Column(scale=3):
            gr.Markdown("### 📄 Paragraflar")
            summary_box = gr.Textbox(label="Özet", interactive=False, lines=1)

            paragraph_table = gr.Dataframe(
                headers=["ID", "Sayfa", "Tumen", "Guven", "Metin"],
                datatype=["str", "number", "str", "str", "str"],
                col_count=(5, "fixed"),
                wrap=True,
                row_count=(20, "dynamic")
            )

            with gr.Row():
                export_btn = gr.Button("💾 JSON Export (embedding ile)", variant="primary")
                export_status = gr.Textbox(label="Export", interactive=False, lines=1)

            gr.Markdown("""
            ---
            **Çıktı formatı** (JSON dosyasında):
            ```json
            {"id": "parag_5", "embedding": [384 değer], "document": "metin...", "metadata": {"division": ["5"], "confidence": 0.95, "source_page": 27}}
            ```
            """)

    # Events
    refresh_btn.click(
        lambda: gr.update(choices=get_books()),
        outputs=[book_list]
    )

    book_list.change(
        get_paragraphs,
        inputs=[book_list, only_div],
        outputs=[paragraph_table, summary_box, current_book_id]
    )

    only_div.change(
        get_paragraphs,
        inputs=[book_list, only_div],
        outputs=[paragraph_table, summary_box, current_book_id]
    )

    upload_btn.click(
        upload_book,
        inputs=[upload_file],
        outputs=[upload_status, book_list]
    )

    export_btn.click(
        export_to_json,
        inputs=[current_book_id, only_div],
        outputs=[export_status]
    )


if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", server_port=7860)
