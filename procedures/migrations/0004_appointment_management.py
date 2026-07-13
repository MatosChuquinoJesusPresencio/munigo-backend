from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procedures', '0003_charfield_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(
                choices=[
                    ('PENDIENTE_CONFIRMACION', 'Pendiente de confirmación'),
                    ('PROGRAMADA', 'Programada'),
                    ('CONFIRMADA', 'Confirmada'),
                    ('PENDIENTE_REPROGRAMACION', 'Pendiente de reprogramación'),
                    ('COMPLETADA', 'Completada'),
                    ('CANCELADA', 'Cancelada'),
                ],
                db_index=True,
                default='PENDIENTE_CONFIRMACION',
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='appointment',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='cancel_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
