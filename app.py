import gspread
import streamlit as st
import pandas as pd
from datetime import datetime 

# gc = gspread.service_account(filename='./google_details.json')
creds_dict = dict(st.secrets.gcreds)
gc = gspread.service_account_from_dict(creds_dict)

# spreadsheet
db = gc.open_by_key(st.secrets.GS.sheet_url)

# sheets
sheets = {
    'trophies' : db.worksheet("trophies"),
    'rosters' : db.worksheet("rosters"),
    'players' : db.worksheet("players"),
    'games' : db.worksheet("games"),
    'offenseStats' : db.worksheet("offenseStats"),
    'defenseStats' : db.worksheet("defenseStats"),
    'staff' : db.worksheet("staff"),
    'current_team' : db.worksheet("current_team"),
    'dates' : db.worksheet("dates")
}

# streamlit configuration
st.set_page_config(
    page_title="GWW Wildcats Flag Football Database",
    layout="wide",
    initial_sidebar_state="expanded"
)

def home():
    # Header
    col1, col2 = st.columns([1,8])
    with col1:
        st.image("https://github.com/mrparkyrdsb/wildcatsflagdb/blob/main/src/wildcat.png?raw=true", width="content")
    
    with col2:
        st.title("Wildcats Flag Football Database")
        st.write("Dr. G.W. Williams Secondary School's Flag Football Program")
    # end of Header

    # Quick Info
    q_col1, q_col2, q_col3 = st.columns([1,2,2])
    with q_col1:
        current_month = datetime.now().month
        yraa_season = ""
        if current_month >= 11 or current_month < 3:
            yraa_season = "Winter"
        elif current_month >= 9 and current_month < 11:
            yraa_season = "Fall"
        elif current_month >= 3 and current_month < 7:
            yraa_season = "Spring"
        
        if yraa_season:
            st.write(f"Current YRAA Season: **{yraa_season}**")
    
    with q_col2:
        teams_col1, teams_col2 = st.columns(2)
        teams = sheets['current_team'].get_all_records()
        team5s = []
        team7s = []
        current_year = datetime.now().year
        for table in teams:
            if table['year'] == current_year and table['season'].lower() == yraa_season.lower():
                current_team = f"{table['division'].capitalize()} {table['identity'].capitalize()} {table['format']}"
                if table['format'] == '5v5':
                    team5s.append(current_team)
                elif table['format'] == '7v7':
                    team7s.append(current_team)

        with teams_col1:
            if team5s:
                st.write("**5v5 Teams:**")
                for team in team5s:
                    st.write(f"- {team}")
            else:
                st.write("No 5v5 team this season")
        
        with teams_col2:
            if team7s:
                st.write("**7v7 Teams:**")
                for team in team7s:
                    st.write(f"- {team}")
            else:
                st.write("No 7v7 team this season")

    dates = sheets['dates'].get_all_records()
    tryouts = []
    games = []
    other_events = []
    with q_col3:
        for table in dates:
            event = f"- {table['title']} @ {table['location']} **[{table['date']}]**"
            if table['event'] == 'tryouts':
                event_date = datetime.strptime(table['date'], "%m/%d/%Y")
                if event_date >= datetime.now():
                    tryouts.append(event)
            elif table['event'] in {'exhibition', 'yraa', 'tournament'}:
                games.append(event)
            else:
                other_events.append(event)
        
        if tryouts:
            st.write("**Tryouts:**")
            for line in tryouts:
                st.write(line)
        else:
            st.write("No tryouts scheduled.")
    # End of quick info

    # Tournament, Games and Events
    st.subheader("Major Events")
    for line in games:
        st.write(line)

    st.space(size="medium")
    #st.image("./src/team.jpg", width="stretch", caption="William's Girls Flag Classic 03/05/2026")
    st.image("https://github.com/mrparkyrdsb/wildcatsflagdb/blob/main/src/team.jpg?raw=true", width="stretch", caption="William's Girls Flag Classic 03/05/2026")
    st.space(size="medium")

    school_map = pd.DataFrame({
        'lat': [44.0151309],
        'lon': [-79.4637783],
        'name': ['Dr. G.W. Williams Secondary School']    
    })

    st.space(size="medium")
    st.divider()
    map_col1, map_col2 = st.columns([1,3])
    with map_col1:
        st.header("Dr. G.W. Williams Secondary School")
        st.markdown("Address: [11 Spring Farm Rd, Aurora, ON L4G 7W2](https://maps.app.goo.gl/cBh6dBVyHc5YP91w9)")

    with map_col2:
        st.map(school_map, size=40, color='#ff4b4b', zoom=11)


# end of home()

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
    st.Page(home, title="Home", icon="🏠"),
    st.Page(trophies_page, title="Wildcats Trophies", icon="🏆"),
    st.Page(games_page, title="Game Results", icon=":material/sports_score:"),
    st.Page(defense_page, title="Defense Stats", icon="🛡")
])

pages.run()

# # Offensive Stats
# o_stats = sheets['offenseStats'].get_all_records()
# print(o_stats)
