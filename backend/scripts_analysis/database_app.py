import streamlit as st

pages = {
    "Create Elements": [
        st.Page("./pages/create_driver.py", title="Create Driver"),
        st.Page("./pages/create_car.py", title="Create Car"),
        st.Page("./pages/create_track.py", title="Create Track"),
        st.Page("./pages/create_session.py", title="Create Session")
    ],
    "View Database": [
        st.Page("./pages/view_database.py", title="View Database"),
        st.Page("./pages/view_lap_plots.py", title="View Lap Plots"),
        st.Page("./pages/study_session.py", title="Study Session")
    ]
}

pg = st.navigation(pages)
pg.run()