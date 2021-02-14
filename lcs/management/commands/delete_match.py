from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from lcs.models import Champion, MatchObjectiveStats, MatchPlayerStats, Player, Team, Tournament, MatchTeamStats, Match
from lcs.importer.match import MatchImporter
class Command(BaseCommand):
  def match_team_stat_deleter(self, match_team_stat):
    top = match_team_stat.top
    jg = match_team_stat.jungle
    mid = match_team_stat.mid
    bot = match_team_stat.bottom
    sup = match_team_stat.support
    obj = match_team_stat.objective
    match_team_stat.delete()

    top.delete()
    jg.delete()
    mid.delete()
    bot.delete()
    sup.delete()
    obj.delete()

  def match_deleter(self, match):
    blue = match.blue_team
    red = match.red_team
    match.delete()

    self.match_team_stat_deleter(blue)
    self.match_team_stat_deleter(red)

  def add_arguments(self, parser):
    parser.add_argument('match_id', nargs='?', type=int)

  @transaction.atomic
  def handle(self, *args, **options):
    match = Match.objects.get(id=options['match_id'])

    print("Deleting {}".format(match))
    self.match_deleter(match)
    print("Success")
