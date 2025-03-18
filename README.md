# XYZ WACC Quackulator

A dynamic dashboard for visualizing WACC (Weighted Average Cost of Capital) data with a fun goose theme.

## Features

- Real-time WACC data visualization
- Animated time series graph
- Current WACC display
- Auto-refresh functionality
- Goose-themed interface

## Setup

1. Clone the repository
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the dashboard:
   ```bash
   python MNwacc_dashboard.py
   ```

## Dependencies

- Python 3.x
- Dash
- Pandas
- Plotly

## Configuration

The dashboard reads WACC data from an Excel file. Update the `EXCEL_PATH` in `MNwacc_dashboard.py` to point to your data source.