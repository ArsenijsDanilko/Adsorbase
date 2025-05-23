# 🧪 Adsorbase - Adsorbent Visualization & Management Web App

Welcome to Adsorbase, a user-friendly adsorbent data visualization package !  
Adsorbase is a Dash-based interactive web application for visualizing, filtering, and managing a database of adsorbents based on various physical and experimental parameters. The app includes support for light/dark mode, dynamic graphs, and data export functionality.

---

## Why We Built This

The climate crisis demands urgent, science-driven solutions. Among the most promising technologies for reducing atmospheric CO₂ is **carbon capture**, with **adsorbent materials** playing a central role in making it efficient, scalable, and cost-effective.

However, the field is vast and fragmented—researchers and developers are often faced with a scattered landscape of data buried in papers, spreadsheets, and proprietary formats.

We created this interactive database to **bridge the gap between innovation and application**.

## 🚀 Features

- 📊 Interactive scatter plots of adsorbent properties
- 🎚️ Range sliders for temperature and pressure filtering
- 🖱️ Customizable hover info on graph
- ➕ Form to add new adsorbent entries
- 📥 Export filtered data to CSV
- 📄 Data table displaying filtered records

## 🚀 Special thanks

Before proceeding with the explanation of the setup, we'd like to inform you that all the data used in this project was pulled directly from a research paper called "Recent Progress in CO2 Capture by Porous Solid Materials" by Wenxing Ye et.al. Special thanks to their team.

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

## 📦 Dependencies

Adsorbase depends on [plotly](https://dash.plotly.com/) for the interactive graph, and on [dash](https://plotly.com/dash/) for the interface. Installation is done through pip.  
Pip should handle all dependencies automatically when installing adsorbase. For developers, hatchling, tox and pytest are recommended to build and test the code.

---

## 🔧 Usage

### 1. Launching the web app

1. Create a .py file, and add the following lines of code to import the `launch` function and call it.

    ```python
    from adsorbase import launch

    launch()
    ```

1. Open your browser and navigate to the link provided in the output (usually <http://127.0.0.1:8050/>). That's it!

1. Quit the application by typing Ctrl+C in the terminal.

### 2. Using Adsorbase

1. Once opened, you're greeted with an interactive graph populated with adsorbent materials. You can choose the axes of the graph using the dropdown menus at the top of the page.

1. When hovering over the points, you'll see a tooltip appear. The first and second lines correspond to the name and type of the selected adsorbent. The rest consists of the coordinates of the point.

1. You can adjust which data appears when hovering your cursor over a data point, using the dropdown menu above the graph. The data can be filtered according to the conditions in which the adsorbent's characteristics were measured, and you can zoom in or out by simply click-and-dragging the plot.

1. All the points that are displayed on the graph are also present in the table at the end of the page. The total amount of points is shown right below the graph. The data from the table can be conveniently exported to a .csv file with a simple click of a button below the table.

## 3. Adding New Adsorbents

Users can add new adsorbents to the existing database via the input form:

- Name (text)
- Type of Adsorbent (text)
- BET Surface Area (numeric)
- Pore Volume (numeric)
- Adsorption Capacity (numeric)
- Temperature during the measurements (numeric)
- Pressure during the measurements (numeric)

Simply click the "Actualize graph" button to see your newly added data on the figure.
You can keep your extended database for the next session by exporting it as explained above.

---

### 4. Dark Mode

Don't like singing your eyeballs when working late ? Click the dark mode button in the top right to switch themes. The UI and graph visuals will adapt accordingly.

---

## 📝 Notes

- Custom entries should persist internally between sessions. However, we recommend exporting them just in case when you close your session, to avoid any data loss.

- Scatter plot supports dynamic zooming, with live feedback on how many points are visible.

- Hover data can be customized using the dropdown menu above the figure.

## 📍 Roadmap

- Ability to import csv databases directly, rather than having to input them manually

- Extending the database, and adding more properties for all adsorbents
