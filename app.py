import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    species = pd.read_csv("species.csv")
    traits = pd.read_csv("trait_id.csv")
    species_traits = pd.read_csv("species_traits.csv")
    traits = traits.dropna(subset=["trait_id"])
    species_traits = species_traits.dropna(subset=["trait_id"])
    merged = species_traits.merge(traits, on="trait_id").merge(species, on="species_id")
    return merged

def filter_species(merged, selected_traits):
    candidates = set(merged["species_id"].unique())
    for trait_id, trait_value in selected_traits.items():
        match = merged[
            (merged["trait_id"] == trait_id) &
            (merged["trait_value"] == trait_value)
        ]["species_id"]
        candidates &= set(match)
        if not candidates:
            break
    return merged[merged["species_id"].isin(candidates)][
        ["species_id", "scientific_name", "Genus", "Family", "Order"]
    ].drop_duplicates().reset_index(drop=True)

# โหลดข้อมูล
merged = load_data()

st.title("Amphipoda Taxonomic Key")
st.write(f"ฐานข้อมูล: {merged['species_id'].nunique()} species")

# เลือก segment
segments = sorted(merged["segment"].dropna().unique())
selected_segment = st.selectbox("เลือก segment:", ["-- เลือก --"] + list(segments))

if selected_segment != "-- เลือก --":
    # เลือก character
    seg_traits = merged[merged["segment"] == selected_segment][
        ["trait_id", "character"]
    ].drop_duplicates()

    trait_options = {row["character"]: row["trait_id"] for _, row in seg_traits.iterrows()}
    selected_character = st.selectbox("เลือก character:", ["-- เลือก --"] + list(trait_options.keys()))

    if selected_character != "-- เลือก --":
        selected_trait_id = trait_options[selected_character]

        # เลือก state
        values = sorted(merged[merged["trait_id"] == selected_trait_id]["trait_value"].dropna().unique())
        selected_value = st.selectbox("เลือกลักษณะ:", ["-- เลือก --"] + list(values))

        if selected_value != "-- เลือก --":
            result = filter_species(merged, {selected_trait_id: selected_value})
            st.subheader(f"พบ {len(result)} species")
            st.dataframe(result)