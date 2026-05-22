# 🚀 STEP-BY-STEP INSTALLATION & RUN GUIDE

Welcome to the Smart School Project! This guide will walk you through setting up both the backend and frontend from scratch.

## 📍 PREREQUISITES
- **Python 3.10+** (Make sure Python is added to your system PATH)
- **Node.js 18+** (Required for the frontend)

---

## **STEP 1: INSTALL & START THE BACKEND**

### Location:
```
smart_school_backend
```

### Commands:
```powershell
# 1. Navigate to backend directory
cd smart_school_backend

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the backend server
python app.py
```

### Expected Output:
```
[*] Starting Smart School Backend...
[*] Project Root: ...
[*] Database: ...\database\smart_school.db
[*] Running on http://127.0.0.1:5000
```

**✅ Backend is running when you see:** `Running on http://127.0.0.1:5000`

---

## **STEP 2: INSTALL & START THE FRONTEND (In a NEW Terminal)**

### Location:
```
smart-school-frontend\smart-school-frontend
```

### Commands:
```powershell
# 1. Navigate to frontend folder
cd smart-school-frontend\smart-school-frontend

# 2. Install Node modules
npm install

# 3. Start the frontend
npm run dev
```

### Expected Output:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help
```

**✅ Frontend is running when you see:** `Local: http://localhost:5173/`

---

## **STEP 3: LOGIN TO SYSTEM**

Once both servers are running, open your web browser.

### Website:
```
http://localhost:5173/login
```

### Default Admin Credentials:
The backend automatically creates a default admin account on its first run.
```
Email:    admin@school.com
Password: admin123
```

### Click: **Login**

---

## **COMPLETE WORKFLOW SUMMARY**

| Step | Action | Location | Command |
|------|--------|----------|---------|
| 1 | Setup Backend | `smart_school_backend` | `python -m venv venv` <br> `.\venv\Scripts\activate` <br> `pip install -r requirements.txt` |
| 2 | Start Backend | `smart_school_backend` | `python app.py` |
| 3 | Setup Frontend | `smart-school-frontend\smart-school-frontend` | `npm install` |
| 4 | Start Frontend | `smart-school-frontend\smart-school-frontend` | `npm run dev` |
| 5 | Login | Browser: `http://localhost:5173/login` | admin@school.com / admin123 |

---

## 🐛 TROUBLESHOOTING

### **Backend won't start?**
Make sure your virtual environment is activated before running `python app.py`. You should see `(venv)` at the beginning of your terminal prompt.
If port 5000 is already in use:
```powershell
# Check what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace <PID> with the actual number)
taskkill /PID <PID> /F
```

### **Frontend won't compile?**
Make sure you ran `npm install` inside the correct `smart-school-frontend/smart-school-frontend` directory. If things seem broken, delete the `node_modules` folder and run `npm install` again.

### **Camera not working for Face Recognition?**
- Allow camera permissions in your browser.
- Ensure no other application (like Zoom or Teams) is actively using your webcam.
- Refresh the page (F5).
