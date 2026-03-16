import gspread
import streamlit as st
import pandas as pd

# replace line 4 with dictionary when deploying
gc = gspread.service_account(filename='./google_details.json')

# spreadsheet
db = gc.open_by_key("1xq3H5Z5Ky5JfKLXx88UHA8XsyAwf9hxU_dz-jfll5wY")\

# sheets
sheets = {
    'trophies' : db.worksheet("trophies"),
    'rosters' : db.worksheet("rosters"),
    'players' : db.worksheet("players"),
    'games' : db.worksheet("games"),
    'offenseStats' : db.worksheet("offenseStats"),
    'defenseStats' : db.worksheet("defenseStats")
}

st.write("Hello, World!")

# sheet 0 : trophies
trophies = sheets['trophies'].get_all_records()
df_trophies = pd.DataFrame(trophies)
st.write(df_trophies)

# Offensive Stats
o_stats = sheets['offenseStats'].get_all_records()
print(o_stats)
