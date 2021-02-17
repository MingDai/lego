from django.db import models
import math

# Create your models here.
class Team(models.Model):
  name = models.CharField(max_length=200, blank=True)
  symbol = models.CharField(max_length=10, primary_key=True)
  def __str__(self):
    return self.symbol

class Champion(models.Model):
  name = models.CharField(max_length=100, primary_key=True)
  def __str__(self):
    return self.name

class Player(models.Model):
  first_name = models.CharField(max_length=200, blank=True)
  last_name = models.CharField(max_length=200, blank=True)
  summoner_name = models.CharField(max_length=200, primary_key=True)
  def __str__(self):
    return self.summoner_name
  # list all scores in games (match history)

  # list all scores in games vs Team

class Tournament(models.Model):
  region = models.CharField(max_length=10)
  tournament_name = models.CharField(max_length=200)
  tournament_code = models.CharField(max_length=10, primary_key=True)
  def __str__(self):
    return self.tournament_name

class MatchObjectiveStats(models.Model):
  dragons = models.IntegerField(default=0)
  barons = models.IntegerField(default=0)
  turrets = models.IntegerField(default=0)
  def __str__(self):
    return 'Drags: {}, Barons: {}, Turrets: {}'.format(self.dragons, self.barons, self.turrets)

class MatchPlayerStats(models.Model):
  class Position(models.TextChoices):
    TOP = 'TOP'
    JUNGLE = 'JG'
    MID = 'MID'
    BOTTOM = 'BOT'
    SUPPORT = 'SUP'

  player = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='match_history')
  kills = models.IntegerField()
  deaths = models.IntegerField()
  assists = models.IntegerField()
  first_blood = models.BooleanField(default=False)
  champion = models.ForeignKey(Champion, on_delete=models.PROTECT)
  gold = models.IntegerField()
  minions = models.IntegerField()
  position = models.CharField(max_length=10, choices=Position.choices)

  # calculate kill participation for player
  # @property
  # def kill_participation(self):

  @property
  def fantasy_points(self):
    ten_kills_or_assists =  math.floor(self.kills/10) + math.floor(self.assists/10)
    return sum(
      self.kills * 3, 
      self.deaths * -1, 
      self.assists * 2, 
      self.minions * 0.02, 
      ten_kills_or_assists * 2
    )
  def __str__(self):
    return '<{}> {} {} {}/{}/{}'.format(
      self.id,
      self.player.summoner_name,
      self.champion.name,
      self.id,
      self.kills,
      self.deaths,
      self.assists
    )

class MatchTeamStats(models.Model):
  team = models.ForeignKey(Team, on_delete=models.PROTECT)
  top = models.OneToOneField(MatchPlayerStats, on_delete=models.PROTECT, related_name='top_for_team')
  jungle = models.OneToOneField(MatchPlayerStats, on_delete=models.PROTECT, related_name='jungle_for_team')
  mid = models.OneToOneField(MatchPlayerStats, on_delete=models.PROTECT, related_name='mid_for_team')
  bottom = models.OneToOneField(MatchPlayerStats, on_delete=models.PROTECT, related_name='bottom_for_team')
  support = models.OneToOneField(MatchPlayerStats, on_delete=models.PROTECT, related_name='support_for_team')
  objective = models.OneToOneField(MatchObjectiveStats, on_delete=models.PROTECT)
  def __str__(self):
    return '<{}> {}'.format(self.id, self.team)

class Match(models.Model):
  url = models.CharField(max_length=200)
  winning_team = models.OneToOneField(MatchTeamStats, on_delete=models.PROTECT, related_name='match_won')
  losing_team = models.OneToOneField(MatchTeamStats, on_delete=models.PROTECT, related_name='match_lost')
  blue_team = models.OneToOneField(MatchTeamStats, on_delete=models.PROTECT, related_name='blue_side_match')
  red_team = models.OneToOneField(MatchTeamStats, on_delete=models.PROTECT, related_name='red_side_match')
  tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
  patch = models.CharField(max_length=10)
  date = models.DateField()
  game_duration = models.IntegerField()  # time in seconds
  def __str__(self):
    return '<{}> date: {} W: {}, L: {}'.format(self.id, self.date, self.winning_team.team, self.losing_team.team)
  # Find all match historys of Huni when he is against Impact