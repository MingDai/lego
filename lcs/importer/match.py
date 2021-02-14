import json
from datetime import datetime
from lcs.models import Champion, MatchObjectiveStats, MatchPlayerStats, Player, Team, Tournament, MatchTeamStats, Match


class MatchImporter:
  
  def __init__(self, patch, blue_team, red_team, tournament_code):
    self.patch = patch
    self.blue_team = Team.objects.get(symbol=blue_team)
    self.red_team = Team.objects.get(symbol=red_team)
    self.tournament = Tournament.objects.get(tournament_code=tournament_code)

  def create_player_stats(self, player_dict, position):
    return MatchPlayerStats.objects.create(
      player = Player.objects.get_or_create(summoner_name=player_dict['summonerName'])[0],
      position = position,
      champion = Champion.objects.get_or_create(name=player_dict['champion'])[0],
      kills = player_dict['stats']['kills'],
      deaths = player_dict['stats']['deaths'],
      assists = player_dict['stats']['assists'],
      gold = player_dict['stats']['gold'],
      minions = player_dict['stats']['minions'],
      first_blood = player_dict['stats']['firstBlood'],
    )

  def create_team_stats(self, team_dict):
    top = self.create_player_stats(team_dict['players']['top'], 'TOP')
    jg = self.create_player_stats(team_dict['players']['jg'], 'JG')
    mid = self.create_player_stats(team_dict['players']['mid'], 'MID')
    bot = self.create_player_stats(team_dict['players']['bottom'], 'BOT')
    sup = self.create_player_stats(team_dict['players']['support'], 'SUP')

    obj = MatchObjectiveStats.objects.create(
      dragons = team_dict['teamStats']['dragons'],
      barons = team_dict['teamStats']['barons'],
      turrets = team_dict['teamStats']['turrets'],
    )
    return MatchTeamStats.objects.create(
      team = self.blue_team,
      top = top,
      jungle = jg,
      mid = mid,
      bottom = bot,
      support = sup,
      objective = obj,
    )
  
  def save_from_dict(self, dict):
    bt = self.create_team_stats(dict['blueTeam'])
    rt = self.create_team_stats(dict['redTeam'])

    if dict['winner'] == "blue":
      winner = bt
      loser = rt
    else:
      winner = bt
      loser = rt

    minutes, seconds = [int(x) for x in dict['gameDuration'].split(':')]


    Match.objects.create(
      url=dict['url'],
      winning_team=winner,
      losing_team=loser,
      blue_team=bt,
      red_team=rt,
      tournament=self.tournament,
      patch=self.patch,
      date=datetime.strptime(dict['date'], "%Y-%m-%d").date(),
      game_duration=minutes*60 + seconds,
    )
