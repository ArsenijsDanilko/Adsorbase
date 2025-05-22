# 🧪 Adsorbase - Adsorbent Visualization & Management App

Welcome to Adsorbase, a user-friendly adsorbent data visualization package !  
Adsorbase is a Dash-based interactive web application for visualizing, filtering, and managing a database of adsorbents based on various physical and experimental parameters. The app includes support for light/dark mode, dynamic graphs, and data export functionality.

---

## 🚀 Features

- 📊 Interactive scatter plots of adsorbent properties
- 🎚️ Range sliders for temperature and pressure filtering
- 🖱️ Customizable hover info on graph
- ➕ Form to add new adsorbent entries
- 📥 Export filtered data to CSV
- 📄 Data table displaying filtered records

---

## 📥 Installation

Adsorbase can be installed either through PiPy, or by building the package from source. End users with no intentions of modifying the source code should use pip, and developers should install from source.

### From PiPy

Not yet implemented

### From source

First, clone the repo on your machine:  

```bash
git clone https://github.com/ArsenijsDanilko/Adsorbase.git
```

Then, navigate to the directory containing the package, and install it using `pip`. We recommend doing that in a virtual environment such as venv or conda, but it is not strictly necessary.
  
```bash
cd Adsorbase
pip install -e .
```
  
If you do not intend to modify the source code of the package, using the `-e` flag in the command above is not necessary.

---

### 📦 Dependencies

Adsorbase depends on [plotly](https://dash.plotly.com/) for the interactive graph, and on [dash](https://plotly.com/dash/) for the interface. Installation is done through pip.  
Pip should handle all dependencies automatically when installing adsorbase. For developers, hatchling, tox and pytest are recommended to build and test the code.

---

## Usage

### 1. Launching the web app

1. In a python file or Jupyter notebook, import the `launch` function, and call it.

    ```python
    from adsorbase import launch
    launch()
    ```

1. Open your browser and navigate to the link provided in the output (usually <http://127.0.0.1:8050/>). That's it !

---

### 2. 

The whole point of this project is the interactive scatter plot in the center of the page. Each data point represents one adsorbent species Hovering your mouse over a data point lets you know about the adsorbent

---

## 🔧 Adding New Adsorbents

Users can add new adsorbents via the input form:

- Name (text)
- Type of Adsorbent (text)
- BET Surface Area (numeric)
- Pore Volume (numeric)
- Adsorption Capacity (numeric)
- Temperature (numeric)
- Pressure (numeric)

Simply click the "Actualize graph" button to see your newly added data on the figure.

---

## 🌗 Dark Mode

Click the dark mode button in the top right to switch themes. The UI and graph visuals will adapt accordingly.

---

## 📤 Exporting Data

Click the **"Export Filtered Data"** button to download the current filtered dataset as `filtered_data.csv`.

---

## 📝 Notes

- Custom entries persist between sessions via `custom.csv`.
- Scatter plot supports dynamic zooming, with live feedback on how many points are visible.
- Hover data can be customized using the dropdown menu above the figure.
