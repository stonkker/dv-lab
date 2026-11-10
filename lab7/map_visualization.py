"""
TFB3133/TEB3133 Data Visualization - Lab 7
Interactive Map Visualization Examples using Streamlit

Run with:   streamlit run map_visualization.py
Needs:      ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp
            (folder next to this file, with the .shp, .shx, .dbf, .prj and .cpg files)

Four map types, chosen from the sidebar:
  1. Map Cosmetics          - basic styling (colours, background, borders)
  2. Map Visual Hierarchy   - highlight selected countries in red
  3. Choropleth Map         - population density, colour scheme + log option
  4. Geo Projection         - the same choropleth in different map projections
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.set_page_config(page_title="Lab 7 - Map Visualization", layout="wide")

HERE = Path(__file__).resolve().parent
SHAPEFILE = HERE / "ne_110m_admin_0_countries" / "ne_110m_admin_0_countries.shp"

# Colour schemes, shown with plain names in the dropdowns (low value -> high value)
COLOUR_SCHEMES = {
    "OrRd": "Light orange → Dark red",
    "YlGn": "Yellow → Green",
    "Blues": "Light blue → Dark blue",
    "Purples": "Light purple → Dark purple",
    "Greens": "Light green → Dark green",
}

# The lab sheet uses projection_options but never defines it - these are the options
projection_options = {
    "Plate Carrée (plain latitude/longitude)": "EPSG:4326",
    "Mercator": "EPSG:3395",
    "Robinson": "ESRI:54030",
    "Mollweide (equal-area)": "ESRI:54009",
    "Equal Earth (equal-area)": "EPSG:8857",
    "Winkel Tripel": "ESRI:54042",
}
PROJECTION_NOTES = {
    "Plate Carrée (plain latitude/longitude)": "Longitude and latitude drawn as a simple grid. "
        "Easy to read, but countries near the poles are stretched sideways.",
    "Mercator": "Keeps shapes and directions correct (used for navigation), but hugely enlarges "
        "areas near the poles - Greenland looks as big as Africa, though Africa is about 14x larger.",
    "Robinson": "A compromise projection - nothing is exactly correct, but shapes and sizes are "
        "only slightly distorted. Often used in atlases.",
    "Mollweide (equal-area)": "Every country keeps its true area, so sizes can be compared fairly. "
        "Shapes near the edges get squashed.",
    "Equal Earth (equal-area)": "A modern equal-area projection (2018) that keeps true areas "
        "while looking more natural than Mollweide.",
    "Winkel Tripel": "Balances area, direction and distance distortion. Used by National Geographic "
        "for world maps.",
}


# --------------------------------------------------------------------------
# Load the Natural Earth dataset
# --------------------------------------------------------------------------
@st.cache_data
def load_data():
    if not SHAPEFILE.exists():
        return None
    gdf = gpd.read_file(SHAPEFILE)
    # Natural Earth uses upper-case column names (NAME, POP_EST) - make them lower-case
    gdf.columns = [c.lower() if c != "geometry" else c for c in gdf.columns]
    if "pop_est" not in gdf.columns:
        np.random.seed(0)
        gdf["pop_est"] = np.random.randint(1e6, 1e9, size=len(gdf))
    # Area in km² using an equal-area projection. Measuring in plain latitude/longitude
    # (as the lab sheet does) gives "square degrees", which makes countries near the
    # poles look much bigger than they are and their density much too low.
    gdf["area_km2"] = gdf.to_crs("ESRI:54009").area / 1e6
    gdf["pop_density"] = gdf["pop_est"] / gdf["area_km2"]
    return gdf


gdf = load_data()
if gdf is None:
    st.error(
        "**Map file not found.** Put the `ne_110m_admin_0_countries` folder (with the .shp, .shx, "
        f".dbf, .prj and .cpg files inside) in this folder:\n\n`{HERE}`\n\nthen refresh the page."
    )
    st.stop()


def density_column(data, use_log):
    """Return the column to colour by, plus a legend label."""
    if use_log:
        data["density_plot"] = np.log10(data["pop_density"] + 1)
        return "density_plot", "Population density, log scale (1 = 10, 2 = 100, 3 = 1,000 people/km²)"
    data["density_plot"] = data["pop_density"]
    return "density_plot", "Population density (people per km²)"


def choropleth(ax, data, cmap, use_log):
    col, label = density_column(data, use_log)
    data.plot(column=col, cmap=cmap, edgecolor="black", linewidth=0.3, legend=True, ax=ax,
              legend_kwds={"label": label, "orientation": "horizontal", "shrink": 0.6, "pad": 0.04})
    ax.set_axis_off()


# --------------------------------------------------------------------------
# Streamlit setup
# --------------------------------------------------------------------------
st.title("Interactive Map Visualization Examples")
st.sidebar.header("Choose a Map Type")
map_type = st.sidebar.radio("Select Map Type", [
    "Map Cosmetics",
    "Map Visual Hierarchy",
    "Choropleth Map",
    "Geo Projection",
])


# --------------------------------------------------------------------------
# 1. Map Cosmetics
# --------------------------------------------------------------------------
if map_type == "Map Cosmetics":
    st.subheader("1. Map Cosmetics")
    st.caption("Change the map's look - colours, borders and background - without changing the data.")
    c1, c2, c3, c4 = st.columns(4)
    land = c1.color_picker("Country colour", "#87CEEB")          # skyblue
    border = c2.color_picker("Border colour", "#000000")
    background = c3.color_picker("Background (sea) colour", "#D3D3D3")   # lightgrey
    width = c4.slider("Border thickness", 0.0, 2.0, 0.5, 0.1)

    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(ax=ax, color=land, edgecolor=border, linewidth=width)
    ax.set_title("Styled Map Example", fontsize=15, fontweight="bold")
    ax.set_facecolor(background)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    st.pyplot(fig)
    plt.close(fig)


# --------------------------------------------------------------------------
# 2. Map Visual Hierarchy
# --------------------------------------------------------------------------
elif map_type == "Map Visual Hierarchy":
    st.subheader("2. Map Visual Hierarchy")
    st.caption("Highlighted countries stand out in red; everything else is a muted background colour, "
               "so the eye goes straight to what matters.")
    highlighted_countries = st.multiselect(
        "Select countries to highlight in red",
        sorted(gdf["name"].unique()),
        default=["Brazil", "India", "China", "Australia", "South Africa", "Russia"],
    )
    gdf["color"] = gdf["name"].apply(lambda x: "red" if x in highlighted_countries else "skyblue")

    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(color=gdf["color"], edgecolor="black", linewidth=0.5, ax=ax)
    ax.set_title("Map Visual Hierarchy with Selected Countries Highlighted in Red")
    ax.set_axis_off()
    st.pyplot(fig)
    plt.close(fig)

    if highlighted_countries:
        sel = gdf[gdf["name"].isin(highlighted_countries)][["name", "continent", "pop_est", "area_km2"]]
        sel = sel.sort_values("pop_est", ascending=False).rename(columns={
            "name": "Country", "continent": "Continent", "pop_est": "Population", "area_km2": "Area (km²)"})
        st.dataframe(sel.style.format({"Population": "{:,.0f}", "Area (km²)": "{:,.0f}"}),
                     hide_index=True, width="stretch")


# --------------------------------------------------------------------------
# 3. Choropleth Map
# --------------------------------------------------------------------------
elif map_type == "Choropleth Map":
    st.subheader("3. Choropleth Map")
    st.caption("Each country is coloured by its population density (people per km²). Darker = more crowded.")
    color_choice = st.selectbox("Choose Color Scheme", list(COLOUR_SCHEMES), index=0,
                                format_func=COLOUR_SCHEMES.get)
    use_log_scale = st.checkbox("Use Log Transformation", value=True,
                                help="Densities range from under 1 to over 1,000 people/km². Without log, "
                                     "a few very dense countries get the darkest colour and almost "
                                     "everything else looks the same pale shade.")

    data = gdf[gdf["name"] != "Antarctica"].copy()   # no permanent population
    fig, ax = plt.subplots(figsize=(10, 6))
    choropleth(ax, data, color_choice, use_log_scale)
    ax.set_title(f"Population Density by Country (Color Scheme: {COLOUR_SCHEMES[color_choice]})")
    st.pyplot(fig)
    plt.close(fig)

    top = data.nlargest(5, "pop_density")[["name", "pop_density"]]
    low = data.nsmallest(5, "pop_density")[["name", "pop_density"]]
    fmt = {"People per km²": "{:,.1f}"}
    c1, c2 = st.columns(2)
    c1.write("**Most densely populated**")
    c1.dataframe(top.rename(columns={"name": "Country", "pop_density": "People per km²"}).style.format(fmt),
                 hide_index=True, width="stretch")
    c2.write("**Least densely populated**")
    c2.dataframe(low.rename(columns={"name": "Country", "pop_density": "People per km²"}).style.format(fmt),
                 hide_index=True, width="stretch")


# --------------------------------------------------------------------------
# 4. Geo Projection
# --------------------------------------------------------------------------
elif map_type == "Geo Projection":
    st.subheader("4. Geo Projection")
    st.caption("A projection is how the round Earth is flattened onto a flat map. Every projection "
               "distorts something - shape, area, distance or direction.")
    proj_choice = st.selectbox("Select a Projection", list(projection_options.keys()))
    color_choice = st.selectbox("Choose Color Scheme", list(COLOUR_SCHEMES), index=0,
                                format_func=COLOUR_SCHEMES.get)
    use_log_scale = st.checkbox("Use Log Transformation for Population Density", value=True)
    st.info(f"**{proj_choice}:** {PROJECTION_NOTES[proj_choice]}")

    # Antarctica is removed: Mercator cannot draw the South Pole (it stretches to infinity)
    data = gdf[gdf["name"] != "Antarctica"].copy()
    gdf_proj = data.to_crs(projection_options[proj_choice])

    fig, ax = plt.subplots(figsize=(10, 6))
    choropleth(ax, gdf_proj, color_choice, use_log_scale)
    ax.set_title(f"Map in {proj_choice} Projection")
    st.pyplot(fig)
    plt.close(fig)
