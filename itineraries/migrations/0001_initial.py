# Generated by Django 5.1.6 on 2025-02-14 07:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PNR',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('locator', models.CharField(max_length=10, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TravelSegment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('segment_type', models.CharField(choices=[('FLIGHT', 'Flight'), ('HOTEL', 'Hotel'), ('CAR', 'Car Rental')], max_length=50)),
                ('carrier', models.CharField(blank=True, max_length=50, null=True)),
                ('flight_number', models.CharField(blank=True, max_length=10, null=True)),
                ('departure_date', models.DateTimeField()),
                ('arrival_date', models.DateTimeField()),
                ('departure_airport', models.CharField(max_length=10)),
                ('arrival_airport', models.CharField(max_length=10)),
                ('booking_status', models.CharField(max_length=20)),
                ('PNR', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='segments', to='itineraries.pnr')),
            ],
        ),
        migrations.AddField(
            model_name='pnr',
            name='trip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pnrs', to='itineraries.trip'),
        ),
    ]
