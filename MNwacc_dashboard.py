import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objects as go
import base64
import dash.dependencies as dd
import io
from datetime import datetime
import os

# File path for the WACC Excel file
EXCEL_PATH = '/Users/staceymitchell/Library/CloudStorage/GoogleDrive-smitchell@block.xyz/Shared drives/Treasury/Automation Workstreams/WACC.xlsx'

def prepare_dataframe():
    """Read data from Excel file and prepare DataFrame"""
    try:
        print("\n=== Loading Excel File ===")
        print(f"Reading from: {EXCEL_PATH}")
        
        # Read the Excel file
        df = pd.read_excel(EXCEL_PATH)
        print("\nRaw Excel Data:")
        print(df.tail())  # Show the last few rows of raw data
        
        # Create final DataFrame with the date and value columns
        df_final = pd.DataFrame({
            'date': pd.to_datetime(df['Date']),  # Convert date column
            'wacc': df['Value'].astype(float)  # Convert WACC values to float
        })
        
        # Sort by date and reset index
        df_final = df_final.sort_values('date').reset_index(drop=True)
        
        print("\nProcessed Data:")
        print(df_final.tail())  # Show the last few rows of processed data
        print(f"\nTotal rows: {len(df_final)}")
        print(f"Date range: {df_final['date'].min()} to {df_final['date'].max()}")
        print(f"Latest WACC value: {df_final['wacc'].iloc[-1]:.2f}%")
        
        return df_final
    except Exception as e:
        print(f"\nError in prepare_dataframe: {e}")
        if 'df' in locals():
            print("\nDataFrame head:")
            print(df.head())
        raise

# Initial data load
print("\n=== Initial Data Load ===")
df = prepare_dataframe()

# Create the Dash application
app = dash.Dash(__name__)
server = app.server

# Encode background Goose GIF
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    goose_gif = os.path.join(script_dir, "goose.gif")
    with open(goose_gif, 'rb') as f:
        encoded_goose = base64.b64encode(f.read()).decode('ascii')
except Exception as e:
    print(f"Warning: Error loading goose.gif: {e}")
    encoded_goose = ""

# Animation settings
animation_speed = 150
pause_duration = 15000

# Styles
background_style = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "width": "100%",
    "height": "100%",
    "background": f"url('data:image/gif;base64,{encoded_goose}')" if encoded_goose else "black",
    "backgroundSize": "cover",
    "backgroundPosition": "center",
    "opacity": "0.8",
    "zIndex": -1
}

refresh_button_style = {
    'backgroundColor': 'yellow',
    'color': 'black',
    'padding': '10px 20px',
    'border': 'none',
    'borderRadius': '5px',
    'cursor': 'pointer',
    'fontSize': '16px',
    'fontWeight': 'bold',
    'marginTop': '10px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'transition': 'transform 0.1s ease',
    ':hover': {
        'transform': 'scale(1.05)'
    }
}

current_wacc_style = {
    'color': 'yellow',
    'fontSize': '64px',  # Increased font size
    'fontWeight': 'bold',
    'textShadow': '2px 2px 4px black',
    'marginTop': '20px',
    'marginBottom': '20px',
    'textAlign': 'center',
    'width': '100%',
    'padding': '10px',
    'backgroundColor': 'rgba(0, 0, 0, 0.5)',
    'borderRadius': '10px',
}

# Layout
app.layout = html.Div([
    html.Div(style=background_style),
    html.Div(
        style={
            "height": "100vh",
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "flexDirection": "column",
            "padding": "20px",
            "position": "relative",
            "zIndex": 1
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "marginBottom": "20px",
                    "background": "rgba(0,0,0,0.5)",
                    "padding": "20px",
                    "borderRadius": "10px",
                    "width": "90%",
                    "justifyContent": "center"
                },
                children=[
                    html.H1(
                        "XYZ WACC QUACKULATOR",
                        style={
                            "color": "yellow",
                            "fontSize": "32px",
                            "textShadow": "3px 3px 10px black",
                            "margin": 0
                        },
                    ),
                ],
            ),
            html.Div(
                id='current-wacc-display',
                style=current_wacc_style
            ),
            html.Div(
                style={
                    "width": "90%",
                    "background": "rgba(0,0,0,0.5)",
                    "padding": "20px",
                    "borderRadius": "10px"
                },
                children=[
                    dcc.Graph(
                        id="wacc-chart",
                        config={"displayModeBar": False},
                        style={"width": "100%", "height": "70vh"},
                    ),
                ]
            ),
            html.Button(
                'Refresh Data',
                id='refresh-button',
                style=refresh_button_style
            ),
            html.Div(
                id='last-refresh-time',
                style={
                    'color': 'white',
                    'marginTop': '10px',
                    'fontSize': '14px'
                }
            ),
            dcc.Store(id='data-store', data=df.to_dict('records')),  # Initialize with data
            dcc.Store(id='animation-state', data={'current_index': len(df) - 1, 'max_points': len(df)}),  # Initialize animation state
            dcc.Interval(
                id='animation-interval',
                interval=animation_speed,
                n_intervals=0
            ),
        ],
    )
])

@app.callback(
    [dd.Output('data-store', 'data'),
     dd.Output('animation-state', 'data'),
     dd.Output('last-refresh-time', 'children')],
    [dd.Input('refresh-button', 'n_clicks')],
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    if n_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update
    
    try:
        print("\n=== Refreshing Data ===")
        new_df = prepare_dataframe()
        
        # Store the data with proper date formatting
        data = [{
            'date': row['date'].strftime('%Y-%m-%d %H:%M:%S'),
            'wacc': float(row['wacc'])  # Ensure WACC is stored as float
        } for _, row in new_df.iterrows()]
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        animation_state = {'current_index': len(data) - 1, 'max_points': len(data)}
        
        print(f"\nStored {len(data)} data points")
        print(f"Latest stored WACC: {data[-1]['wacc']:.2f}%")
        
        return data, animation_state, f"Last refreshed: {current_time}"
    
    except Exception as e:
        print(f"\nError in refresh_data: {e}")
        return dash.no_update, dash.no_update, f"Error refreshing data: {str(e)}"

@app.callback(
    [dd.Output("wacc-chart", "figure"),
     dd.Output("current-wacc-display", "children")],
    [dd.Input("animation-interval", "n_intervals"),
     dd.Input("data-store", "data"),
     dd.Input("animation-state", "data")]
)
def update_graph(n_intervals, stored_data, animation_state):
    try:
        if stored_data is None:
            return dash.no_update, "Loading..."
            
        current_df = pd.DataFrame(stored_data)
        current_df['date'] = pd.to_datetime(current_df['date'])
        
        total_points = len(current_df)
        if animation_state is not None:
            current_index = animation_state.get('current_index', n_intervals)
        else:
            current_index = min(n_intervals if n_intervals is not None else 0, total_points - 1)

        current_index = min(max(0, current_index), total_points - 1)
        display_df = current_df.iloc[:current_index + 1]
        
        fig = go.Figure()

        # WACC Line
        fig.add_trace(
            go.Scatter(
                x=display_df["date"],
                y=display_df["wacc"],
                mode="lines+markers",
                line=dict(color="white", width=3, shape="spline"),
                marker=dict(size=8, color="white"),
                name="WACC",
            )
        )

        # Current point highlight
        if not display_df.empty:
            current_wacc = display_df["wacc"].iloc[-1]
            last_x = display_df["date"].iloc[-1]
            
            # Make the last point larger and more prominent
            fig.add_trace(
                go.Scatter(
                    x=[last_x],
                    y=[current_wacc],
                    mode="markers+text",
                    marker=dict(size=24, color="yellow", line=dict(color="red", width=4)),
                    text=[f"{current_wacc:.2f}%"],
                    textfont=dict(
                        size=24,  # Increased text size
                        color="yellow",
                    ),
                    textposition="top center",
                    showlegend=False,
                )
            )
            
            # Update current WACC display with label and value
            current_wacc_display = f"Current WACC: {current_wacc:.2f}%"
        else:
            current_wacc_display = "Loading..."

        fig.update_layout(
            title="",
            xaxis_title="Date",
            yaxis_title="WACC (%)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0.2)",
            font=dict(size=14, color="white"),
            margin=dict(l=50, r=50, t=50, b=50),
            template="plotly_dark",
            xaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                tickcolor="white",
                tickfont=dict(color="white"),
                showgrid=True,
            ),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                tickcolor="white",
                tickfont=dict(color="white"),
                showgrid=True,
            ),
        )

        return fig, current_wacc_display
    except Exception as e:
        print(f"\nError in update_graph: {e}")
        return dash.no_update, dash.no_update

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8051))
    app.run(debug=True, host='0.0.0.0', port=port)