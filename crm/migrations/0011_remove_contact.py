from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0010_company_hubspot_id'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Contact',
        ),
    ] 