# Bi-Monthly Payroll & Work Schedule Feature

## Overview
Implementation of bi-monthly payroll system with 15-day cutoff periods and admin-managed work schedules.

## New Models

### 1. PayrollPeriod
- Tracks cutoff periods (1st-15th and 16th-end of month)
- Stores period dates and status
- Links to payroll records

### 2. WorkSchedule
- Admin sets employee work schedules per cutoff period
- Defines work days and rest days for each employee
- Linked to PayrollPeriod

### 3. Updated Payroll Model
- Modified to support bi-monthly periods
- Salary divided by 2 for each cutoff
- Linked to PayrollPeriod

## Features

### For Admin:
1. **Set Work Schedules**
   - Define work days for each employee per cutoff period
   - Set rest days (days off)
   - Schedule must be set before or at start of cutoff period

2. **Bi-Monthly Payroll Processing**
   - Process payroll for 1st-15th cutoff
   - Process payroll for 16th-end of month cutoff
   - Salary automatically divided by 2

3. **Schedule Management Dashboard**
   - View all employee schedules
   - Edit schedules per cutoff period
   - Copy previous period schedules

### For Employees:
1. **View Work Schedule**
   - See assigned work days for current cutoff
   - View rest days
   - See next cutoff schedule

2. **Bi-Monthly Payslips**
   - Receive payslip for each cutoff period
   - View salary breakdown (half of monthly salary)

## Database Schema

```python
class PayrollPeriod(models.Model):
    PERIOD_CHOICES = [
        ('first_half', '1st-15th'),
        ('second_half', '16th-End of Month'),
    ]
    
    period_type = CharField  # first_half or second_half
    start_date = DateField
    end_date = DateField
    month = IntegerField
    year = IntegerField
    status = CharField  # Open, Closed, Processing
    
class WorkSchedule(models.Model):
    employee = ForeignKey(Employee)
    payroll_period = ForeignKey(PayrollPeriod)
    work_days = JSONField  # List of dates employee should work
    rest_days = JSONField  # List of dates employee is off
    notes = TextField
    
class Payroll (Updated):
    payroll_period = ForeignKey(PayrollPeriod)  # NEW
    # Salary will be monthly_salary / 2
```

## Implementation Steps

1. Create new models (PayrollPeriod, WorkSchedule)
2. Update Payroll model to link to PayrollPeriod
3. Create migrations
4. Create API endpoints for schedule management
5. Build admin UI for setting schedules
6. Update payroll processing logic
7. Update employee dashboard to show schedules

## UI Components

### Admin Dashboard - New Section: "Work Schedules"
- Calendar view showing all employees
- Set schedule button per employee
- Cutoff period selector
- Bulk schedule copy feature

### Employee Dashboard - Updated Section: "My Schedule"
- Calendar showing work days (green) and rest days (gray)
- Current cutoff period indicator
- Next cutoff schedule preview

## Payroll Calculation Logic

```
Monthly Salary: ₱10,000
First Half (1-15): ₱5,000
Second Half (16-31): ₱5,000

Deductions/Allowances calculated proportionally
Attendance tracked per cutoff period
```

## Next Steps
1. Approve this design
2. Implement models and migrations
3. Build API endpoints
4. Create UI components
5. Test with sample data
