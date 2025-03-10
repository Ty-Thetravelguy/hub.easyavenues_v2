# Generated by Django 5.1.6 on 2025-02-20 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AgentSupportSupplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supplier_type', models.CharField(choices=[('air', 'Air'), ('accommodation', 'Accommodation'), ('ground_transportation', 'Ground Transportation'), ('rail', 'Rail'), ('other', 'Other')], max_length=25)),
                ('supplier_name', models.CharField(max_length=255)),
                ('agent_websites', models.TextField(blank=True, null=True)),
                ('contact_phone', models.TextField(blank=True, null=True)),
                ('general_email', models.TextField(blank=True, null=True)),
                ('group_phone', models.TextField(blank=True, null=True)),
                ('group_email', models.TextField(blank=True, null=True)),
                ('account_manager_name', models.TextField(blank=True, null=True)),
                ('account_manager_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('account_manager_phone', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
