# 🌿 AI NutriGuide – Smart Healthy Diet Planner

A complete **Python Flask** web application for personalised Telangana diet planning with AI-powered meal recommendations, BMI tracking, activity monitoring, and progress charts.

---

## 📁 Project Structure

```
ai_nutriguide/
├── app.py                  # Main Flask application
├── database.py             # SQLite database setup
├── nutriguide.db           # SQLite database (auto-created)
├── requirements.txt        # Python dependencies
│
├── static/
│   ├── css/
│   │   └── style.css       # Main stylesheet
│   └── js/
│       └── main.js         # Frontend JavaScript
│
└── templates/
    ├── base.html           # Base layout (sidebar + topbar)
    ├── welcome.html        # Landing page
    ├── signup.html         # User registration
    ├── login.html          # User login
    ├── profile_setup.html  # Health profile form
    ├── dashboard.html      # Main dashboard
    ├── diet_plan.html      # 7-day diet plan
    ├── activity.html       # Activity tracker
    ├── progress.html       # Progress charts
    ├── grocery.html        # Grocery list
    └── profile.html        # User profile
```

---

## 🚀 How to Run Locally

### Step 1 – Prerequisites
Make sure you have **Python 3.8+** installed.
```bash
python --version
```

### Step 2 – Create Virtual Environment (Recommended)
```bash
cd ai_nutriguide
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on Mac/Linux:
source venv/bin/activate
```

### Step 3 – Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 – Run the Application
```bash
python app.py
```

### Step 5 – Open in Browser
```
http://localhost:5000
```

---

## ✅ Features by Phase

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | Project Setup & Navigation | ✅ Done |
| 2 | User Registration & Login | ✅ Done |
| 3 | Health Profile Form | ✅ Done |
| 4 | BMI & Calorie Calculator | ✅ Done |
| 5 | AI Diet Plan Generator | ✅ Done |
| 6 | Meal Visualization with Emojis | ✅ Done |
| 7 | Activity Tracker | ✅ Done |
| 8 | Progress Charts (Chart.js) | ✅ Done |
| 9 | Grocery List Generator | ✅ Done |
| 10 | Responsive UI & Testing | ✅ Done |

---

## 🍽️ Telangana Foods Included

**Breakfasts:** Jonna Roti, Pesarattu, Idli with Sambar, Sajja Roti, Upma, Ragi Mudde, Punugulu

**Lunches:** Jonna Sangati, Curd Rice, Mamidikaya Pulihora, Gongura Mutton Curry, Bagara Baingan, Chicken Curry, Gongura Dal, Fish Curry

**Dinners:** Gongura Pappu, Ragi Sankati, Pesara Pappu, Vegetable Kurma, Tomato Pappu, Kandi Pappu, Mutton Curry

---

## 🛠️ Technologies Used

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Database | SQLite (via sqlite3) |
| Frontend | HTML5, CSS3, JavaScript |
| Charts | Chart.js |
| Fonts | Google Fonts (Sora) |
| Auth | Session-based with SHA-256 password hashing |

---

## 📱 Pages / Routes

| Route | Page |
|-------|------|
| `/` | Redirects to dashboard or welcome |
| `/welcome` | Landing page |
| `/signup` | User registration |
| `/login` | User login |
| `/logout` | Logout |
| `/profile-setup` | Health data form |
| `/dashboard` | Main dashboard |
| `/diet-plan` | 7-day meal plan |
| `/activity` | Activity tracker |
| `/progress` | Weight & BMI charts |
| `/grocery` | Grocery list |
| `/profile` | User profile |

---

## 🧮 Calculations Used

**BMI Formula:**
```
BMI = weight(kg) / (height(m))²
```

**Daily Calorie Requirement (Mifflin-St Jeor):**
```
Male:   BMR = 10×weight + 6.25×height - 5×age + 5
Female: BMR = 10×weight + 6.25×height - 5×age - 161
TDEE   = BMR × Activity Multiplier
```

**Activity Multipliers:**
- Sedentary: 1.2
- Lightly Active: 1.375
- Moderately Active: 1.55
- Very Active: 1.725
- Extra Active: 1.9

---

## 🔐 Security Notes

- Passwords are hashed with **SHA-256** before storage
- Sessions are managed with Flask's secure session cookies
- All routes require login (via `@login_required` decorator)
- SQL injection prevented via parameterised queries

---

## 📞 Support

For issues or feature requests, check the project code or contact the developer.
