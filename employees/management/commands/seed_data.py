from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta, time
import random
from employees.models import Employee, Attendance, Leave


class Command(BaseCommand):
    help = 'Seed database with sample HR data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Clear existing data
        Employee.objects.all().delete()
        
        # Create sample employees
        employees_data = [
            {
                'first_name': 'John', 'last_name': 'Smith',
                'email': 'john.smith@company.com',
                'department': 'Engineering', 'position': 'Senior Developer',
                'salary': 8000, 'join_date': '2022-01-15'
            },
            {
                'first_name': 'Sarah', 'last_name': 'Johnson',
                'email': 'sarah.j@company.com',
                'department': 'Design', 'position': 'UI/UX Designer',
                'salary': 6500, 'join_date': '2022-03-20'
            },
            {
                'first_name': 'Michael', 'last_name': 'Chen',
                'email': 'm.chen@company.com',
                'department': 'Engineering', 'position': 'DevOps Engineer',
                'salary': 7500, 'join_date': '2021-11-10'
            },
            {
                'first_name': 'Emily', 'last_name': 'Davis',
                'email': 'emily.d@company.com',
                'department': 'Marketing', 'position': 'Marketing Manager',
                'salary': 7000, 'join_date': '2022-06-01'
            },
            {
                'first_name': 'Robert', 'last_name': 'Wilson',
                'email': 'rob.w@company.com',
                'department': 'Sales', 'position': 'Sales Representative',
                'salary': 6000, 'join_date': '2023-01-10'
            },
        ]
        
        employees = []
        for emp_data in employees_data:
            employee = Employee.objects.create(**emp_data, status='Active')
            employees.append(employee)
            self.stdout.write(f'Created employee: {employee.full_name}')
        
        # Create attendance records for the past 7 days
        today = date.today()
        for i in range(7):
            attendance_date = today - timedelta(days=i)
            
            for employee in employees:
                # 80% attendance rate
                if random.random() > 0.2:
                    clock_in_hour = random.randint(8, 9)
                    clock_in_minute = random.randint(0, 59)
                    clock_out_hour = random.randint(17, 19)
                    clock_out_minute = random.randint(0, 59)
                    
                    status = 'Late' if clock_in_hour >= 9 else 'Present'
                    
                    Attendance.objects.create(
                        employee=employee,
                        date=attendance_date,
                        status=status,
                        clock_in=time(clock_in_hour, clock_in_minute),
                        clock_out=time(clock_out_hour, clock_out_minute),
                        notes=''
                    )
        
        self.stdout.write(f'Created attendance records for past 7 days')
        
        # Create sample leave requests
        leaves_data = [
            {
                'employee': employees[1],
                'leave_type': 'Vacation',
                'start_date': today + timedelta(days=15),
                'end_date': today + timedelta(days=20),
                'days': 6,
                'status': 'Approved',
                'reason': 'Family vacation'
            },
            {
                'employee': employees[2],
                'leave_type': 'Sick Leave',
                'start_date': today - timedelta(days=5),
                'end_date': today - timedelta(days=4),
                'days': 2,
                'status': 'Approved',
                'reason': 'Flu'
            },
            {
                'employee': employees[3],
                'leave_type': 'Personal',
                'start_date': today + timedelta(days=5),
                'end_date': today + timedelta(days=5),
                'days': 1,
                'status': 'Pending',
                'reason': 'Personal matter'
            },
        ]
        
        for leave_data in leaves_data:
            Leave.objects.create(**leave_data)
        
        self.stdout.write(f'Created {len(leaves_data)} leave requests')
        
        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))
        self.stdout.write(f'Total employees: {Employee.objects.count()}')
        self.stdout.write(f'Total attendance records: {Attendance.objects.count()}')
        self.stdout.write(f'Total leave requests: {Leave.objects.count()}')
