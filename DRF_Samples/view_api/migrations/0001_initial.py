# Generated by Django 4.2.7 on 2023-11-22 15:11

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Quantity', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1, message='Quantity must be at least one'), django.core.validators.MaxValueValidator(10, message='Quantity must not be more than 10')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('Owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='user id')),
                ('ProductName', models.CharField(max_length=200, unique=True)),
                ('Price', models.IntegerField(default=200, validators=[django.core.validators.MinValueValidator(200, message='price is too low'), django.core.validators.MaxValueValidator(10000, message='price is too high')])),
                ('Quality', models.CharField(choices=[('F', 'First_class'), ('S', 'Second_class'), ('T', 'Third_class'), ('N', 'No-class')], default='F', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('Purchases', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='view_api.purchase')),
                ('Seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Seller', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['updated_at', 'Price'],
            },
        ),
    ]