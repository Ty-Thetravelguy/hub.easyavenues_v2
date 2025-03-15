# Generated by Django 5.1.6 on 2025-03-15 10:37

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_alter_company_company_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='ops_team',
            new_name='client_ops_team',
        ),
        migrations.RemoveField(
            model_name='company',
            name='account_status',
        ),
        migrations.RemoveField(
            model_name='company',
            name='company_owner',
        ),
        migrations.AddField(
            model_name='company',
            name='client_account_manager',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_companies', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='company',
            name='client_status',
            field=models.CharField(choices=[('Trading', 'Trading'), ('No longer Trading', 'No longer Trading'), ('On hold', 'On hold'), ('Other', 'Other')], default='Trading', max_length=255),
        ),
        migrations.AddField(
            model_name='company',
            name='client_type',
            field=models.CharField(choices=[('White Glove Client', 'White Glove Client'), ('Online Client', 'Online Client'), ('Blended', 'Blended'), ('Supplier', 'Supplier')], default='White Glove Client', max_length=255),
        ),
        migrations.AddField(
            model_name='company',
            name='company_memberships',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='corporate_airline_fares',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='corporate_hotel_rates',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='fop_limit',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='company',
            name='invoice_references',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='invoicing_frequency',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='payment_terms',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='supplier_for_department',
            field=models.CharField(choices=[('Company Supplier', 'Company Supplier'), ('Operations Supplier', 'Operations Supplier'), ('Finance Supplier', 'Finance Supplier'), ('Sales Supplier', 'Sales Supplier'), ('Marketing Supplier', 'Marketing Supplier'), ('Other', 'Other')], default='Company Supplier', max_length=255),
        ),
        migrations.AddField(
            model_name='company',
            name='supplier_owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_suppliers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='company',
            name='supplier_status',
            field=models.CharField(choices=[('Preferred Supplier', 'Preferred Supplier'), ('Non-Preferred Supplier', 'Non-Preferred Supplier'), ('Other', 'Other')], default='Preferred Supplier', max_length=255),
        ),
        migrations.AddField(
            model_name='company',
            name='supplier_type',
            field=models.CharField(choices=[('Air', 'Air'), ('Accommodation', 'Accommodation'), ('Car Hire', 'Car Hire'), ('Transfer', 'Transfer'), ('Rail', 'Rail'), ('Other', 'Other')], default='Air', max_length=255),
        ),
        migrations.AddField(
            model_name='contact',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contact',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contacts_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contact',
            name='do_not_contact',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contact',
            name='is_primary_finance_contact',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contact',
            name='is_primary_hr_contact',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contact',
            name='is_primary_it_contact',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contact',
            name='out_of_office_until',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='preferred_contact_method',
            field=models.CharField(choices=[('email', 'Email'), ('phone', 'Phone'), ('mobile', 'Mobile'), ('teams', 'Microsoft Teams'), ('whatsapp', 'WhatsApp')], default='email', max_length=20),
        ),
        migrations.AddField(
            model_name='contact',
            name='preferred_contact_time',
            field=models.CharField(blank=True, help_text="e.g., 'Mornings only', '9-5 GMT'", max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='teams_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contacts_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contact',
            name='whatsapp_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_type',
            field=models.CharField(choices=[('Client', 'Client'), ('Supplier', 'Supplier')], default='Client', max_length=255),
        ),
        migrations.AlterField(
            model_name='company',
            name='midoco_crm_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('meeting', 'Meeting'), ('call', 'Phone Call'), ('email', 'Email'), ('note', 'Note'), ('document', 'Document Upload'), ('status_change', 'Status Change'), ('policy_update', 'Policy Update')], max_length=20)),
                ('description', models.TextField()),
                ('performed_at', models.DateTimeField(auto_now_add=True)),
                ('scheduled_for', models.DateTimeField(blank=True, null=True)),
                ('outcome', models.TextField(blank=True)),
                ('follow_up_date', models.DateField(blank=True, null=True)),
                ('follow_up_notes', models.TextField(blank=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='crm.company')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activities', to='crm.contact')),
                ('performed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Activities',
                'ordering': ['-performed_at'],
            },
        ),
        migrations.CreateModel(
            name='ClientTravelPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('policy_name', models.CharField(default='Default Policy', max_length=255)),
                ('effective_date', models.DateField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('travel_policy', models.TextField(blank=True)),
                ('flight_notes', models.TextField(blank=True)),
                ('accommodation_notes', models.TextField(blank=True)),
                ('car_hire_notes', models.TextField(blank=True)),
                ('transfer_notes', models.TextField(blank=True)),
                ('rail_notes', models.TextField(blank=True)),
                ('other_notes', models.TextField(blank=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='travel_policies', to='crm.company')),
            ],
            options={
                'verbose_name_plural': 'Client travel policies',
                'ordering': ['-effective_date'],
            },
        ),
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('field_type', models.CharField(choices=[('text', 'Text'), ('number', 'Number'), ('date', 'Date'), ('boolean', 'Yes/No'), ('choice', 'Choice')], max_length=20)),
                ('required', models.BooleanField(default=False)),
                ('choices', models.JSONField(blank=True, null=True)),
                ('default_value', models.JSONField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomFieldValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.JSONField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_field_values', to='crm.company')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_field_values', to='crm.contact')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.customfield')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('field', 'company'), ('field', 'contact')},
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('document_type', models.CharField(choices=[('contract', 'Contract'), ('agreement', 'Agreement'), ('policy', 'Policy'), ('presentation', 'Presentation'), ('proposal', 'Proposal'), ('other', 'Other')], max_length=50)),
                ('file', models.FileField(upload_to='company_documents/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True)),
                ('version', models.CharField(blank=True, max_length=50)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='crm.company')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StatusHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_status', models.CharField(max_length=255)),
                ('new_status', models.CharField(max_length=255)),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.TextField(blank=True)),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_history', to='crm.company')),
            ],
            options={
                'verbose_name_plural': 'Status histories',
                'ordering': ['-changed_at'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ContactTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='crm.contact')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.tag')),
            ],
            options={
                'unique_together': {('contact', 'tag')},
            },
        ),
        migrations.CreateModel(
            name='CompanyTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='crm.company')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.tag')),
            ],
            options={
                'unique_together': {('company', 'tag')},
            },
        ),
        migrations.DeleteModel(
            name='CompanyNotes',
        ),
    ]
