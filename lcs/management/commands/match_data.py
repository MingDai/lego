from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from lcs.models import Champion, MatchObjectiveStats, MatchPlayerStats, Player, Team, Tournament, MatchTeamStats, Match
from lcs.importer.match import MatchImporter
from lcs.importer.scrape import MatchHistoryScraper

class Command(BaseCommand):

  def add_arguments(self, parser):
    parser.add_argument('patch', nargs='?')
    parser.add_argument('blue_team', nargs='?')
    parser.add_argument('red_team', nargs='?')
    parser.add_argument('url', nargs='?')

  @transaction.atomic
  def handle(self, *args, **options):
    print("Start Scraping")

    print(options['patch'], options['blue_team'], options['red_team'], 'LCS_2021_SPR')

    scr = MatchHistoryScraper(options['url'])

    scraped_match_data = scr.run()

    # Tournament.objects.get_or_create(
    #   tournament_name='LCS 2021 Spring',
    #   tournament_code='LCS_2021_SPR',
    #   region = 'NA',
    # )
    print("Start Importer")

    m = MatchImporter(options['patch'], options['blue_team'], options['red_team'], 'LCS_2021_SPR')
    m.save_from_dict(scraped_match_data)



