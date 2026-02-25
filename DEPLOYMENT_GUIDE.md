# Deployment Guide for ALP Portal on Render

## Changes Made for Production

### 1. ✅ ALLOWED_HOSTS Updated
Added your Render domain to `hr_nexus/settings.py`:
```python
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1',
    'attendance-leave-payroll-portal.onrender.com',
    '.onrender.com',
]
```

### 2. ✅ CORS Settings Updated
Added production domain to CORS allowed origins:
```python
CORS_ALLOWED_ORIGINS = [
    # ... local hosts
    "https://attendance-leave-payroll-portal.onrender.com",
]
```

### 3. ✅ CSRF Trusted Origins Updated
Added production domain to trusted origins:
```python
CSRF_TRUSTED_ORIGINS = [
    # ... local hosts
    "https://attendance-leave-payroll-portal.onrender.com",
]
```

### 4. ✅ API URLs Auto-Detection
Updated all API URL configurations to automatically detect production vs local:
- `frontend/static/api.js`
- `templates/index.html`
- `templates/login.html`
- `templates/signup.html`

Now uses:
- Production: `https://attendance-leave-payroll-portal.onrender.com/api`
- Local: `http://127.0.0.1:8000/api`

## Next Steps for Render Deployment

### 1. Commit and Push Changes
```bash
git add .
git commit -m "Configure for Render deployment"
git push origin main
```

### 2. Render Will Auto-Deploy
Render should automatically detect the changes and redeploy.

### 3. Run Migrations on Render
After deployment, run migrations in Render shell:
```bash
python manage.py migrate
```

### 4. Create Superuser (if needed)
```bash
python manage.py createsuperuser
```

### 5. Collect Static Files
Make sure your `build.sh` or deployment script includes:
```bash
python manage.py collectstatic --no-input
```

## Production Checklist

### Security (TODO for Production):
- [ ] Change `SECRET_KEY` to environment variable
- [ ] Set `DEBUG = False` in production
- [ ] Use environment variables for sensitive data
- [ ] Set up proper database (PostgreSQL instead of SQLite)
- [ ] Configure proper static file serving
- [ ] Set up HTTPS (Render does this automatically)
- [ ] Review and restrict CORS settings
- [ ] Set up proper logging

### Database:
- [ ] SQLite works for testing but use PostgreSQL for production
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create admin user: `python manage.py createsuperuser`

### Static Files:
- [ ] Configure `STATIC_ROOT` in settings
- [ ] Run `collectstatic` command
- [ ] Serve static files properly (Whitenoise or CDN)

## Environment Variables for Render

Create these in Render dashboard:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=your-postgres-url
ALLOWED_HOSTS=attendance-leave-payroll-portal.onrender.com
```

## Build Command for Render
```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

## Start Command for Render
```bash
gunicorn hr_nexus.wsgi:application
```

## Common Issues & Solutions

### Issue: DisallowedHost Error
**Solution**: ✅ Already fixed - added domain to ALLOWED_HOSTS

### Issue: Static files not loading
**Solution**: 
1. Install whitenoise: `pip install whitenoise`
2. Add to `requirements.txt`
3. Configure in `settings.py`

### Issue: Database not persisting
**Solution**: Use PostgreSQL instead of SQLite on Render

### Issue: API calls failing
**Solution**: ✅ Already fixed - API URLs auto-detect production domain

## Testing After Deployment

1. Visit: https://attendance-leave-payroll-portal.onrender.com
2. Test login page
3. Test signup
4. Test admin dashboard
5. Test employee dashboard
6. Check all API endpoints work

## Current Status

✅ DisallowedHost error fixed
✅ API URLs configured for production
✅ CORS and CSRF settings updated
⏳ Ready to redeploy on Render

After you push these changes, Render will redeploy and the DisallowedHost error should be gone!
