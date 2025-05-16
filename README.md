# 🧪 Adsorbase - Adsorbent Visualization & Management App

Welcome to Adsorbase !  
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

## 📦 Dependencies

Make sure to install the required libraries using:

```bash
pip install dash_bootstrap_components dash_bootstrap_templates dash pandas plotly
```

---

## 📌 How to Run

1. Run the app

    ```bash
    python app.py
    ```

1. Open your browser and navigate to `http://127.0.0.1:8050/`.

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

Entries are saved to `custom.csv`.

---

## 🌗 Dark Mode

Click the **"Activate Dark Mode"** button to switch themes. The UI and graph visuals will adapt accordingly.

---

## 📤 Exporting Data

Click the **"Export Filtered Data"** button to download the current filtered dataset as `filtered_data.csv`.

---

## 📝 Notes

- Custom entries persist between sessions via `custom.csv`.
- Scatter plot supports dynamic zooming, with live feedback on how many points are visible.
- Hover data can be customized using the dropdown menu above the figure.
