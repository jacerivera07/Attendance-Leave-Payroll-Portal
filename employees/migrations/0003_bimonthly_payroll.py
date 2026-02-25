# Generated migration for bi-monthly payroll feature

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0002_update_employee_status'),
    ]

    operations = [
        # Create PayrollPeriod model
        migrations.CreateModel(
            name='PayrollPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_type', models.CharField(choices=[('first_half', '1st-15th'), ('second_half', '16th-End of Month')], max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('month', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('year', models.IntegerField(validators=[django.core.validators.MinValueValidator(2000)])),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Processing', 'Processing'), ('Closed', 'Closed')], default='Open', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-year', '-month', '-start_date'],
                'indexes': [
                    models.Index(fields=['month', 'year'], name='employees_p_month_idx'),
                    models.Index(fields=['status'], name='employees_p_status_idx'),
                    models.Index(fields=['start_date', 'end_date'], name='employees_p_dates_idx'),
                ],
            },
        ),
        
        # Create WorkSchedule model
        migrations.CreateModel(
            name='WorkSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_days', models.JSONField(default=list, help_text='List of dates (YYYY-MM-DD) when employee should work')),
                ('rest_days', models.JSONField(default=list, help_text='List of dates (YYYY-MM-DD) when employee is off')),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_schedules', to='employees.employee')),
                ('payroll_period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_schedules', to='employees.payrollperiod')),
            ],
            options={
                'ordering': ['-payroll_period__year', '-payroll_period__month'],
                'indexes': [
                    models.Index(fields=['employee', 'payroll_period'], name='employees_w_emp_per_idx'),
                ],
            },
        ),
        
        # Add unique constraints
        migrations.AddConstraint(
            model_name='payrollperiod',
            constraint=models.UniqueConstraint(fields=['period_type', 'month', 'year'], name='unique_payroll_period'),
        ),
        migrations.AddConstraint(
            model_name='workschedule',
            constraint=models.UniqueConstraint(fields=['employee', 'payroll_period'], name='unique_work_schedule'),
        ),
        
        # Add payroll_period field to Payroll model (nullable for now)
        migrations.AddField(
            model_name='payroll',
            name='payroll_period',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='payroll_records',
                to='employees.payrollperiod'
            ),
        ),
    ]
