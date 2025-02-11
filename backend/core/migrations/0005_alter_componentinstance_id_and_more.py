# Generated by Django 4.2.18 on 2025-02-11 09:30

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_parameter_options_remove_parameter_unit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='componentinstance',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='Primary identifier for the instance', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='valid_ranges',
            field=models.JSONField(blank=True, default=dict, help_text='Defines acceptable value ranges and constraints'),
        ),
        migrations.CreateModel(
            name='ParameterValue',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for the parameter value', primary_key=True, serialize=False)),
                ('value', models.JSONField(help_text='The actual value of the parameter')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('instance', models.ForeignKey(help_text='Reference to component instance', on_delete=django.db.models.deletion.CASCADE, to='core.componentinstance')),
                ('parameter', models.ForeignKey(help_text='Reference to parameter definition', on_delete=django.db.models.deletion.CASCADE, to='core.parameter')),
            ],
            options={
                'db_table': 'et_parameter_value',
                'indexes': [models.Index(fields=['parameter'], name='et_paramete_paramet_b1b14f_idx'), models.Index(fields=['instance'], name='et_paramete_instanc_c29af0_idx')],
            },
        ),
        migrations.AddConstraint(
            model_name='parametervalue',
            constraint=models.UniqueConstraint(fields=('parameter', 'instance'), name='unique_parameter_value_per_instance'),
        ),
    ]
