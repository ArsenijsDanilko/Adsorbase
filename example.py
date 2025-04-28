from rdkit import Chem
from rdkit.Chem import PandasTools
import pandas as pd
from pathlib import Path
import numpy as np
from rdkit.Chem import AllChem, DataStructs
# from sklearn.decomposition import PCA
import plotly.express as px
# import molplotly

csv_file = Path("/home/aurele/Projects/Adsorbase/adsorbents.csv")
df2 = pd.read_csv(csv_file, sep=",")
df2.head()


fig_pca = px.scatter(
    df2,  # data to pull from
    x="Pore volume",  # column name withx-axis
    y="Adsorption capacity",  # column name withy-axis
    color="Type of Adsorbent",  # color by application
    title="Adsorbents",  # title of the plot
    labels={"color": "Type of Adsorbent"},  # label for the color legend
    hover_data=["Conditions T","Conditions P"],
    hover_name="Name",
    width=1200,
    height=800,
)

# populate with molecule information
# app_pca = molplotly.add_molecules(
#     fig=fig_pca,  # figure to populate
#     df=df2,
#     show_img=False,
#     smiles_col="BET Surface Area",  # column with SMILES
#     title_col="Name",  # column to take the name for the molecule when hovering over it
#     caption_cols=[
#         "Conditions P",
#         "Conditions T",
#     ],  # columns to take the additional captions from
#     color_col="Type of Adsorbent",  # column to color by
#     show_coords=False,
# )

# show the plot: don't use the same port several times as it will overwrite the previous one
# app_pca.run(port=8408)

fig_pca.show()
