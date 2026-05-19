import streamlit as st

from vector_db import vector_db
from visual_search import ImageVectorExtractor


st.set_page_config(
    page_title="BE2 Image-to-Vector Demo",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_extractor() -> ImageVectorExtractor:
    return ImageVectorExtractor()


def main() -> None:
    st.title("BE2 Image-to-Vector Demo")
    st.write("Upload an image to preprocess, extract CLIP vector, and retrieve products.")

    uploaded_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
    if not uploaded_file:
        return

    extractor = get_extractor()
    original_image = extractor.load_image(uploaded_file)
    processed_image = extractor.preprocess_image(original_image)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(original_image, use_container_width=True)
    with col2:
        st.subheader("Processed")
        st.image(processed_image, use_container_width=True)

    with st.spinner("Extracting features..."):
        vector = extractor.extract_vector(processed_image)

    with st.spinner("Searching in VectorDB..."):
        results = vector_db.query_image_embeddings([vector.tolist()], n_results=5)

    st.subheader("Search Results")
    if not results or not results.get("ids") or not results["ids"][0]:
        st.warning("No results found in ChromaDB image collection.")
        return

    rows = []
    ids = results.get("ids", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for idx, item_id in enumerate(ids):
        metadata = metadatas[idx] if idx < len(metadatas) else {}
        distance = distances[idx] if idx < len(distances) else None
        score = None
        if isinstance(distance, (int, float)):
            score = max(0.0, 1.0 - float(distance))

        rows.append(
            {
                "id": item_id,
                "name": metadata.get("name", "N/A"),
                "description": metadata.get("description", "N/A"),
                "price": metadata.get("price", "N/A"),
                "shop": metadata.get("shop_name", metadata.get("shop", "N/A")),
                "shop_address": metadata.get("shop_address", "N/A"),
                "similarity": score,
            }
        )

    st.dataframe(rows, use_container_width=True)


if __name__ == "__main__":
    main()
