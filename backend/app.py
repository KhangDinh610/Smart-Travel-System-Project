import streamlit as st

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
    st.write("Upload an image to preprocess and extract a 512-dim vector.")

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
        st.subheader("Processed (OpenCV)")
        st.image(processed_image, use_container_width=True)

    with st.spinner("Extracting features..."):
        vector = extractor.extract_vector(processed_image)

    st.subheader("Vector Output")
    st.write(f"Vector shape: {vector.shape}")
    st.write("Vector preview (first 20 values):")
    st.json(vector[:20].tolist())


if __name__ == "__main__":
    main()
