# Generated migration for Business model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_authtoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_info', models.TextField(help_text='Business information: name, owner, address, industry (max 10 lines)', max_length=2000)),
                ('logo', models.BinaryField(blank=True, help_text='Business logo stored as binary data (max 200KB)', null=True)),
                ('logo_filename', models.CharField(blank=True, help_text='Original filename of the logo', max_length=255, null=True)),
                ('logo_content_type', models.CharField(blank=True, help_text='MIME type of the logo (e.g., image/jpeg, image/png)', max_length=100, null=True)),
                ('chroma_id', models.CharField(db_index=True, help_text='Unique ID for ChromaDB document', max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(help_text='User who owns this business', on_delete=django.db.models.deletion.CASCADE, related_name='business', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Business',
                'verbose_name_plural': 'Businesses',
                'db_table': 'businesses',
                'ordering': ['-created_at'],
            },
        ),
    ]
