# ML Base Platform

A web-based machine learning platform built with Streamlit that allows users to upload data files, write custom Python algorithms in a code editor, and execute them with visualization of results.

## Features

- **Drag & Drop Data Upload**: Support for CSV, JSON, Excel, and Parquet files
- **Code Editor**: Write Python algorithms with syntax highlighting
- **Data Preview**: View data structure, columns, and sample rows
- **Code Execution**: Run algorithms with pre-loaded ML libraries
- **Results Visualization**: View outputs, data, variables, and plots in organized tabs
- **Interactive Parameter Sliders**: Auto-detected sliders for tuning numeric parameters in your code

## Installation

1. Clone or download this repository

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:

```bash
streamlit run app.py
```

2. The application will open in your default web browser (usually at `http://localhost:8501`)

3. **Upload Data**:
   - Click on the file uploader in the sidebar
   - Or drag and drop a data file (CSV, JSON, Excel, or Parquet)
   - The data will be automatically loaded and displayed in the preview

4. **Write Algorithm**:
   - Use the code editor to write your Python algorithm
   - The uploaded data is available as `df` (pandas DataFrame)
   - Common libraries are pre-imported:
     - `pd` - pandas
     - `np` - numpy
     - `plt` - matplotlib.pyplot
     - `sns` - seaborn
     - `sklearn` - scikit-learn

5. **Run Algorithm**:
   - Click the "Run Algorithm" button
   - Results will be displayed in organized tabs:
     - **Output**: Console output and results
     - **Data**: DataFrames and data structures
     - **Variables**: All variables created during execution
     - **Visualizations**: Matplotlib plots and charts

## Parameter Tuning Sliders

When your code contains recognizable ML parameters, interactive sliders will appear. Toggle "Show Parameter Sliders" to enable them.

**Supported parameter patterns:**
- Learning rates: `learning_rate`, `alpha`, `beta`, `eta`, `epsilon`
- Counts: `n_clusters`, `n_estimators`, `n_neighbors`, `num_layers`
- Limits: `max_depth`, `max_iter`, `min_samples`
- Ratios: `test_size`, `dropout`, `split_ratio`
- Others: `epochs`, `batch_size`, `random_state`, `threshold`

**Example with sliders:**

```python
# These parameters will get auto-detected sliders
learning_rate = 0.01
n_clusters = 5
max_depth = 10
test_size = 0.2
epochs = 100

# K-Means clustering example
from sklearn.cluster import KMeans

model = KMeans(n_clusters=n_clusters, random_state=42)
model.fit(df.select_dtypes(include=['number']))
print(f"Cluster centers:\n{model.cluster_centers_}")
print(f"Labels: {model.labels_}")
```

Drag the sliders to adjust values - the code updates automatically!

## Example Code

```python
# Basic data exploration
print(f"Data shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(df.head())

# Statistical analysis
print(df.describe())

# Create a visualization
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
df.hist()
plt.show()

# Machine learning example
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Assuming you have target column 'target'
X = df.drop('target', axis=1)
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = LinearRegression()
model.fit(X_train, y_train)
print(f"R² Score: {model.score(X_test, y_test)}")
```

## Supported File Formats

- **CSV** (.csv): Comma-separated values
- **JSON** (.json, .jsonl): JavaScript Object Notation
- **Excel** (.xlsx, .xls): Microsoft Excel files
- **Parquet** (.parquet): Apache Parquet format

## Security Notes

- Code execution has a 30-second timeout
- Execution runs in a restricted namespace
- File system write access is not available
- Network access from user code is not available

## Requirements

- Python 3.8 or higher
- See `requirements.txt` for full dependency list

## Troubleshooting

- **File upload fails**: Make sure the file format is supported and the file is not corrupted
- **Code execution timeout**: Simplify your algorithm or break it into smaller parts
- **Import errors**: Only pre-loaded libraries are available. Check the list of available imports in the sidebar tips
- **Visualizations not showing**: Use `plt.show()` or return figure objects from your code

## License

This project is open source and available for use.
