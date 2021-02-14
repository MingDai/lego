from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from lcs.models import Champion, MatchObjectiveStats, MatchPlayerStats, Player, Team, Tournament, MatchTeamStats, Match
from lcs.importer.match import MatchImporter
from lcs.match_history.week1.hundredT_vs_clg import MATCH_DATA
# https://matchhistory.na.leagueoflegends.com/en/#match-details/ESPORTSTMNT02/1686346?gameHash=f8b4d43ab4b4d02e&tab=overview

class Command(BaseCommand):
  @transaction.atomic
  def handle(self, *args, **options):
    print("Start Creating Team")

    Team.objects.get_or_create(name='100 Thieves', symbol='100T')
    Team.objects.get_or_create(name='Counter Logic Gaming', symbol='CLG')

    print("Start Creating Champs")

    Tournament.objects.get_or_create(
      tournament_name='LCS 2021 Spring',
      tournament_code='LCS_2021_SPR',
      region = 'NA',
    )
    print("Start Importer")

    m = MatchImporter(11.2, '100T', 'CLG', 'LCS_2021_SPR')
    m.save_from_dict(MATCH_DATA)



