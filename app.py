
import pandas as pd
import plotly.express as px
import streamlit as st

UCI_WINE_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/wine/wine.data"
)
FEATURE_NAMES = [
    "alcohol",
    "malic_acid",
    "ash",
    "alcalinity_of_ash",
    "magnesium",
    "total_phenols",
    "flavanoids",
    "nonflavanoid_phenols",
    "proanthocyanins",
    "color_intensity",
    "hue",
    "od280/od315_of_diluted_wines",
    "proline",
]
CLASS_COL = "clase"

#Los nombres son de la literatura no un metadato
CLASS_LABELS = {
    0: "Clase 0 (Barolo)",
    1: "Clase 1 (Grignolino)",
    2: "Clase 2 (Barbera)",
}
CHART_TYPES = ["Todos", "Histograma", "Dispersión", "Boxplot", "Correlación"]
DEFAULT_VARIABLES = ["alcohol", "malic_acid", "flavanoids", "color_intensity", "proline"]

st.set_page_config(page_title="WineDashboard", page_icon="🍷", layout="wide")


@st.cache_data
def load_wine_data() -> pd.DataFrame:
    """Return the Wine dataset with 13 numeric features and a class label."""
    try:
        from sklearn.datasets import load_wine

        raw = load_wine(as_frame=True)
        df = raw.frame.rename(columns={"target": CLASS_COL})
    except ImportError:
        # UCI file has no header; first column is the class (1, 2, 3).
        df = pd.read_csv(UCI_WINE_URL, header=None, names=[CLASS_COL, *FEATURE_NAMES])
        df[CLASS_COL] = df[CLASS_COL] - 1
    df[CLASS_COL] = df[CLASS_COL].map(CLASS_LABELS)
    return df


def render_sidebar(df: pd.DataFrame) -> dict:
    """Draw sidebar controls and return the user's selections."""
    st.sidebar.header("⚙️ Controles")
    features = [c for c in df.columns if c != CLASS_COL]

    variables = st.sidebar.multiselect(
        "Variables",
        options=features,
        default=DEFAULT_VARIABLES,
        help="Variables usadas en gráficos, correlación e indicadores.",
    )
    chart_type = st.sidebar.selectbox("Tipo de gráfico", CHART_TYPES)

    all_classes = sorted(df[CLASS_COL].unique())
    classes = st.sidebar.multiselect("Clase de vino", all_classes, default=all_classes)

    st.sidebar.subheader("Filtro adicional")
    filter_var = st.sidebar.selectbox("Filtrar por variable", features)
    vmin, vmax = float(df[filter_var].min()), float(df[filter_var].max())
    value_range = st.sidebar.slider(
        f"Rango de {filter_var}", min_value=vmin, max_value=vmax, value=(vmin, vmax)
    )
    bins = st.sidebar.slider("Número de bins (histograma)", 5, 60, 20)

    return {
        "variables": variables,
        "chart_type": chart_type,
        "classes": classes,
        "filter_var": filter_var,
        "value_range": value_range,
        "bins": bins,
    }


def apply_filters(df: pd.DataFrame, sel: dict) -> pd.DataFrame:
    low, high = sel["value_range"]
    mask = df[CLASS_COL].isin(sel["classes"]) & df[sel["filter_var"]].between(low, high)
    return df[mask]


def render_indicators(df: pd.DataFrame, variables: list[str]) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Número de datos", len(df))
    c2.metric("Número de clases", df[CLASS_COL].nunique())
    c3.metric("Número de variables", len(variables))

    with st.container(border=True):
        st.subheader("Medias de variables")
        means = df[variables].mean().to_frame("General").T
        means_by_class = df.groupby(CLASS_COL)[variables].mean()
        st.dataframe(pd.concat([means, means_by_class]).round(3), width="stretch")


def histogram(df: pd.DataFrame, variables: list[str], bins: int) -> None:
    with st.container(border=True):
        st.subheader("Histograma")
        var = st.selectbox("Variable", variables, key="hist_var")
        fig = px.histogram(
            df, x=var, color=CLASS_COL, nbins=bins, barmode="overlay", opacity=0.7
        )
        st.plotly_chart(fig, width="stretch")


def scatter(df: pd.DataFrame, variables: list[str]) -> None:
    with st.container(border=True):
        st.subheader("Gráfica de dispersión")
        if len(variables) < 2:
            st.info("Selecciona al menos 2 variables para la dispersión.")
            return
        cx, cy = st.columns(2)
        x = cx.selectbox("Eje X", variables, index=0, key="scatter_x")
        y = cy.selectbox("Eje Y", variables, index=1, key="scatter_y")
        fig = px.scatter(df, x=x, y=y, color=CLASS_COL, opacity=0.8)
        st.plotly_chart(fig, width="stretch")


def boxplot(df: pd.DataFrame, variables: list[str]) -> None:
    with st.container(border=True):
        st.subheader("Boxplot por clase de vino")
        var = st.selectbox("Variable", variables, key="box_var")
        fig = px.box(df, x=CLASS_COL, y=var, color=CLASS_COL, points="all")
        st.plotly_chart(fig, width="stretch")


def correlation(df: pd.DataFrame, variables: list[str]) -> None:
    with st.container(border=True):
        st.subheader("Matriz de correlación")
        if len(variables) < 2:
            st.info("Selecciona al menos 2 variables para la correlación.")
            return
        corr = df[variables].corr()
        fig = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
        )
        st.plotly_chart(fig, width="stretch")


def render_charts(df: pd.DataFrame, sel: dict) -> None:
    variables, chart_type = sel["variables"], sel["chart_type"]
    charts = {
        "Histograma": lambda: histogram(df, variables, sel["bins"]),
        "Dispersión": lambda: scatter(df, variables),
        "Boxplot": lambda: boxplot(df, variables),
        "Correlación": lambda: correlation(df, variables),
    }
    if chart_type != "Todos":
        charts[chart_type]()
        return

    names = list(charts)
    for row in (names[:2], names[2:]):
        for col, name in zip(st.columns(2), row):
            with col:
                charts[name]()


def main() -> None:
    st.title("🍷 WineDashboard")
    st.caption("Análisis exploratorio del dataset Wine (UCI): 178 vinos, 3 clases.")

    df = load_wine_data()
    sel = render_sidebar(df)

    if not sel["variables"]:
        st.warning("Selecciona al menos una variable en la barra lateral.")
        st.stop()
    filtered = apply_filters(df, sel)
    if filtered.empty:
        st.warning("Ningún dato cumple los filtros. Amplía el rango o las clases.")
        st.stop()

    render_indicators(filtered, sel["variables"])
    render_charts(filtered, sel)

    with st.expander("Ver datos filtrados"):
        st.dataframe(filtered, width="stretch")


main()
