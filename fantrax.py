#import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os

def add_total_games(df):
    for col in df.columns:
        if col not in ['Player','Status']:
            df[col] = df[col].notnull().astype('int')

    df['Games'] = pd.Series([0]*df.shape[0],)
    for col in df.columns:
        if col not in ['Player','Status','Games']:
            df['Games'] += df[col]

    return df


def get_teams_categories():
    ytd = pd.read_csv('./data/fantrax_ytd.csv')
    projected = pd.read_csv('./data/fantrax_projected.csv')
    sched = pd.read_csv('./data/fantrax_sched.csv')

    ytd.drop(['Opponent', 'Score', '% Owned', '+/-', 'GP', 'Rk', 'MIN'], axis=1, inplace=True)
    sched.drop(['Team', 'Status', 'Position', 'Rk', 'Score', '% Owned', '+/-'], inplace=True,axis=1)
    
    sched = add_total_games(sched)

    currentPeriodDates = sched.columns[1:-1]

    projectedClean = projected.drop(['Team','MIN', 'Position', 'Status', 'FG%', 'FT%', 'Rk', 'Opponent', 'Score', '% Owned', '+/-'],axis=1)
    ytdClean = ytd.drop(['FG%', 'FT%'],axis=1)
    mergedStats = ytdClean.merge(projectedClean, on='Player', suffixes=('_ytd', '_projected'))
    mergedStats = mergedStats.merge(sched, on='Player',)
    mergedStats.head()

    mergedStatsGrouped = mergedStats.copy()
    mergedStatsGrouped.drop(['Team', 'Position','GP'], axis=1, inplace=True)
    for col in mergedStatsGrouped.columns:
        if col not in ['Player','Team','Position', 'Status'] and col not in currentPeriodDates and col != 'Games':
            mergedStatsGrouped[col+'_Fact'] = mergedStatsGrouped[col]*mergedStatsGrouped['Games']
            mergedStatsGrouped.drop(col, axis=1, inplace=True)

    aggDict = {
        
    }

    for date in currentPeriodDates:
        aggDict[str(date)] = 'sum'
    aggDict['Games'] = 'sum'
    for col in mergedStatsGrouped.columns:
        if col not in ['Player','Team','Position', 'Status'] and col not in aggDict.keys():
            aggDict[col] = 'sum'
    mergedStatsGrouped = mergedStatsGrouped.groupby('Status', as_index=False).agg(aggDict)
    mergedStatsGrouped['FG%'] = mergedStatsGrouped['FGM_ytd_Fact']/mergedStatsGrouped['FGA_ytd_Fact']*100
    mergedStatsGrouped['FT%'] = mergedStatsGrouped['FTM_ytd_Fact']/mergedStatsGrouped['FTA_ytd_Fact']*100
    mergedStatsGrouped

    mergedStatsGroupedOnlyYtd = mergedStatsGrouped.copy()
    for col in mergedStatsGroupedOnlyYtd.columns:
        if col.endswith('_projected_Fact') or col in currentPeriodDates:
           mergedStatsGroupedOnlyYtd.drop(col, axis=1, inplace=True)

    mergedStatsGroupedOnlyProj = mergedStatsGrouped.copy()
    for col in mergedStatsGroupedOnlyProj.columns:
        if col.endswith('_ytd_Fact') or col in currentPeriodDates:
           mergedStatsGroupedOnlyProj.drop(col, axis=1, inplace=True)

    return mergedStatsGroupedOnlyYtd, mergedStatsGroupedOnlyProj

def get_players_mean(fact=False):
    players = pd.read_csv('./data/Fantrax-players.csv')
    dates = pd.read_csv('./data/nba-2018-UTC-08.csv')

    dates.drop(['Round Number', 'Location', 'Result'],axis=1, inplace=True)
    dates['Date'] = pd.to_datetime(dates['Date'])

    nameToAbv = {}
    nameToAbv['Hawks'] = 'ATL'
    nameToAbv['Nets'] = 'BKN'
    nameToAbv['Celtics'] = 'BOS'
    nameToAbv['Hornets'] = 'CHA'
    nameToAbv['Bulls'] = 'CHI'
    nameToAbv['Cavaliers'] = 'CLE'
    nameToAbv['Mavericks'] = 'DAL'
    nameToAbv['Nuggets'] = 'DEN'
    nameToAbv['Pistons'] = 'DET'
    nameToAbv['Warriors'] = 'GS'
    nameToAbv['Rockets'] = 'HOU'
    nameToAbv['Pacers'] = 'IND'
    nameToAbv['Clippers'] = 'LAC'
    nameToAbv['Lakers'] = 'LAL'
    nameToAbv['Grizzlies'] = 'MEM'
    nameToAbv['Heat'] = 'MIA'
    nameToAbv['Bucks'] = 'MIL'
    nameToAbv['Timberwolves'] = 'MIN'
    nameToAbv['Pelicans'] = 'NO'
    nameToAbv['Knicks'] = 'NY'
    nameToAbv['Thunder'] = 'OKC'
    nameToAbv['Magic'] = 'ORL'
    nameToAbv['76ers'] = 'PHI'
    nameToAbv['Suns'] = 'PHO'
    nameToAbv['Blazers'] = 'POR'
    nameToAbv['Kings'] = 'SAC'
    nameToAbv['Spurs'] = 'SA'
    nameToAbv['Raptors'] = 'TOR'
    nameToAbv['Jazz'] = 'UTA'
    nameToAbv['Wizards'] = 'WAS'

    periodGames = dates[(dates['Date'] >= pd.Timestamp(year=2018, month=10, day=16)) & (dates['Date'] <= pd.Timestamp(year=2018, month=10, day=22))]
    periodGames['Home Team'] = periodGames['Home Team'].apply(lambda x:nameToAbv[x.split()[-1:][0]])
    periodGames['Away Team'] = periodGames['Away Team'].apply(lambda x:nameToAbv[x.split()[-1:][0]])

    playersGrouped = players[players['Status']!='FA'].groupby(by='Status',as_index=False).mean()
    playersGrouped.drop(['Rk','GP','Score'], axis=1,inplace=True)
    labels = playersGrouped.columns[1:]

    playersGroupedNorm = playersGrouped.copy()
    for label in labels:
        if label.endswith('%'):
            continue
        playersGroupedNorm[label]-=playersGroupedNorm[label].min()
        playersGroupedNorm[label]/=playersGroupedNorm[label].max()
        if label == 'TO':
            playersGroupedNorm[label]=1-playersGroupedNorm[label]

    if fact is False:
        return playersGroupedNorm, labels

    periodGames.groupby('Home Team',as_index=False).count().drop('Away Team', axis=1)
    gamesPerTeam = periodGames.groupby('Home Team',as_index=False).count().drop('Away Team', axis=1)
    gamesPerTeam = gamesPerTeam.merge(periodGames.groupby('Away Team',as_index=False).count().drop('Home Team', axis=1),how='outer', left_on='Home Team', right_on='Away Team')
    gamesPerTeam['Team'] = gamesPerTeam['Home Team']
    gamesPerTeam['Team'].fillna(gamesPerTeam['Away Team'], inplace=True)
    gamesPerTeam['Date_x'].fillna(0, inplace=True)
    gamesPerTeam['Date_y'].fillna(0, inplace=True)
    gamesPerTeam.drop(['Home Team', 'Away Team'],inplace=True,axis=1)
    gamesPerTeam['Total'] = gamesPerTeam['Date_x']+gamesPerTeam['Date_y']
    gamesPerTeam.drop(['Date_x', 'Date_y'],inplace=True,axis=1)

    playersStatsFactorizedByGames = players[players['Status']!='FA'].copy()
    playersStatsFactorizedByGames = playersStatsFactorizedByGames.merge(gamesPerTeam, how='outer', on='Team')
    playersStatsFactorizedByGames.drop(['Rk','GP','ADP','%D','Score','Opponent'], axis=1,inplace=True)

    colsToCalc = ['FG%', '3PTM', 'FT%', 'PTS',
        'REB', 'AST', 'ST', 'BLK', 'TO']
    for col in colsToCalc:
        playersStatsFactorizedByGames[col]=playersStatsFactorizedByGames[col]*playersStatsFactorizedByGames['Total']
    playersStatsFactorizedByGamesGrouped = playersStatsFactorizedByGames.groupby('Status', as_index=False).sum()
    playersStatsFactorizedByGamesGrouped['FT%']/=playersStatsFactorizedByGamesGrouped['Total']
    playersStatsFactorizedByGamesGrouped['FG%']/=playersStatsFactorizedByGamesGrouped['Total']
    playersStatsFactorizedByGamesGrouped.drop('Total', axis=1, inplace=True)
    
    labels = playersStatsFactorizedByGamesGrouped.columns[1:]
    scale=True
    if scale:
        labelsToScale= [ '3PTM','PTS', 'REB',
        'AST', 'ST', 'BLK', 'TO']
        for label in labelsToScale:
            playersStatsFactorizedByGamesGrouped[label]-=playersStatsFactorizedByGamesGrouped[label].min()
            playersStatsFactorizedByGamesGrouped[label]/=playersStatsFactorizedByGamesGrouped[label].max()
            if label == 'TO':
                playersStatsFactorizedByGamesGrouped[label]=1-playersStatsFactorizedByGamesGrouped[label]
    
    return playersStatsFactorizedByGamesGrouped, labels