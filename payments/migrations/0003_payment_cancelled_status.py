from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_orderitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'Pending'),
                    ('COMPLETE', 'Complete'),
                    ('FAILED', 'Failed'),
                    ('CANCELLED', 'Cancelled'),
                ],
                default='PENDING',
                max_length=20,
            ),
        ),
    ]
