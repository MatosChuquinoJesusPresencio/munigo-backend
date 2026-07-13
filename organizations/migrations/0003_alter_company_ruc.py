from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='ruc',
            field=models.CharField(max_length=13, unique=True),
        ),
    ]
