import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_sorted_combined_bar_graphs_adjusted_legend(df_list):
    # Set up the figure and axes
    fig, axs = plt.subplots(4, 1, figsize=(14, 20), sharex=True)
    fig.subplots_adjust(hspace=0.5, right=0.7)
    
    conditions = ['Cellular Component', 'Biological Process', 'Molecular Function', 'Reactome Pathways']

    # Loop over each condition to plot the bar graphs in one figure
    for index, (ax, df, condition) in enumerate(zip(axs, df_list, conditions)):
        # Convert 'Count' column to numeric
        df['Count'] = pd.to_numeric(df['Count'], errors='coerce')
        df = df.dropna(subset=['Count'])
        df = df.sort_values(by='Count', ascending=False)
        
        sns.barplot(x='Count', y=condition, data=df, ax=ax, 
                    palette=sns.color_palette("inferno", as_cmap=True)(df['Unnamed: 1']/df['Unnamed: 1'].max()))

        # Set title and labels
        ax.set_title(condition)
        ax.set_ylabel('')
        
        # Set x-axis label for the last subplot
        if index == len(conditions) - 1:
            ax.set_xlabel('Counts')
        else:
            ax.set_xlabel('')

        ax.grid(axis='x', linestyle='--', alpha=0.7)

    # Adjust the layout
    plt.tight_layout()
    
    # Add legend for -log10(P-Value)
    norm = plt.Normalize(df['Unnamed: 1'].min(), df['Unnamed: 1'].max())
    sm = plt.cm.ScalarMappable(cmap="inferno", norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes([1.05, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='vertical')
    cbar.set_label('-log10(P-Value)', size=16)
    cbar.ax.tick_params(labelsize=14)

    # Display the plot in Streamlit
    st.pyplot(fig)

# Streamlit UI
st.title("Combined Bar Graphs App")
st.write("Upload an Excel file to generate combined bar graphs.")

# Upload the Excel file through Streamlit
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])

if uploaded_file:
    # Read all sheets
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())

    required_sheets = ['Sheet1', 'Sheet2', 'Sheet3', 'Sheet4']
    if set(required_sheets).issubset(sheet_names):
        df_list = [all_sheets[sheet] for sheet in required_sheets]
        plot_sorted_combined_bar_graphs_adjusted_legend(df_list)
    else:
        st.write("Please upload an Excel file with the required sheet names: Sheet1, Sheet2, Sheet3, and Sheet4.")
