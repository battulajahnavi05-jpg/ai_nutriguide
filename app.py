from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from database import init_db, get_db
import hashlib, json, math, random
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'ainutriguide_secret_2024'
app.jinja_env.globals.update(enumerate=enumerate, zip=zip, abs=abs)

init_db()

# ─── HELPERS ────────────────────────────────────────────
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def calc_bmi(weight, height):
    h = height / 100
    return round(weight / (h * h), 1)

def bmi_category(bmi):
    if bmi < 18.5: return 'Underweight', '#3498db'
    if bmi < 25:   return 'Normal',      '#2ecc71'
    if bmi < 30:   return 'Overweight',  '#f39c12'
    return 'Obese', '#e74c3c'

def calc_calories(age, gender, weight, height, activity):
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    mul = {'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55, 'very': 1.725, 'extra': 1.9}
    return round(bmr * mul.get(activity, 1.2))

# ─── TELANGANA FOOD DATABASE ─────────────────────────────
TELANGANA_FOODS = {
    'breakfast': [
        {'name': 'Jonna Roti with Peanut Chutney',   'emoji': '🫓', 'cal': 280, 'protein': 9,  'carbs': 52, 'fat': 6,  'tags': ['veg','vegan','jain'], 'ingredients': ['Sorghum flour','Peanuts','Green chilli','Garlic','Curry leaves'],        'why': 'Jowar is rich in fibre and complex carbs keeping blood sugar stable. Peanuts add healthy fats and protein for sustained morning energy.'},
        {'name': 'Pesarattu with Ginger Chutney',    'emoji': '🥗', 'cal': 220, 'protein': 14, 'carbs': 38, 'fat': 4,  'tags': ['veg','vegan','jain'], 'ingredients': ['Whole moong dal','Green chilli','Ginger','Onion','Cumin'],               'why': 'Moong dal is rich in plant protein and easily digestible. Ginger reduces inflammation — a classic Telangana superfood breakfast.'},
        {'name': 'Idli with Sambar & Chutney',       'emoji': '🫙', 'cal': 260, 'protein': 8,  'carbs': 50, 'fat': 4,  'tags': ['veg','jain'],         'ingredients': ['Idli rice','Urad dal','Toor dal','Coconut','Tamarind'],             'why': 'Fermented idlis have probiotics for gut health. Sambar provides iron from toor dal and vitamins from vegetables.'},
        {'name': 'Sajja Roti with Groundnut Chutney','emoji': '🫓', 'cal': 240, 'protein': 7,  'carbs': 46, 'fat': 6,  'tags': ['veg','vegan'],        'ingredients': ['Pearl millet flour','Groundnuts','Red chilli','Garlic','Salt'],    'why': 'Pearl millet is rich in iron and zinc, great for anaemia prevention. Low glycaemic index makes it ideal for diabetics.'},
        {'name': 'Upma with Vegetables',             'emoji': '🥣', 'cal': 200, 'protein': 6,  'carbs': 38, 'fat': 5,  'tags': ['veg','jain'],         'ingredients': ['Semolina','Onion','Mustard seeds','Curry leaves','Mixed vegetables'], 'why': 'Semolina provides quick energy while vegetables add micronutrients. Tempering with mustard seeds aids digestion.'},
        {'name': 'Ragi Mudde with Dal',              'emoji': '🟤', 'cal': 300, 'protein': 11, 'carbs': 58, 'fat': 3,  'tags': ['veg','vegan'],        'ingredients': ['Finger millet','Toor dal','Onion','Tomato','Turmeric'],            'why': 'Ragi is the richest plant source of calcium — excellent for bone health. High fibre helps control obesity and diabetes.'},
        {'name': 'Punugulu with Tomato Chutney',     'emoji': '🔵', 'cal': 250, 'protein': 7,  'carbs': 44, 'fat': 7,  'tags': ['veg','jain'],         'ingredients': ['Idli batter','Onion','Green chilli','Cumin','Coriander'],          'why': 'Fermented batter provides probiotics. A traditional Telangana snack-breakfast rich in carbohydrates for morning energy.'},
    ],
    'lunch': [
        {'name': 'Jonna Sangati with Sambar',        'emoji': '🍱', 'cal': 380, 'protein': 12, 'carbs': 72, 'fat': 6,  'tags': ['veg','vegan'],        'ingredients': ['Jowar flour','Toor dal','Tamarind','Drumstick','Tomato'],          'why': 'Traditional Telangana staple. Jowar provides resistant starch feeding gut bacteria while drumstick sambar adds iron and vitamins.'},
        {'name': 'Curd Rice with Mango Pickle',      'emoji': '🍚', 'cal': 320, 'protein': 10, 'carbs': 58, 'fat': 7,  'tags': ['veg','jain'],         'ingredients': ['Cooked rice','Yoghurt','Mustard seeds','Curry leaves','Green chilli'], 'why': 'Probiotic-rich, cooling meal perfect for Telangana heat. Excellent for digestive health and maintaining gut flora.'},
        {'name': 'Mamidikaya Pulihora',              'emoji': '🍋', 'cal': 290, 'protein': 5,  'carbs': 60, 'fat': 6,  'tags': ['veg','vegan'],        'ingredients': ['Rice','Raw mango','Peanuts','Turmeric','Mustard seeds'],           'why': 'Raw mango provides Vitamin C and aids digestion. Turmeric has anti-inflammatory curcumin. Peanuts add healthy fats.'},
        {'name': 'Gongura Mutton Curry with Rice',   'emoji': '🍖', 'cal': 480, 'protein': 38, 'carbs': 45, 'fat': 18, 'tags': ['nonveg'],             'ingredients': ['Mutton','Gongura leaves','Onion','Red chilli','Ginger-garlic'],   'why': "Gongura (sorrel) is Telangana's signature ingredient, loaded with iron and Vitamin C. Mutton provides complete protein for muscle repair."},
        {'name': 'Bagara Baingan with Roti',         'emoji': '🍆', 'cal': 340, 'protein': 8,  'carbs': 42, 'fat': 14, 'tags': ['veg','vegan'],        'ingredients': ['Brinjal','Peanuts','Sesame seeds','Tamarind','Coconut'],          'why': 'Brinjal is low-calorie and rich in anthocyanins. Peanut-sesame gravy provides healthy fats and plant protein.'},
        {'name': 'Chicken Curry with Jonna Roti',   'emoji': '🍗', 'cal': 440, 'protein': 42, 'carbs': 38, 'fat': 14, 'tags': ['nonveg'],             'ingredients': ['Country chicken','Jowar roti','Onion','Tomato','Telangana spices'], 'why': 'Free-range country chicken has less fat and more omega-3. Jowar roti adds fibre for sustained satiety.'},
        {'name': 'Dal with Jowar Roti & Greens',    'emoji': '🥬', 'cal': 310, 'protein': 14, 'carbs': 54, 'fat': 5,  'tags': ['veg','vegan'],        'ingredients': ['Toor dal','Jowar roti','Fenugreek leaves','Garlic','Tamarind'],   'why': 'Toor dal is high in folate, protein and fibre. Fenugreek leaves reduce post-meal blood sugar spikes.'},
        {'name': 'Fish Curry with Rice',             'emoji': '🐟', 'cal': 360, 'protein': 32, 'carbs': 42, 'fat': 10, 'tags': ['nonveg'],             'ingredients': ['Rohu fish','Tamarind','Onion','Green chilli','Curry leaves'],     'why': 'Telangana river fish is rich in omega-3 fatty acids supporting heart health. Tamarind aids absorption of minerals.'},
    ],
    'dinner': [
        {'name': 'Gongura Pappu with Rice',          'emoji': '🌿', 'cal': 280, 'protein': 12, 'carbs': 52, 'fat': 4,  'tags': ['veg','vegan'],        'ingredients': ['Toor dal','Gongura leaves','Onion','Green chilli','Mustard seeds'], 'why': 'Light and nutritious evening meal. Gongura adds iron and Vitamin C to protein-rich dal. Easy on digestion before sleep.'},
        {'name': 'Ragi Sankati with Spinach Curry', 'emoji': '🟤', 'cal': 260, 'protein': 10, 'carbs': 48, 'fat': 4,  'tags': ['veg','vegan'],        'ingredients': ['Ragi flour','Spinach','Garlic','Cumin','Dry red chilli'],         'why': 'Ragi calcium strengthens bones. Spinach adds iron and folate. This combination covers most micronutrient needs.'},
        {'name': 'Pesara Pappu with Sajja Roti',    'emoji': '🫘', 'cal': 290, 'protein': 15, 'carbs': 50, 'fat': 5,  'tags': ['veg','vegan'],        'ingredients': ['Split moong dal','Pearl millet roti','Tomato','Turmeric','Ginger'], 'why': 'Moong dal is the lightest legume for dinner, easily digested during sleep. Pearl millet keeps blood sugar stable overnight.'},
        {'name': 'Vegetable Kurma with Chapati',    'emoji': '🥙', 'cal': 320, 'protein': 9,  'carbs': 55, 'fat': 8,  'tags': ['veg','jain'],         'ingredients': ['Mixed vegetables','Coconut','Peanuts','Whole wheat flour','Spices'], 'why': 'Mixed vegetables provide diverse vitamins. Coconut adds MCTs for overnight energy. Whole wheat adds fibre.'},
        {'name': 'Tomato Pappu with Jonna Roti',   'emoji': '🍅', 'cal': 240, 'protein': 10, 'carbs': 44, 'fat': 4,  'tags': ['veg','vegan'],        'ingredients': ['Toor dal','Tomato','Jowar roti','Mustard seeds','Turmeric'],      'why': 'Tomatoes provide lycopene, a potent antioxidant. Low-calorie dinner ideal for weight management. Jowar aids overnight digestion.'},
        {'name': 'Kandi Pappu with Vankaya Fry',   'emoji': '🍆', 'cal': 300, 'protein': 13, 'carbs': 48, 'fat': 7,  'tags': ['veg','vegan'],        'ingredients': ['Red gram dal','Brinjal','Coriander','Cumin','Mustard seeds'],     'why': 'Red gram (kandi) is packed with protein, fibre, and folate essential for cell repair during sleep.'},
        {'name': 'Mutton Curry with Ragi Sankati', 'emoji': '🍖', 'cal': 420, 'protein': 36, 'carbs': 38, 'fat': 16, 'tags': ['nonveg'],             'ingredients': ['Mutton','Ragi flour','Onion','Ginger','Telangana masala'],        'why': 'Protein-rich mutton repairs muscles overnight. Ragi provides calcium and iron for complete nutrition.'},
    ]
}

ACTIVITY_BURNS = {'walking': 4, 'running': 10, 'cycling': 7, 'gym': 8, 'yoga': 3, 'swimming': 9, 'work': 3, 'dance': 6, 'other': 4}

def get_filtered_meals(diet_type):
    tag = diet_type.lower()
    breakfasts = [m for m in TELANGANA_FOODS['breakfast'] if tag in m['tags']]
    lunches    = [m for m in TELANGANA_FOODS['lunch']     if tag in m['tags']]
    dinners    = [m for m in TELANGANA_FOODS['dinner']    if tag in m['tags']]
    if not breakfasts: breakfasts = TELANGANA_FOODS['breakfast']
    if not lunches:    lunches    = TELANGANA_FOODS['lunch']
    if not dinners:    dinners    = TELANGANA_FOODS['dinner']
    return breakfasts, lunches, dinners

def generate_diet_plan(profile):
    breakfasts, lunches, dinners = get_filtered_meals(profile['diet_type'])
    plan = []
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    for i in range(7):
        plan.append({
            'day': days[i],
            'breakfast': breakfasts[i % len(breakfasts)],
            'lunch':     lunches[i % len(lunches)],
            'dinner':    dinners[i % len(dinners)],
        })
    return plan

# ─── ROUTES ─────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('welcome'))

@app.route('/welcome')
def welcome():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('welcome.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name     = request.form.get('name','').strip()
        email    = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        confirm  = request.form.get('confirm_password','')
        if not name or not email or not password:
            return render_template('signup.html', error='All fields are required.')
        if password != confirm:
            return render_template('signup.html', error='Passwords do not match.', name=name, email=email)
        if len(password) < 6:
            return render_template('signup.html', error='Password must be at least 6 characters.', name=name, email=email)
        db = get_db()
        existing = db.execute('SELECT id FROM users WHERE email=?', (email,)).fetchone()
        if existing:
            return render_template('signup.html', error='Email already registered. Please sign in.', name=name)
        db.execute('INSERT INTO users (name,email,password) VALUES (?,?,?)',
                   (name, email, hash_password(password)))
        db.commit()
        user = db.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return redirect(url_for('profile_setup'))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        if not email or not password:
            return render_template('login.html', error='Please enter email and password.')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email=? AND password=?',
                          (email, hash_password(password))).fetchone()
        if not user:
            return render_template('login.html', error='Invalid email or password.', email=email)
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        profile = db.execute('SELECT * FROM profiles WHERE user_id=?', (user['id'],)).fetchone()
        if not profile:
            return redirect(url_for('profile_setup'))
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('welcome'))

@app.route('/profile-setup', methods=['GET','POST'])
@login_required
def profile_setup():
    if request.method == 'POST':
        data = {
            'user_id':    session['user_id'],
            'age':        int(request.form.get('age', 25)),
            'gender':     request.form.get('gender','male'),
            'height':     float(request.form.get('height', 165)),
            'weight':     float(request.form.get('weight', 65)),
            'target_weight': float(request.form.get('target_weight', 65)),
            'diet_type':  request.form.get('diet_type','veg'),
            'activity':   request.form.get('activity','moderate'),
            'allergies':  request.form.get('allergies',''),
            'conditions': ','.join(request.form.getlist('conditions')),
        }
        bmi = calc_bmi(data['weight'], data['height'])
        data['bmi'] = bmi
        data['daily_calories'] = calc_calories(data['age'], data['gender'], data['weight'], data['height'], data['activity'])
        db = get_db()
        existing = db.execute('SELECT id FROM profiles WHERE user_id=?', (data['user_id'],)).fetchone()
        if existing:
            db.execute('''UPDATE profiles SET age=?,gender=?,height=?,weight=?,target_weight=?,
                          diet_type=?,activity=?,allergies=?,conditions=?,bmi=?,daily_calories=?
                          WHERE user_id=?''',
                       (data['age'],data['gender'],data['height'],data['weight'],data['target_weight'],
                        data['diet_type'],data['activity'],data['allergies'],data['conditions'],
                        data['bmi'],data['daily_calories'],data['user_id']))
        else:
            db.execute('''INSERT INTO profiles (user_id,age,gender,height,weight,target_weight,
                          diet_type,activity,allergies,conditions,bmi,daily_calories)
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                       (data['user_id'],data['age'],data['gender'],data['height'],data['weight'],
                        data['target_weight'],data['diet_type'],data['activity'],data['allergies'],
                        data['conditions'],data['bmi'],data['daily_calories']))
            # seed initial weight log
            db.execute('INSERT INTO weight_logs (user_id,weight,logged_date) VALUES (?,?,?)',
                       (data['user_id'], data['weight'], date.today().isoformat()))
        db.commit()
        return redirect(url_for('dashboard'))
    db = get_db()
    profile = db.execute('SELECT * FROM profiles WHERE user_id=?', (session['user_id'],)).fetchone()
    return render_template('profile_setup.html', profile=profile)

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    profile = db.execute('SELECT * FROM profiles WHERE user_id=?', (session['user_id'],)).fetchone()
    if not profile:
        return redirect(url_for('profile_setup'))
    bmi_cat, bmi_color = bmi_category(profile['bmi'])
    today_activities = db.execute(
        'SELECT * FROM activities WHERE user_id=? AND activity_date=?',
        (session['user_id'], date.today().isoformat())
    ).fetchall()
    total_burned = sum(a['calories_burned'] for a in today_activities)
    diet_plan = generate_diet_plan(dict(profile))
    today_meals = diet_plan[date.today().weekday() % 7]
    weight_logs = db.execute(
        'SELECT * FROM weight_logs WHERE user_id=? ORDER BY logged_date DESC LIMIT 7',
        (session['user_id'],)
    ).fetchall()
    now = datetime.now()
    return render_template('dashboard.html', now=now,
        profile=profile, bmi_cat=bmi_cat, bmi_color=bmi_color,
        today_meals=today_meals, total_burned=total_burned,
        weight_logs=weight_logs, user_name=session['user_name'])

@app.route('/diet-plan')
@login_required
def diet_plan():
    db = get_db()
    profile = db.execute('SELECT * FROM profiles WHERE user_id=?', (session['user_id'],)).fetchone()
    if not profile:
        return redirect(url_for('profile_setup'))
    plan = generate_diet_plan(dict(profile))
    bmi_cat, _ = bmi_category(profile['bmi'])
    return render_template('diet_plan.html', plan=plan, profile=profile,
                           bmi_cat=bmi_cat, user_name=session['user_name'])

@app.route('/activity', methods=['GET','POST'])
@login_required
def activity():
    db = get_db()
    if request.method == 'POST':
        act_type = request.form.get('activity_type','walking')
        duration = int(request.form.get('duration', 30))
        steps    = int(request.form.get('steps', 0))
        burned   = round(ACTIVITY_BURNS.get(act_type, 4) * duration)
        db.execute('''INSERT INTO activities (user_id,activity_type,duration_mins,steps,calories_burned,activity_date)
                      VALUES (?,?,?,?,?,?)''',
                   (session['user_id'], act_type, duration, steps, burned, date.today().isoformat()))
        db.commit()
        return redirect(url_for('activity'))
    profile = db.execute('SELECT * FROM profiles WHERE user_id=?', (session['user_id'],)).fetchone()
    today_acts = db.execute(
        'SELECT * FROM activities WHERE user_id=? AND activity_date=? ORDER BY id DESC',
        (session['user_id'], date.today().isoformat())
    ).fetchall()
    all_acts = db.execute(
        'SELECT * FROM activities WHERE user_id=? ORDER BY activity_date DESC, id DESC LIMIT 20',
        (session['user_id'],)
    ).fetchall()
    total_burned = sum(a['calories_burned'] for a in today_acts)
    total_mins   = sum(a['duration_mins']   for a in today_acts)
    total_steps  = sum(a['steps']           for a in today_acts)
    return render_template('activity.html', today_acts=today_acts, all_acts=all_acts,
                           total_burned=total_burned, total_mins=total_mins, total_steps=total_steps,
                           profile=profile, user_name=session['user_name'])

@app.route('/progress', methods=['GET','POST'])
@login_required
def progress():
    db = get_db()
    if request.method == 'POST':
        weight = float(request.form.get('weight', 0))
        if weight > 0:
            db.execute('INSERT INTO weight_logs (user_id,weight,logged_date) VALUES (?,?,?)',
                       (session['user_id'], weight, date.today().isoformat()))
            db.execute('UPDATE profiles SET weight=?, bmi=? WHERE user_id=?',
                       (weight, calc_bmi(weight, db.execute('SELECT height FROM profiles WHERE user_id=?',(session['user_id'],)).fetchone()['height']), session['user_id']))
            db.commit()
        return redirect(url_for('progress'))
    profile = db.execute('SELECT * FROM profiles WHERE user_id=?', (session['user_id'],)).fetchone()
    logs = db.execute(
        'SELECT * FROM weight_logs WHERE user_id=? ORDER BY logged_date ASC',
        (session['user_id'],)
    ).fetchall()
    bmi_cat, bmi_color = bmi_category(profile['bmi'])
    chart_labels = [l['logged_date'] for l in logs]
    chart_weights = [l['weight'] for l in logs]
    chart_bmis = [round(calc_bmi(l['weight'], profile['height']), 1) for l in logs]
    return render_template('progress.html', profile=profile, logs=logs,
                           bmi_cat=bmi_cat, bmi_color=bmi_color,
                           chart_labels=json.dumps(chart_labels),
                           chart_weights=json.dumps(chart_weights),
                           chart_bmis=json.dumps(chart_bmis),
                           user_name=session['user_name'])

@app.route('/grocery')
@login_required
def grocery():
    db = get_db()
    profile = db.execute('SELECT * FROM profiles WHERE user_id=?', (session['user_id'],)).fetchone()
    if not profile:
        return redirect(url_for('profile_setup'))
    plan = generate_diet_plan(dict(profile))
    all_ingredients = {}
    for day in plan:
        for meal_type in ['breakfast','lunch','dinner']:
            for ing in day[meal_type]['ingredients']:
                all_ingredients[ing] = all_ingredients.get(ing, 0) + 1
    grains  = {k:v for k,v in all_ingredients.items() if any(x in k.lower() for x in ['flour','rice','ragi','jowar','bajra','millet','semolina','rava'])}
    lentils = {k:v for k,v in all_ingredients.items() if any(x in k.lower() for x in ['dal','lentil','moong','toor','gram','peanut','groundnut'])}
    veggies = {k:v for k,v in all_ingredients.items() if any(x in k.lower() for x in ['brinjal','spinach','tomato','onion','chilli','fenugreek','curry','drumstick','mango','coconut','tamarind','ginger','garlic','vegetable'])}
    proteins= {k:v for k,v in all_ingredients.items() if any(x in k.lower() for x in ['mutton','chicken','fish','egg','meat'])}
    others  = {k:v for k,v in all_ingredients.items() if k not in grains and k not in lentils and k not in veggies and k not in proteins}
    return render_template('grocery.html', grains=grains, lentils=lentils,
                           veggies=veggies, proteins=proteins, others=others,
                           profile=profile, user_name=session['user_name'])

@app.route('/profile')
@login_required
def profile():
    db = get_db()
    user    = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    profile = db.execute('SELECT * FROM profiles WHERE user_id=?', (session['user_id'],)).fetchone()
    if not profile:
        return redirect(url_for('profile_setup'))
    bmi_cat, bmi_color = bmi_category(profile['bmi'])
    return render_template('profile.html', user=user, profile=profile,
                           bmi_cat=bmi_cat, bmi_color=bmi_color,
                           user_name=session['user_name'])

# ─── API ENDPOINTS ────────────────────────────────────────
@app.route('/api/delete-activity/<int:act_id>', methods=['POST'])
@login_required
def delete_activity(act_id):
    db = get_db()
    db.execute('DELETE FROM activities WHERE id=? AND user_id=?', (act_id, session['user_id']))
    db.commit()
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
