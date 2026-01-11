# Migration to add chroma_id field to Product model

from django.db import migrations, models
import uuid


def generate_chroma_ids(apps, schema_editor):
    """Generate chroma_id for existing products."""
    Product = apps.get_model('accounts', 'Product')
    for product in Product.objects.all():
        product.chroma_id = f"product_{product.business_id}_{uuid.uuid4().hex[:8]}"
        product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='chroma_id',
            field=models.CharField(
                db_index=True,
                default='temp',
                help_text='Unique ID for ChromaDB document',
                max_length=255
            ),
            preserve_default=False,
        ),
        migrations.RunPython(generate_chroma_ids, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='product',
            name='chroma_id',
            field=models.CharField(
                db_index=True,
                help_text='Unique ID for ChromaDB document',
                max_length=255,
                unique=True
            ),
        ),
    ]
