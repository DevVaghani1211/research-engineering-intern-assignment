# Dev-prompts.md: AI-Assisted UI/CSS Development Log

## 📝 Statement of Methodology
Due to the strict accuracy and robustness requirements of Open Source Intelligence (OSINT) workflows, all core investigative components—including the FAISS semantic vector search, time-series analysis pipelines, Bipartite PageRank analytics, and KMeans dimensionality reduction algorithms—were manually engineered and hand-written. 

Artificial Intelligence (LLMs) was utilized **exclusively** to accelerate the frontend styling, Plotly layout aesthetics, and custom CSS injection for the Streamlit interface. 

Below is a transparent log documenting the iterative, prompt-driven workflow used strictly to refine the visual presentation layers of the application.

---

## 1. Streamlit Layout Architecture

**Prompt 1**
- **Component**: Tab Navigation
- **Prompt Used**: "I have 4 distinct analysis outputs: timeline, clustering, network, and source data. Write Streamlit code to lay these out using `st.tabs` instead of rendering them all vertically in one long scroll."
- **What Was Wrong**: The initial output created tabs but failed to isolate the heavier Plotly logic inside them, meaning all 4 charts processed simultaneously on boot, slowing down the UI.
- **How I Fixed It**: *"Refine this. Wrap the rendering of each Plotly chart within a `with st.tab:` context manager so Streamlit defers rendering until the analyst actually clicks the specific tab."*

**Prompt 2**
- **Component**: Metric Cards
- **Prompt Used**: "Generate an HTML/CSS layout using Streamlit columns to display four key metrics side-by-side at the top of the dashboard."
- **What Was Wrong**: The columns were strictly proportional, meaning long numbers caused text overlap on smaller laptop screens.
- **How I Fixed It**: *"Update the column definitions. Apply responsive CSS wrapping to the metric cards and add overflow constraints so they wrap perfectly on 13-inch screens."*

## 2. Dashboard Theme & CSS Injection

**Prompt 3**
- **Component**: Custom Typography
- **Prompt Used**: "Write a CSS block to override Streamlit's default font. Change it to JetBrains Mono for headers and Inter for standard text."
- **What Was Wrong**: The CSS applied correctly to markdown paragraphs but failed to capture Streamlit's dynamically generated div classes (like buttons and sidebar inputs).
- **How I Fixed It**: *"The base CSS missed Streamlit's proprietary `st-` classes. Update the selector to target `html, body, [class*='css']` to force the font universally across all proprietary Streamlit shadow DOM elements."*

**Prompt 4**
- **Component**: Brutalist Palantir Aesthetic
- **Prompt Used**: "Write custom CSS to give the dashboard a sharp, enterprise OSINT tool feel—similar to Palantir. Use strict dark slate backgrounds (#0A0E17), cyan accents, and remove all rounded corners."
- **What Was Wrong**: The AI added glowing neon box-shadows which made it look like a gaming application, not a serious research tool.
- **How I Fixed It**: *"Remove the neon blur effects. Replace them with sharp, 1px solid borders (`#1F2937`) and restrict the cyan accent solely to a 6px `border-left` on the main header for a strictly brutalist look."*

## 3. Plotly Chart Aesthetics

**Prompt 5**
- **Component**: Background Transparency
- **Prompt Used**: "Modify my Plotly bar chart code so the background is completely transparent instead of the default solid white."
- **What Was Wrong**: It made the plot area transparent but left a stark white paper-background around the legend and axes.
- **How I Fixed It**: *"You need to update both the plot and paper properties. Set both `plot_bgcolor='rgba(0,0,0,0)'` and `paper_bgcolor='rgba(0,0,0,0)'`."*

**Prompt 6**
- **Component**: UMAP Scatter Colors
- **Prompt Used**: "Write the Plotly code to color the UMAP scatter plot dots according to their designated KMeans cluster label."
- **What Was Wrong**: It used a high-contrast sequential color scale which implied that Cluster #5 was somehow 'greater' than Cluster #1.
- **How I Fixed It**: *"Do not use a sequential color map for unordered categorical clusters. Switch the color palette to `px.colors.qualitative.Pastel` to denote distinct, equal categories."*

## 4. UI Polish & Interactivity

**Prompt 7**
- **Component**: Hover Interactions
- **Prompt Used**: "Add custom CSS to make my metric cards pop out when an analyst hovers their mouse over them."
- **What Was Wrong**: The hover animation snapped instantly, creating a jarring, unpolished visual experience.
- **How I Fixed It**: *"Inject a CSS `transition: all 0.2s ease;` rule into the base card class so the hover state smoothly triggers a subtle cyan border and shadow lift."*

**Prompt 8**
- **Component**: Pandas DataFrame Rendering
- **Prompt Used**: "How do I render a Pandas dataframe in Streamlit so that the 'permalink' column is a clickable URL instead of raw text?"
- **What Was Wrong**: It suggested using raw HTML rendering inside the dataframe, which breaks Streamlit's native sorting and filtering functionality.
- **How I Fixed It**: *"Instead of raw HTML, utilize Streamlit's native column configuration. Use `st.column_config.LinkColumn("Reddit Link")` in the `st.dataframe()` arguments to preserve interactive sorting while displaying URLs."*
