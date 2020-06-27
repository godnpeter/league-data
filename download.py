from riotwatcher import LolWatcher, ApiError
import json
import os
import pandas as pd
import time

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

apiKey = 'RGAPI-9ac19158-e679-477b-8f70-426a8e1bf63e'
lol_watcher = LolWatcher(apiKey)
my_region = 'euw1'

path = __location__

######################################################################################################################################
def download_game(gameId):
    proceed = False
    with open(path+'/Tracker_files/GameIds.txt', 'r+') as fp:
        arr = fp.readlines()
        arr = [int(item.strip('\n')) for item in arr]
        if(gameId not in arr):
            proceed = True
            fp.write('{}\n'.format(gameId))
    
    if(proceed):
        try:
            game_dict = lol_watcher.match.by_id(my_region, gameId)
        except:
            with open(path+'/Tracker_files/Failed_gameIds.txt', 'a') as fp:
                fp.write('{}\n'.format(gameId))
            time.sleep(60)
            game_dict = lol_watcher.match.by_id(my_region, gameId)
            
        with open(path+'/games/{}.json'.format(gameId), 'w') as fp:
            json.dump(game_dict, fp)

######################################################################################################################################


for idx in range(9858):
    
    match_dict = {}
    accountIds = []
    
    with open(path+'/Root_games/match{}'.format(idx), 'r') as fp:
        match_dict = json.load(fp)
    
    gameCreation = match_dict['gameCreation']
    gameId = match_dict['gameId']
    accountIds = [match_dict['participantIdentities'][num]['player']['currentAccountId'] for num in range(10)]
    
    with open(path+'/Tracker_files/Completed_rootIds.txt', 'r+') as fp:
        arr = fp.readlines()
        arr = [int(item.strip('\n')) for item in arr]
        
        if(gameId not in arr):
            # Recording accountId list to a file
            with open(path+'/Tracker_files/AccountIds.txt', 'r+') as fp:
                arr = fp.readlines()
                arr = [item.strip('\n') for item in arr]
                
                for accountId in accountIds:
                    if accountId not in arr:
                        fp.write('{}\n'.format(accountId))
                        
            # Fetching gameId list for each accountId and saving the game
            week_in_milli = 604800000
            for accountId in accountIds:
                matchlist_dict = lol_watcher.match.matchlist_by_account(my_region, accountId,
                    begin_time=gameCreation-week_in_milli, end_time=gameCreation)
                matchlist_df = pd.json_normalize(matchlist_dict, record_path='matches')
                match_list = matchlist_df['gameId'].tolist()
                
                for matchId in match_list:
                    download_game(matchId)
                    
            fp.write('{}\n'.format(gameId))
