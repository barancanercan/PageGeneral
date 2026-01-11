"""
PageGeneral
Streamlit UI
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path

# PyTorch DLL fix
try:
    import torch
except ImportError:
    pass

from src.ingest import IngestPipeline
from src.query import DivisionQuery
import config

# Page config
st.set_page_config(
    page_title="PageGeneral",
    page_icon="📚",
    layout="wide"
)

# Cache
@st.cache_resource
def get_pipeline():
    return IngestPipeline()

@st.cache_resource
def get_query():
    return DivisionQuery()

pipeline = get_pipeline()
query = get_query()


def main():
    # Logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo/logo.png", width=200)

    st.title("PageGeneral")
    st.caption("PDF'lerden tumen bilgisi cikarin ve JSON olarak indirin")

    # Sidebar: Kitap Yonetimi
    with st.sidebar:
        st.header("Kitaplar")

        # Yuklu kitaplar
        books = query.list_books()

        if books:
            book_names = [b['title'] for b in books]
            selected_book = st.selectbox(
                "Kitap Sec",
                options=book_names,
                index=0
            )

            # Secilen kitabin ID'sini bul
            book_id = None
            for b in books:
                if b['title'] == selected_book:
                    book_id = b['id']
                    st.caption(f"Paragraf: {b['paragraphs']}")
                    break
        else:
            st.info("Henuz kitap yuklenmemis")
            selected_book = None
            book_id = None

        st.divider()

        # Yeni kitap yukle
        st.subheader("Yeni Yukle")
        uploaded_file = st.file_uploader("PDF Sec", type=['pdf'])

        if uploaded_file and st.button("Yukle", type="primary"):
            with st.spinner("Yukleniyor..."):
                # Gecici dosyaya kaydet
                temp_path = config.INPUT_DIR / uploaded_file.name
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())

                # Ingest
                result = pipeline.ingest_pdf(temp_path, force=True)

                if result["status"] == "success":
                    st.success(f"Yuklendi: {result['paragraphs']} paragraf")
                    st.cache_resource.clear()
                    st.rerun()
                else:
                    st.error(result.get('message', 'Hata'))

    # Ana icerik
    if book_id:
        # Filtre
        col1, col2 = st.columns([3, 1])
        with col1:
            only_divisions = st.checkbox("Sadece tumen icerenler", value=True)
        with col2:
            if st.button("JSON Indir", type="primary"):
                # Export
                result = query.export_json(
                    book_id=book_id,
                    only_with_divisions=only_divisions,
                    include_embeddings=True
                )
                if result["status"] == "success":
                    with open(result["output_file"], 'r', encoding='utf-8') as f:
                        json_data = f.read()

                    st.download_button(
                        label="Indir",
                        data=json_data,
                        file_name=f"{selected_book}_export.json",
                        mime="application/json"
                    )

        # Paragraflar
        paragraphs = query.get_all_paragraphs(
            book_id=book_id,
            only_with_divisions=only_divisions,
            include_embeddings=False
        )

        if paragraphs:
            # Ozet
            divisions = set()
            for p in paragraphs:
                divisions.update(p["metadata"]["division"])

            st.metric("Toplam Paragraf", len(paragraphs))
            st.caption(f"Tumenler: {sorted(divisions, key=lambda x: int(x) if x.isdigit() else 0)}")

            st.divider()

            # Tablo
            rows = []
            for p in paragraphs:
                rows.append({
                    "Sayfa": p["metadata"]["source_page"],
                    "Tumen": ", ".join(p["metadata"]["division"]) or "-",
                    "Guven": f"{p['metadata']['confidence']:.0%}",
                    "Metin": p["document"]
                })

            df = pd.DataFrame(rows)

            # Dataframe goster
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Sayfa": st.column_config.NumberColumn(width="small"),
                    "Tumen": st.column_config.TextColumn(width="small"),
                    "Guven": st.column_config.TextColumn(width="small"),
                    "Metin": st.column_config.TextColumn(width="large")
                }
            )
        else:
            st.info("Paragraf bulunamadi")

    else:
        st.info("Sol taraftan kitap secin veya yeni PDF yukleyin")

        # Cikti formati ornegi
        st.subheader("Cikti Formati")
        st.code('''
{
  "id": "parag_5",
  "embedding": [384 deger...],
  "document": "Tam paragraf metni...",
  "metadata": {
    "division": ["5", "36"],
    "confidence": 0.85,
    "source_page": 27
  }
}
        ''', language="json")


if __name__ == "__main__":
    main()
