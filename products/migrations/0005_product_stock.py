from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_wishlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
