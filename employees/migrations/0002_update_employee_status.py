# Generated migration for updating employee status choices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='status',
            field=models.CharField(
                choices=[
                    ('Pending', 'Pending Setup'),
                    ('Active', 'Active'),
                    ('Inactive', 'Inactive'),
                    ('On Leave', 'On Leave')
                ],
                default='Pending',
                max_length=20
            ),
        ),
    ]
