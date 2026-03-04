import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# Assumptions:
# - workplaces is already defined and imported
# - workplaces is a list of objects
# - each workplace has:
#     .name
#     .input_WIP
#     .capa_per_day
#     .df  (pandas DataFrame to display)
# --------------------------------------------------

st.set_page_config(layout="wide")

st.title("Workplace Dashboard")


def build_webpage(workplaces, production_orders, opcs):
    """
    Builds and displays a workplace dashboard web page using Streamlit, providing the
    user interactive tools to visualize and modify workplace-related data such as
    work in progress (WIP) and daily capacities.

    The dashboard includes multiple features to interactively explore and edit data:
    - DataFrame selection for workplaces
    - Bar plots showcasing work in progress (WIP) per workplace
    - Editable table for modifying workplace capacities

    It uses the provided workplaces, production orders, and operational process controls
    (OPCs) to structure and display the respective data.

    :param workplaces: A list of workplace objects, where each object contains
        the name, associated data (in a DataFrame), input work in progress (input_WIP),
        and capacity per day (capa_per_day).
    :type workplaces: list
    :param production_orders: A list of production orders that relate to the operations
        and workplaces being displayed in the dashboard.
    :type production_orders: list
    :param opcs: A list of operational process controls, which may influence or
        be referenced by workplace operations.
    :type opcs: list
    :return: None. The function generates and displays the dashboard in the Streamlit app.
    :rtype: None
    """
    # --------------------------------------------------
    # Sidebar: DataFrame selector
    # --------------------------------------------------

    workplace_names = [wp.name for wp in workplaces]
    selected_name = st.sidebar.selectbox("Select Workplace", workplace_names)

    selected_workplace = next(wp for wp in workplaces if wp.name == selected_name)

    st.subheader(f"DataFrame: {selected_workplace.name}")
    st.dataframe(selected_workplace.df, use_container_width=True)

    # --------------------------------------------------
    # Bar Plot
    # --------------------------------------------------

    st.subheader("Input WIP per Workplace")

    names = [wp.name for wp in workplaces]
    wip_lengths = [len(wp.input_WIP) for wp in workplaces]

    fig, ax = plt.subplots()
    ax.bar(names, wip_lengths)
    ax.set_xlabel("Workplace")
    ax.set_ylabel("Length of input_WIP")
    ax.set_xticklabels(names, rotation=45, ha="right")

    st.pyplot(fig)

    # --------------------------------------------------
    # Capacity Editor Table
    # --------------------------------------------------

    st.subheader("Edit Capacity per Day")

    capa_df = pd.DataFrame({
        "Workplace": [wp.name for wp in workplaces],
        "Capacity per Day": [float(wp.capa_per_day) for wp in workplaces]
    })

    edited_df = st.data_editor(
        capa_df,
        column_config={
            "Capacity per Day": st.column_config.NumberColumn(
                "Capacity per Day",
                min_value=0.0,
                step=0.1,
                format="%.2f"
            )
        },
        use_container_width=True,
        hide_index=True
    )

    # Apply changes back to objects
    if st.button("Apply Capacity Changes"):
        for wp in workplaces:
            new_value = edited_df.loc[
                edited_df["Workplace"] == wp.name,
                "Capacity per Day"
            ].values[0]
            wp.capa_per_day = float(new_value)

        st.success("Capacities updated successfully.")
