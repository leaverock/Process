# Generated by Django 2.2.5 on 2019-10-17 14:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('process', '0004_auto_20191016_1723'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventmodels',
            name='name_risk',
        ),
        migrations.AddField(
            model_name='eventmodels',
            name='expense',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='process.Expense', verbose_name='Риск'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='process',
            name='base',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='process.Process'),
        ),
    ]
