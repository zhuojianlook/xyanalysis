import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io

# Set up streamlit
st.title("GO Bargraph Heatmap - Hope Easy to use for Gary and XY")

# Upload functionality
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

# If a file is uploaded
if uploaded_file:
    # Extracting sheet names
    sheet_options = pd.ExcelFile(uploaded_file).sheet_names
    sheet_names = st.multiselect("Select the sheets you want to visualize:", options=sheet_options)

    # Getting headers for each sheet and asking user to select the conditions column
    condition_columns = []
    conditions_list = []  # List to store unique conditions from each sheet
    rename_dict_list = []  # List to store rename dictionaries for each sheet
    if sheet_names:
        for sheet in sheet_names:
            df_sample = pd.read_excel(uploaded_file, sheet_name=sheet, nrows=5)
            condition_column = st.selectbox(f"Select the condition column for {sheet}:", df_sample.columns)
            condition_columns.append(condition_column)
            conditions_list.append(df_sample.columns[0])  # Store the name of the first column for title
            
            # Rename y labels (conditions)
            unique_conditions = df_sample[condition_column].unique()
            rename_dict = {}
            for condition in unique_conditions:
                new_name = st.text_input(f"Rename '{condition}' from {sheet}:", condition)
                rename_dict[condition] = new_name
            rename_dict_list.append(rename_dict)

        # Options to specify graph details
        x_axis_label = st.text_input("Enter X-Axis Label:", "Counts")
        x_axis_font_size = st.slider("Select X-Axis Font Size:", 8, 20, 12)
        y_axis_font_size = st.slider("Select Y-Axis Font Size:", 8, 20, 12)
        graph_width, graph_height = st.slider("Select Graph Dimensions:", 5, 20, (14, 20))
        legend_width = st.slider("Select Legend Width:", 0.02, 0.5, 0.02)
        legend_height = st.slider("Select Legend Height:", 0.1, 1.0, 0.7)
        legend_scaling = st.slider("Select Legend Scaling (Font Size):", 10, 20, 14)
        color_scheme = st.selectbox("Select Color Scheme:", ["inferno", "viridis", "magma", "plasma"])

        # Plotting
        def plot_data():
            fig, axs = plt.subplots(len(sheet_names), 1, figsize=(graph_width, graph_height), sharex=True)
            fig.subplots_adjust(hspace=0.5, right=0.7)

            for index, (ax, sheet, condition_column, rename_dict) in enumerate(zip(axs, sheet_names, condition_columns, rename_dict_list)):
                df = pd.read_excel(uploaded_file, sheet_name=sheet)

                # Rename based on user input
                df[condition_column] = df[condition_column].replace(rename_dict)

                # Convert 'Count' column to numeric
                df['Count'] = pd.to_numeric(df['Count'], errors='coerce')
                df = df.dropna(subset=['Count'])
                df = df.sort_values(by='Count', ascending=False)

                # Create the bar plot
                sns.barplot(x='Count', y=condition_column, data=df, ax=ax,
                            palette=sns.color_palette(color_scheme, as_cmap=True)(df['Unnamed: 1'] / df['Unnamed: 1'].max()))

                ax.set_title(conditions_list[index], fontsize=16)
                ax.set_ylabel('', fontsize=y_axis_font_size)
                ax.set_xlabel(x_axis_label if index == len(sheet_names) - 1 else '', fontsize=x_axis_font_size)
                ax.xaxis.labelpad = 10  # Additional spacing for x-axis label
                ax.tick_params(axis='x', labelsize=x_axis_font_size)  # Set x-tick label size
                ax.grid(axis='x', linestyle='--', alpha=0.7)

            plt.tight_layout()

            # Add legend
            norm = plt.Normalize(df['Unnamed: 1'].min(), df['Unnamed: 1'].max())
            sm = plt.cm.ScalarMappable(cmap=color_scheme, norm=norm)
            sm.set_array([])
            cbar_ax = fig.add_axes([1.05, 0.15, legend_width, legend_height])
            cbar = fig.colorbar(sm, cax=cbar_ax, orientation='vertical')
            cbar.set_label('-log10(P-Value)', size=legend_scaling)
            cbar.ax.tick_params(labelsize=legend_scaling-2)  # A bit smaller than the legend label

            st.pyplot(fig)

            # Button to download as TIFF
            if st.button('Download Plot as TIFF'):
                buffer = io.BytesIO()
                fig.savefig(buffer, format="tiff", dpi=300, bbox_inches='tight')
                buffer.seek(0)
                st.download_button("Download TIFF", buffer, "plot.tiff")

        plot_data()

# End of the Streamlit app
