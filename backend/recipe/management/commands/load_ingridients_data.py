from csv import DictReader

from django.core.management import BaseCommand
from recipe.models import Ingredient


class Command(BaseCommand):
    help = "Loads data from ingredients.csv"

    def handle(self, *args, **options):

        with open('./static/data/ingredients.csv', encoding='utf-8') as f:
            for row in DictReader(f):
                ingredient = Ingredient(
                    name=row['абрикосовое варенье'],
                    measurement_unit=row['г']
                )
                ingredient.save()

        self.stdout.write(
            self.style.SUCCESS(
                'Load_ingridients_data executed successfully.'
            )
        )
