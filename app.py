import gspread
import streamlit as st
import pandas as pd

# replace line 4 with dictionary when deploying
gc = gspread.service_account(filename='./google_details.json')

# spreadsheet
db = gc.open_by_key("1xq3H5Z5Ky5JfKLXx88UHA8XsyAwf9hxU_dz-jfll5wY")

# sheets
sheets = {
    'trophies' : db.worksheet("trophies"),
    'rosters' : db.worksheet("rosters"),
    'players' : db.worksheet("players"),
    'games' : db.worksheet("games"),
    'offenseStats' : db.worksheet("offenseStats"),
    'defenseStats' : db.worksheet("defenseStats")
}

# streamlit configuration
st.set_page_config(
    page_title="GWW Wildcats Flag Football Database",
    layout="wide",
    initial_sidebar_state="expanded"
)

def trophies_page():
    trophies = sheets['trophies'].get_all_records()
    df_trophies = pd.DataFrame(trophies)
    
    # Streamlit elements written
    st.title("🏆 GWW Wildcats Trophies")
    st.dataframe(df_trophies, hide_index=True)
# end of trophies()

def games_page():
    # Grab data from Google Sheets
    games = sheets['games'].get_all_records()
    # Set up Dataframe
    df_games = pd.DataFrame(games)
    df_games['Date'] = pd.to_datetime(df_games['Date'])
    df_games = df_games.sort_values(by='Date', ascending=False)
   
    # Streamit elements
    st.title(":material/sports_score: Game Results")

    # Column
    col1, col2 = st.columns(2)

    with col1:
        # Choose a format
        format_choice = st.selectbox(
            label="Choose a game format",
            index=None,
            options=df_games['Format'].unique(),
            placeholder="Choose a format:"
        )

    with col2:
        # Choose a team
        team_choice = st.selectbox(
            label="Filter by team",
            index=None,
            options=df_games['GWWTeams'].unique(),
            placeholder="Choose a GWW team:"
        )

    if format_choice is not None and team_choice is not None:
        mask = (df_games['GWWTeams'] == team_choice) & (df_games['Format'] == format_choice)
        filtered_games = df_games[mask]
        st.write("Results:")
        st.dataframe(filtered_games, hide_index=True)
# end of games()

def defense_page():
    defense = sheets['defenseStats'].get_all_records()
    df_defense = pd.DataFrame(defense) # turns defense in to pandas dataframe
    df_defense = df_defense.drop(columns=['Date'])
    df_defense['Athlete'] = df_defense.apply(lambda x: f"{x['First']} {x['Last'][0]}.", axis=1)
    df_defense = df_defense.drop(columns=['First'])
    df_defense = df_defense.drop(columns=['Last'])
    df_defense = df_defense[['SN','Athlete','Flags','Deflections','Interceptions','Sacks','Touchdowns']].groupby('SN').agg({
        'Athlete': 'first', 
        'Flags': 'sum',
        'Deflections': 'sum',
        'Interceptions': 'sum',
        'Sacks': 'sum',
        'Touchdowns': 'sum'
    })
    #df_defense = df_defense.fillna(0)

    st.title("🛡 GWW Defensive Stats")
    st.dataframe(df_defense, hide_index=True)
# end of defense_page()

pages = st.navigation([
    st.Page(trophies_page, title="Wildcats Trophies", icon="🏆"),
    st.Page(games_page, title="Game Results", icon=":material/sports_score:"),
    st.Page(defense_page, title="Defense Stats", icon="🛡")
])

pages.run()

# # Offensive Stats
# o_stats = sheets['offenseStats'].get_all_records()
# print(o_stats)
