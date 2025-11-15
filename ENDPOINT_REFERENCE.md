# Complete Endpoint Reference Guide

## Fixed Issues

### ❌ Fixed Broken Endpoints

1. **index.html - Line 45:** `{{ url_for('contact') }}`
   - **Status:** Fixed ✅
   - **Changed to:** `#contact` (placeholder link)

2. **index.html - Line 53:** `{{ url_for('about') }}`
   - **Status:** Fixed ✅
   - **Changed to:** `#about` (placeholder link)

3. **upload_payment.html - Line 127:** `{{ url_for('student.status') }}`
   - **Status:** Fixed ✅
   - **Changed to:** `{{ url_for('student.student_dashboard') }}`
   - **Reason:** The `student.status` endpoint doesn't exist; dashboard shows payment status

---

## All Available Endpoints

### Student Blueprint (`/student`)

| Route | Function | Method | Endpoint Name | URL |
|-------|----------|--------|---------------|-----|
| `/login` | student_login | GET, POST | `student.student_login` | `/student/login` |
| `/logout` | student_logout | GET | `student.student_logout` | `/student/logout` |
| `/dashboard` | student_dashboard | GET | `student.student_dashboard` | `/student/dashboard` |
| `/upload_payment` | upload_payment | GET, POST | `student.upload_payment` | `/student/upload_payment` |
| `/delete_payment/<id>` | delete_payment | POST | `student.delete_payment` | `/student/delete_payment/<id>` |
| `/registration_slip` | registration_slip | GET | `student.registration_slip` | `/student/registration_slip` |
| `/registration_slip/download` | download_registration_slip | GET | `student.download_registration_slip` | `/student/registration_slip/download` |
| `/download_timetable` | download_timetable | GET | `student.download_timetable` | `/student/download_timetable` |
| `/register` | student_register | GET, POST | `student.student_register` | `/student/register` |
| `/uploads/<filename>` | serve_upload | GET | *(dynamic)* | `/student/uploads/<filename>` |

---

### Lecturer Blueprint (`/lecturer`)

| Route | Function | Method | Endpoint Name | URL |
|-------|----------|--------|---------------|-----|
| `/login` | lecturer_login | GET, POST | `lecturer.lecturer_login` | `/lecturer/login` |
| `/register` | lecturer_register | GET, POST | `lecturer.lecturer_register` | `/lecturer/register` |
| `/dashboard` | dashboard | GET | `lecturer.dashboard` | `/lecturer/dashboard` |

---

### Admin Blueprint (`/admin`)

| Route | Function | Method | Endpoint Name | URL |
|-------|----------|--------|---------------|-----|
| `/login` | admin_login | GET, POST | `admin.admin_login` | `/admin/login` |
| `/logout` | admin_logout | GET | `admin.admin_logout` | `/admin/logout` |
| `/dashboard` | dashboard | GET | `admin.dashboard` | `/admin/dashboard` |
| `/payment/<id>/<action>` | manage_payment | GET | `admin.manage_payment` | `/admin/payment/<id>/<action>` |
| *(and more...)* | *(...)* | *(...)* | *(...)* | *(...)* |

---

### Chatbot Blueprint (`/chatbot`)

| Route | Function | Method | Endpoint Name | URL |
|-------|----------|--------|---------------|-----|
| `/send_message` | send_message | POST | `chatbot.send_message` | `/chatbot/send_message` |
| `/help` | help_page | GET | `chatbot.help_page` | `/chatbot/help` |

---

### General Blueprint (no prefix)

| Route | Function | Method | Endpoint Name | URL |
|-------|----------|--------|---------------|-----|
| `/forgot-password` | forgot_password | GET, POST | `general.forgot_password` | `/forgot-password` |
| `/reset-password/<token>` | reset_password | GET, POST | `general.reset_password` | `/reset-password/<token>` |

---

## Verified Working References in Templates

### index.html ✅
- `{{ url_for('admin.admin_login') }}` → `/admin/login`
- `{{ url_for('lecturer.lecturer_login') }}` → `/lecturer/login`
- `{{ url_for('student.student_login') }}` → `/student/login`
- `{{ url_for('student.student_register') }}` → `/student/register`

### base.html ✅
- `{{ url_for('student.student_login') }}`
- `{{ url_for('lecturer.lecturer_login') }}`
- `{{ url_for('admin.admin_login') }}`
- `{{ url_for('static', filename='...') }}`

### student/login.html ✅
- `{{ url_for('admin.admin_login') }}`
- `{{ url_for('student.student_register') }}`
- `{{ url_for('student.student_login') }}`
- `{{ url_for('student.student_dashboard') }}`
- `{{ url_for('general.forgot_password') }}`
- `{{ url_for('chatbot.help_page') }}`

### student/upload_payment.html ✅
- `{{ url_for('student.student_dashboard') }}` *(Fixed from `student.status`)*

### student/dashboard.html ✅
- `{{ url_for('student.student_logout') }}`
- `{{ url_for('student.download_timetable') }}`
- `{{ url_for('chatbot.help_page') }}`
- `{{ url_for('student.download_registration_slip') }}`

---

## Testing Checklist

After fixing these endpoints, test the following:

```
✓ / (Homepage) - Should load without errors
✓ /student/login - Should work
✓ /student/register - Should work
✓ /student/dashboard - Should work (after login)
✓ /student/upload_payment - Should work, "Check Status" button → dashboard
✓ /lecturer/login - Should work
✓ /lecturer/register - Should work
✓ /lecturer/dashboard - Should work
✓ /admin/login - Should work
✓ /admin/dashboard - Should work
✓ /forgot-password - Should work
✓ All navigation links in header - Should work
✓ All buttons in quick access menu - Should work
```

---

## Error Resolution Summary

| Error | File | Line | Old Value | New Value | Status |
|-------|------|------|-----------|-----------|--------|
| BuildError: Could not build url for endpoint 'contact' | index.html | 45 | `url_for('contact')` | `#contact` | ✅ Fixed |
| BuildError: Could not build url for endpoint 'about' | index.html | 53 | `url_for('about')` | `#about` | ✅ Fixed |
| BuildError: Could not build url for endpoint 'student.status' | upload_payment.html | 127 | `url_for('student.status')` | `url_for('student.student_dashboard')` | ✅ Fixed |

---

## Future Considerations

If you plan to add Contact and About pages, create these routes:

```python
# In general_routes.py
@general.route('/contact', methods=['GET', 'POST'])
def contact():
    # Contact form implementation
    return render_template('contact.html')

@general.route('/about')
def about():
    # About page
    return render_template('about.html')
```

Then update index.html:
```html
<a href="{{ url_for('general.contact') }}">Contact</a>
<a href="{{ url_for('general.about') }}">About</a>
```
