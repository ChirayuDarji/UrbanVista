# 🚀 QUICK TESTING GUIDE

## ⚡ **FASTEST WAY TO TEST YOUR WEBSITE**

### 1. **Start the Server**
```bash
python manage.py runserver
```

### 2. **Open Browser**
Navigate to: `http://localhost:8000`

---

## 🎯 **CRITICAL PATHS TO TEST (Priority Order)**

### **Must Test First:**
1. ✅ **Home Page** - `/`
2. ✅ **Login** - `/login/`
3. ✅ **Signup** - `/signup/`
4. ✅ **Reports List** - `/reports/` (requires login)
5. ✅ **Create Report** - `/reports/create/` (requires login)
6. ✅ **Projects List** - `/projects/`
7. ✅ **News List** - `/news/`
8. ✅ **About Page** - `/about/`
9. ✅ **Help Center** - `/help/`

### **Features to Test:**
1. ✅ **Statistics** - `/reports/statistics/`
2. ✅ **Leaderboard** - `/reports/leaderboard/`
3. ✅ **Dashboard** - `/reports/dashboard/` (requires login)
4. ✅ **Contribute** - `/free-contribution/` (requires login)

---

## 🔍 **QUICK CHECKS**

### **Visual Checks:**
- [ ] All pages load without errors
- [ ] Images display correctly
- [ ] Navigation works
- [ ] Footer displays
- [ ] Mobile responsive

### **Functional Checks:**
- [ ] Can login
- [ ] Can create report
- [ ] Can view projects
- [ ] Can view news
- [ ] Forms submit successfully

### **Error Checks:**
- [ ] No console errors (F12)
- [ ] No 404 errors
- [ ] No 500 errors
- [ ] All links work

---

## 🐛 **COMMON ISSUES & FIXES**

### **Issue: Page not loading**
- Check: `python manage.py runserver` is running
- Check: No errors in terminal
- Check: Browser console for errors

### **Issue: Login not working**
- Check: Database has users
- Check: Email backend configured
- Check: OAuth credentials set (if using Google)

### **Issue: Images not showing**
- Check: `MEDIA_ROOT` and `MEDIA_URL` in settings
- Check: Files exist in `media/` folder
- Check: Static files collected: `python manage.py collectstatic`

### **Issue: Forms not submitting**
- Check: CSRF token present
- Check: JavaScript errors in console
- Check: Network tab for failed requests

---

## 📱 **MOBILE TESTING**

### **Quick Mobile Test:**
1. Open browser DevTools (F12)
2. Click device toggle icon
3. Test on:
   - iPhone 12/13/14
   - iPad
   - Samsung Galaxy
   - Desktop (1920x1080)

### **What to Check:**
- [ ] Navigation menu works
- [ ] Forms are usable
- [ ] Text is readable
- [ ] Buttons are tappable
- [ ] Images load
- [ ] No horizontal scroll

---

## ⚙️ **TEST DATA SETUP**

### **Create Test User:**
```bash
python manage.py createsuperuser
```

### **Create Sample Projects:**
```bash
python manage.py create_sample_projects --clear
```

### **Create Test Report:**
1. Login
2. Go to `/reports/create/`
3. Fill form and submit

---

## 🔧 **PRE-TEST CHECKLIST**

Before testing, ensure:
- [ ] Server is running
- [ ] Database migrations applied
- [ ] Static files collected (if production)
- [ ] Test user created
- [ ] Sample data created (optional)

---

## 📊 **TEST RESULTS**

After testing, note:
- ✅ **Working Features:** List what works
- ❌ **Broken Features:** List what's broken
- ⚠️ **Issues Found:** List any bugs
- 💡 **Improvements:** List suggestions

---

## 🎉 **READY TO TEST!**

Start your server and begin testing:
```bash
python manage.py runserver
```

Open: `http://localhost:8000`

**Happy Testing! 🚀**

