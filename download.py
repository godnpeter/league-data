from riotwatcher import LolWatcher, ApiError
import json
import os
import pandas as pd
import time
import sys

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

apiKey = 'RGAPI-024ffbf6-33cc-4658-ba52-54c776a500e5'
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
            
            with open(path+'/games/{}.json'.format(gameId), 'w') as games_fp:
                json.dump(game_dict, games_fp)
        except ApiError as err:
            print("Riotwatcher Failed")
            if(err.response.status_code == 403 or err.response.status_code == 429):
                sys.exit("403 or 429")
            else:
                with open(path+'/Tracker_files/Failed_gameIds.txt', 'a') as failed_fp:
                    failed_fp.write('{}\n'.format(gameId))

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
            with open(path+'/Tracker_files/AccountIds.txt', 'r+') as accountId_fp:
                arr = accountId_fp.readlines()
                arr = [item.strip('\n') for item in arr]
                
                for accountId in accountIds:
                    if accountId not in arr:
                        accountId_fp.write('{}\n'.format(accountId))
                        
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
