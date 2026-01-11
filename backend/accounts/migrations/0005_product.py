# Generated migration for Product and ProductImage models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_business'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_description', models.TextField(help_text='Product details: name, price, specifications (max 10 lines)', max_length=2000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(help_text='Business that owns this product', on_delete=django.db.models.deletion.CASCADE, related_name='products', to='accounts.business')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'db_table': 'products',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_data', models.BinaryField(help_text='Product image stored as binary data')),
                ('image_filename', models.CharField(help_text='Original filename of the image', max_length=255)),
                ('image_content_type', models.CharField(help_text='MIME type of the image (e.g., image/jpeg, image/png)', max_length=100)),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order of the image (0-3)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(help_text='Product this image belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='images', to='accounts.product')),
            ],
            options={
                'verbose_name': 'Product Image',
                'verbose_name_plural': 'Product Images',
                'db_table': 'product_images',
                'ordering': ['order', 'created_at'],
                'unique_together': {('product', 'order')},
            },
        ),
    ]
