import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
from datetime import datetime 

@st.cache_resource
def get_gspread_client():
    # Pull credentials from your Streamlit secrets
    creds_dict = dict(st.secrets["gcreds"]) 
    return gspread.service_account_from_dict(creds_dict)

@st.cache_data(ttl=3600)
def get_sheets():
    # gc = gspread.service_account(filename='./google_details.json')
    gc = get_gspread_client()

    # spreadsheet
    db = gc.open_by_key(st.secrets.GS.sheet_url)

    worksheet_names = [
        'trophies', 'rosters', 'players', 'games', 
        'offenseStats', 'defenseStats', 'staff', 
        'current_team', 'dates', 'homepage'
    ]

    result = {}
    for name in worksheet_names:
        ws = db.worksheet(name)
        result[name] = pd.DataFrame(ws.get_all_records())

    return result # returns a table of dataframes
# end of get_sheets()

# sheets
sheets = get_sheets()

# streamlit configuration
st.set_page_config(
    page_title="GWW Wildcats Flag Football Database",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        #teams = sheets['current_team'].get_all_records()
        teams = sheets['current_team'].to_dict(orient="records")
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

    dates = sheets['dates'].to_dict(orient="records")
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
    st.subheader("Major Upcoming Events")
    for line in games:
        st.write(line)
    # End of Tournament, Games and Events

    # Team Picture
    st.space(size="medium")
    homepage = sheets["homepage"].to_dict(orient="records")
    print(homepage)
    banner_link = str(homepage[-1]['display_url'])
    st.image(banner_link, width="content")
    st.space(size="medium")
    # End of Team Picture

    # Coaches
    staff = sheets['staff'].to_dict(orient="records")
    staff_names = []
    for line in staff:
        coach = f"{line["first"][0]}. {line["last"]}"
        staff_names.append(coach)

    st.subheader("Coaching Staff")
    
    coach_tabs = st.tabs(staff_names)
    for tab, line in zip(coach_tabs, staff):
        with tab:
            st.space(size="small")
            if not line["img_link"]:
                st.image("https://github.com/mrparkyrdsb/wildcatsflagdb/blob/main/src/placeholder.png?raw=true", width=96)
            else:
                st.image(line["img_link"], width=96)

            coach = f"{line["first"][0]}. {line["last"]}"
            st.write(coach)
    # end of coaches

    # School & Map
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
    # end of school & map


# end of home()

def trophies_page():
    trophies = sheets['trophies'].to_dict(orient="records")
    df_trophies = pd.DataFrame(trophies)
    
    # Streamlit elements written
    st.title("🏆 GWW Wildcats Trophies")
    st.dataframe(df_trophies, hide_index=True)
# end of trophies()

def games_page():
    # Grab data from Google Sheets
    games = sheets['games'].to_dict(orient="records")
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
    st.title("🛡 GWW Defensive Stats")
    st.space("small")

    defense = sheets['defenseStats'].to_dict(orient="records")
    df_defense = pd.DataFrame(defense) # turns defense in to pandas dataframe

    # Year Filter
    unique_year = set()
    for table in defense:
        row_year = table['Date'].split("/")[-1]
        unique_year.add(row_year)
    
    unique_year = sorted(unique_year, reverse=True)
    year_choice = st.selectbox(
        label="Select a year",
        index=None,
        options=unique_year,
        placeholder="Year"
    )

    if year_choice is not None:
        mask = df_defense['Date'].str.endswith(year_choice)
        df_defense = df_defense[mask]
    
    df_defense['Athlete'] = df_defense.apply(lambda x: f"{x['First']} {x['Last'][0]} ({str(x['SN'])[-1:-5:-1]})", axis=1)
    df_defense = df_defense.drop(columns=['First'])
    df_defense = df_defense.drop(columns=['Last'])

    # Athlete Filter
    athlete_choice = st.selectbox(
        label="Select an athlete",
        index=None,
        options=df_defense['Athlete'].unique(),
        placeholder="Athlete Name"
    )

    if athlete_choice is not None:
        mask = df_defense['Athlete'] == athlete_choice
        df_defense = df_defense[mask]

    df_defense = df_defense[['SN','Athlete','Flags','Deflections','Interceptions','Sacks','Safety', 'Touchdowns']].groupby('SN').agg({
        'Athlete': 'first', 
        'Flags': 'sum',
        'Deflections': 'sum',
        'Interceptions': 'sum',
        'Sacks': 'sum',
        'Safety': 'sum',
        'Touchdowns': 'sum'
    })

    st.space("small")
    if year_choice and athlete_choice:
        st.subheader(f"{athlete_choice} - {year_choice} stats")
    st.dataframe(df_defense, hide_index=True)
# end of defense_page()

def offense_page():
    offense = sheets['offenseStats'].to_dict(orient="records")
    df_offense = pd.DataFrame(offense)
    df_offense['Athlete'] = df_offense.apply(lambda x: f"{x['First']} {x['Last'][0]} ({str(x['SN'])[-1:-5:-1]})", axis=1)
    df_offense = df_offense.drop(columns=['First'])
    df_offense = df_offense.drop(columns=['Last'])

    # Streamlit contents
    st.header("🏈 GWW Offensive Stats")

    col1, col2 = st.columns(2)
    # Year Filter
    with col1:
        unique_year = set()
        for table in offense:
            row_year = table['Date'].split("/")[-1]
            unique_year.add(row_year)
        
        unique_year = sorted(unique_year, reverse=True)
        year_choice = st.selectbox(
            label="Select a year",
            index=None,
            options=unique_year,
            placeholder="Year"
        )

    # Athlete Filter
    with col2:
        athlete_choice = st.selectbox(
            label="Select an athlete",
            index=None,
            options=df_offense['Athlete'].unique(),
            placeholder="Athlete Name"
        )
    # end of filter contents

    df_passing = df_offense[['Date', 'SN', 'Athlete', 'p_TD', 'p_INT', 'p_1st', 'p_1pt', 'p_2pt', 'p_attempts', 'p_completions']]
    df_rushing = df_offense[['Date', 'SN', 'Athlete', 'rb_td', 'rb_1st', 'rb_1pt', 'rb_2pt', 'rb_attempts']]
    df_receiving = df_offense[['Date', 'SN', 'Athlete', 'wr_rec', 'wr_td', 'wr_1st', 'wr_1pt', 'wr_2pt', 'wr_drops']]

    if year_choice is not None:
        mask = df_passing['Date'].str.endswith(year_choice)
        df_passing = df_passing[mask]
        mask = df_rushing['Date'].str.endswith(year_choice)
        df_rushing = df_rushing[mask]
        mask = df_receiving['Date'].str.endswith(year_choice)
        df_receiving = df_receiving[mask]
    
    if athlete_choice is not None:
        mask = df_passing['Athlete'].str.endswith(athlete_choice)
        df_passing = df_passing[mask]
        mask = df_rushing['Athlete'].str.endswith(athlete_choice)
        df_rushing = df_rushing[mask]
        mask = df_receiving['Athlete'].str.endswith(athlete_choice)
        df_receiving = df_receiving[mask]       
    
    df_passing = df_passing[df_passing[['p_TD', 'p_INT', 'p_1st', 'p_1pt', 'p_2pt', 'p_attempts', 'p_completions']].sum(axis=1) > 0]
    df_rushing = df_rushing[df_rushing[['rb_td', 'rb_1st', 'rb_1pt', 'rb_2pt', 'rb_attempts']].sum(axis=1) > 0]
    df_receiving = df_receiving[df_receiving[['wr_rec', 'wr_td', 'wr_1st', 'wr_1pt', 'wr_2pt', 'wr_drops']].sum(axis=1) > 0]

    df_passing = df_passing[['SN', 'Athlete', 'p_TD', 'p_INT', 'p_1st', 'p_1pt', 'p_2pt', 'p_attempts', 'p_completions']].groupby('SN').agg({
        'Athlete': 'first', 
        'p_TD': 'sum',
        'p_INT': 'sum',
        'p_1pt': 'sum',
        'p_2pt': 'sum',
        'p_attempts': 'sum',
        'p_completions': 'sum'
    })

    df_rushing = df_rushing[['SN', 'Athlete', 'rb_td', 'rb_1st', 'rb_1pt', 'rb_2pt', 'rb_attempts']].groupby('SN').agg({
        'Athlete': 'first', 
        'rb_td': 'sum',
        'rb_1st': 'sum',
        'rb_1pt': 'sum',
        'rb_2pt': 'sum',
        'rb_attempts': 'sum'
    })

    df_receiving = df_receiving[['SN', 'Athlete', 'wr_rec', 'wr_td', 'wr_1st', 'wr_1pt', 'wr_2pt', 'wr_drops']].groupby('SN').agg({
        'Athlete': 'first', 
        'wr_rec': 'sum',
        'wr_td': 'sum',
        'wr_1st': 'sum',
        'wr_1pt': 'sum',
        'wr_2pt': 'sum',
        'wr_drops': 'sum',
    })

    df_passing = df_passing.rename(columns={
        'p_TD': 'Passing TD',
        'p_INT': 'Interceptions', 
        'p_1st': '1st Downs', 
        'p_1pt': '1pt Converts', 
        'p_2pt': '2pt Converts', 
        'p_attempts': 'Passing Attempts', 
        'p_completions': 'Completion'
    })

    df_rushing = df_rushing.rename(columns={
        'rb_td': 'Rushing TD', 
        'rb_1st': '1st Downs', 
        'rb_1pt': '1pt Converts', 
        'rb_2pt': '2pt Converts', 
        'rb_attempts': 'Rushing Attempts'
    })

    df_receiving = df_receiving.rename(columns={
        'wr_rec': 'Receptions', 
        'wr_td': 'Receiving TD', 
        'wr_1st': '1st Downs', 
        'wr_1pt': '1pt Converts', 
        'wr_2pt': '2pt Converts', 
        'wr_drops': 'Drops'
    })

    st.space("small")

    if year_choice is None and athlete_choice is None:
        st.subheader("Passing Stats")
        st.dataframe(df_passing, column_config={"SN":None, "Date":None},hide_index=True)
        st.subheader("Rushing Stats")
        st.dataframe(df_rushing, column_config={"SN":None, "Date":None},hide_index=True)
        st.subheader("Receiving Stats")
        st.dataframe(df_receiving, column_config={"SN":None, "Date":None},hide_index=True)
    elif year_choice is not None and athlete_choice is None:
        st.subheader(f"{year_choice} Passing Stats")
        st.dataframe(df_passing, column_config={"SN":None, "Date":None},hide_index=True)
        st.subheader(f"{year_choice} Rushing Stats")
        st.dataframe(df_rushing, column_config={"SN":None, "Date":None},hide_index=True)
        st.subheader(f"{year_choice} Receiving Stats")
        st.dataframe(df_receiving, column_config={"SN":None, "Date":None},hide_index=True)
    elif year_choice is None and athlete_choice is not None:
        st.subheader(f"Passing Stats for {athlete_choice}.")
        st.dataframe(df_passing, column_config={"SN":None, "Date":None},hide_index=True)
        st.subheader(f"Rushing Stats for {athlete_choice}.")
        st.dataframe(df_rushing, column_config={"SN":None, "Date":None},hide_index=True)
        st.subheader(f"Receiving Stats for {athlete_choice}.")
        st.dataframe(df_receiving, column_config={"SN":None, "Date":None},hide_index=True)
    elif year_choice is not None and athlete_choice is not None:
        st.subheader(f"{year_choice} Passing Stats for {athlete_choice}.")
        st.dataframe(df_passing, column_config={"SN":None, "Date":None},hide_index=True)
        st.subheader(f"{year_choice} Rushing Stats for {athlete_choice}.")
        st.dataframe(df_rushing, column_config={"SN":None, "Date":None},hide_index=True)
        st.subheader(f"{year_choice} Receiving Stats for {athlete_choice}.")
        st.dataframe(df_receiving, column_config={"SN":None, "Date":None},hide_index=True)
# end of offense_page()

pages = st.navigation([
    st.Page(home, title="Home", icon="🏠"),
    st.Page(trophies_page, title="Wildcats Trophies", icon="🏆"),
    st.Page(games_page, title="Game Results", icon=":material/sports_score:"),
    st.Page(offense_page, title="Offense Stats", icon="🏈"),
    st.Page(defense_page, title="Defense Stats", icon="🛡")
])

if st.sidebar.button("Refresh Data from Google"):
    st.cache_data.clear()
    st.rerun()

pages.run()