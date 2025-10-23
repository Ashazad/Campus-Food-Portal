import os
import json
from datetime import datetime

from flask import Flask, render_template, request, jsonify, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, login_user, logout_user, current_user
from sqlalchemy.orm import joinedload

from extensions import db, login_manager
from models import User, Chef, Food, CookingClass

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


def create_app():
    app = Flask(__name__, static_url_path='', static_folder='static')

    # Load settings from config.py if present (SECRET_KEY, DB URI, etc.)
    app.config.from_pyfile('config.py', silent=True)

    # Fallbacks if not provided by config/env
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///cuisine_connect.db')
    app.config.setdefault('SQLALCHEMY_ECHO', False)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login_view'

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_uuid):
        # Try User first, then Chef (both use id as primary key)
        user = User.query.filter_by(id=user_uuid).first()
        if user:
            return user
        chef = Chef.query.filter_by(id=user_uuid).first()
        if chef:
            return chef
        return None

    # ---------------------------
    # Basic pages / auth
    # ---------------------------
    @app.route('/')
    def index():
        return render_template('homepage.html')

    @app.route('/landing')
    def landing():
        return render_template('landing.html')

    @app.route('/logout')
    def logout():
        logout_user()
        return render_template('landing.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login_view():
        if request.method == 'POST':
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')

            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                # Redirect based on the role
                if user.role == 'chef':
                    return jsonify({
                        'success': True,
                        'message': 'Logged in successfully',
                        'redirect_url': url_for('chef_marketplace_home_page')
                    })
                else:
                    return jsonify({
                        'success': True,
                        'message': 'Logged in successfully',
                        'redirect_url': url_for('marketplace_home_page')
                    })

            return jsonify({'success': False, 'message': 'Login failed. Please check your credentials and try again.'})

        return render_template('login.html')

    @app.route('/create_account', methods=['GET', 'POST'])
    def create_account():
        if request.method == 'POST':
            data = request.get_json()
            email = data.get('email')
            first_name = data.get('first-name', '')
            last_name = data.get('last-name', '')
            dob_str = data.get('dob')
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
            password_hash = generate_password_hash(data.get('password'))
            account_type = data.get('account-type')

            # Check for existing accounts with role-specific uniqueness
            user_exists = User.query.filter(User.email == email, User.role == 'user').first() is not None
            chef_exists = User.query.filter(User.email == email, User.role == 'chef').first() is not None

            if user_exists and account_type == 'consumer':
                return jsonify({'success': False, 'message': 'Account already exists with this email.'}), 400
            if chef_exists and account_type == 'chef':
                return jsonify({'success': False, 'message': 'Account already exists with this email.'}), 400

            if account_type == 'consumer':
                user = User(email=email, first_name=first_name, last_name=last_name,
                            password=password_hash, dob=dob, role="user")
                db.session.add(user)
            else:
                business_name = data.get('business-name')
                order_location = data.get('map-options')
                location = data.get('location')

                user = User(email=email, first_name=first_name, last_name=last_name,
                            password=password_hash, dob=dob, role="chef")
                chef = Chef(email=email, first_name=first_name, last_name=last_name,
                            password=password_hash, dob=dob, business_name=business_name,
                            location=location, order_location=order_location)
                db.session.add(user)
                db.session.add(chef)

            db.session.commit()
            return jsonify({'success': True, 'message': 'Account created successfully'})

        return render_template('create_account.html')

    # ---------------------------
    # Marketplace (user & chef)
    # ---------------------------
    @app.route('/marketplace_home_page', methods=['GET', 'POST'])
    def marketplace_home_page():
        if not current_user.is_authenticated:
            return render_template('homepage.html', alert=True)

        if request.method == 'POST':
            data = request.json
            category = data.get('diet-category', 'none')

            if category == 'none':
                filtered_foods = Food.query.all()
            else:
                filtered_foods = (Food.query
                                  .options(joinedload(Food.chef))
                                  .filter_by(dietary_category=category)
                                  .all())

            foods_html = render_template_string('''
                {% if foods %}
                    {% for food in foods %}
                    <div class="food-item">
                        <img src="{{ url_for('static', filename=food.image_url) }}" alt="{{ food.foodName }}" class="food-image">
                        <div class="food-info">
                            <h3 class="food-name">{{ food.foodName }}</h3>
                            <p class="food-price">{{ food.price }} CAD</p>
                            <p class="food-category">{{ food.dietary_category }}</p>
                            <p class="food-chef">Created By Chef: {{ food.chef.first_name }} {{ food.chef.last_name }}</p>
                            <p class="food-start">Chef opening hours: {{ food.chef.start_time }} </p>
                            <p class="food-end">Chef closing hours: {{ food.chef.end_time }} </p>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p>No foods found.</p>
                {% endif %}
            ''', foods=filtered_foods)
            return jsonify({'foods_html': foods_html})

        all_foods = Food.query.all()
        return render_template('marketplace_home_page.html', foods=all_foods, is_authenticated=current_user.is_authenticated)

    @app.route('/chef/marketplace_home_page', methods=['GET', 'POST'])
    def chef_marketplace_home_page():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)

        chef = Chef.query.filter_by(email=current_user.email).first()
        if request.method == 'POST':
            data = request.json
            category = data.get('diet-category', 'none')

            if not chef:
                filtered_foods = []
            else:
                if category == 'none':
                    filtered_foods = Food.query.filter_by(chef_id=chef.id).all()
                else:
                    filtered_foods = (Food.query
                                      .options(joinedload(Food.chef))
                                      .filter(Food.dietary_category == category, Food.chef_id == chef.id)
                                      .all())

            foods_html = render_template_string('''
                {% if foods %}
                    {% for food in foods %}
                    <div class="food-item">
                        <img src="{{ url_for('static', filename=food.image_url) }}" alt="{{ food.foodName }}" class="food-image">
                        <div class="food-info">
                            <h3 class="food-name">{{ food.foodName }}</h3>
                            <p class="food-price">{{ food.price }} CAD</p>
                            <p class="food-category">{{ food.dietary_category }}</p>
                            <p class="food-chef">Created By {{ chef.first_name }} {{ chef.last_name }}</p>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p>No foods found.</p>
                {% endif %}
            ''', foods=filtered_foods, chef=chef)
            return jsonify({'foods_html': foods_html})

        if not chef:
            return render_template('chef_marketplace_home_page.html', foods=[], chef=None, start_time=None, end_time=None)

        start_time = chef.start_time
        end_time = chef.end_time
        all_foods = Food.query.filter_by(chef_id=chef.id).all()
        return render_template('chef_marketplace_home_page.html', foods=all_foods, chef=chef,
                               start_time=start_time, end_time=end_time)

    # ---------------------------
    # Chef CRUD: Food Items
    # ---------------------------
    @app.route('/chef/add_food_item', methods=['GET', 'POST'])
    def add_food_item():
        if not current_user.is_authenticated:
            return render_template('homepage.html', alert=True)

        chef = Chef.query.filter_by(email=current_user.email).first()
        if request.method == 'POST':
            food_name = request.form.get('foodName')
            dietary_category = request.form.get('dietary_category')
            price = request.form.get('price')
            image_file = request.files.get('image')

            image_url = ''
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                chef_folder = os.path.join('static', 'images', str(chef.id))
                os.makedirs(chef_folder, exist_ok=True)
                image_path = os.path.join(chef_folder, filename)
                image_file.save(image_path)
                # Store path relative to /static
                image_url = os.path.join('images', str(chef.id), filename)

            new_food = Food(
                foodName=food_name,
                dietary_category=dietary_category,
                price=price,
                image_url=image_url,
                chef_id=chef.id
            )
            db.session.add(new_food)
            db.session.commit()

            return jsonify({'success': True, 'message': 'Food item added successfully'})

        return render_template('add_food_item.html')

    @app.route('/chef/remove_food_item', methods=['GET', 'POST'])
    def remove_food_item():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)

        if request.method == 'POST':
            food_id = request.form.get('foodID')
            food = Food.query.get(food_id)
            if food:
                db.session.delete(food)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Food item removed successfully'})
            else:
                return jsonify({'success': False, 'message': food_id})
        chef = Chef.query.filter_by(email=current_user.email).first()
        foods = Food.query.filter_by(chef_id=chef.id).all() if chef else []
        return render_template('remove_food_item.html', foods=foods)

    # ---------------------------
    # Chef profile / hours
    # ---------------------------
    @app.route('/chef/edit_profile', methods=['GET', 'POST'])
    def edit_profile():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)

        chef = Chef.query.filter_by(email=current_user.email).first()
        if not chef:
            return jsonify({'success': False, 'message': 'Chef not found'}), 404

        if request.method == 'POST':
            chef.about_me = request.form.get('about_me')

            chef_folder = os.path.join('static', 'images', str(chef.id))
            os.makedirs(chef_folder, exist_ok=True)

            # Profile picture
            profile_picture = request.files.get('profile')
            if profile_picture and profile_picture.filename:
                filename = secure_filename(profile_picture.filename)
                filepath = os.path.join(chef_folder, filename)
                profile_picture.save(filepath)
                chef.profile_url = os.path.join('images', str(chef.id), filename)

            # Up to 3 showcase food images
            for i in range(1, 4):
                food_pic = request.files.get(f'food_choice{i}_image')
                if food_pic and food_pic.filename:
                    filename = secure_filename(food_pic.filename)
                    filepath = os.path.join(chef_folder, filename)
                    food_pic.save(filepath)
                    setattr(chef, f'food_choice{i}_image_url', os.path.join('images', str(chef.id), filename))

            db.session.commit()
            return jsonify({'success': True, 'message': 'Profile updated successfully', 'chef_id': str(chef.id)})

        return render_template('edit_profile.html', chef=chef)

    @app.route('/chef/view_profile/<chef_id>')
    def view_profile(chef_id):
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)

        chef = Chef.query.filter_by(id=chef_id).first()
        if not chef:
            return "Chef not found", 404

        return render_template('view_profile.html', chef=chef)

    @app.route('/chef/modify_open_hours', methods=['GET', 'POST'])
    def modify_open_hours():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)

        if request.method == 'POST':
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')
            chef = Chef.query.filter_by(email=current_user.email).first()
            if chef:
                chef.start_time = start_time
                chef.end_time = end_time
                db.session.commit()
        return render_template('modify_open_hours.html')

    # ---------------------------
    # Cooking classes (chef + user)
    # ---------------------------
    @app.route('/chef/cooking_classes', methods=['GET', 'POST'])
    def chef_cooking_classes_homepage():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)

        if request.method == 'POST':
            data = request.json
            html_category = data.get('class-category', 'none')

            if html_category == 'none':
                filtered_class = CookingClass.query.all()
            else:
                filtered_class = CookingClass.query.filter_by(category=html_category).all()

            # FIXED: pass 'classes=...' and use class.hostChef (field name)
            cooking_class_home = render_template_string('''
                {% if classes %}
                    {% for class in classes %}
                        <div class="class-card">
                            <img src="{{ url_for('static', filename=class.image_url) }}" alt="{{ class.className }}" class="food-image">
                            <div class="food-info">
                                <h3 class="food-name">{{ class.className }}</h3>
                                <p class="food-category">Dietary category: {{ class.category | title }}</p>
                                <p class="food-chef">Created By {{ class.hostChef }}</p>
                                <a href="cooking_classes/view/?search={{ class.className }}" class="class-card-link"></a>
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <p>No Classes found.</p>
                {% endif %}
            ''', classes=filtered_class)
            return jsonify({'chef_cooking_classes_home': cooking_class_home})

        all_classes = CookingClass.query.all()
        return render_template('chef_cooking_classes_home.html', classes=all_classes,
                               is_authenticated=current_user.is_authenticated)

    @app.route('/cooking_classes', methods=['GET'])
    def cooking_classes_homepage():
        if not current_user.is_authenticated:
            return render_template('homepage.html', alert=True)
        all_classes = CookingClass.query.all()
        return render_template('cooking_classes_home.html', classes=all_classes,
                               is_authenticated=current_user.is_authenticated)

    @app.route('/chef/create_cooking_class', methods=['GET', 'POST'])
    def add_cooking_class():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)

        chef = Chef.query.filter_by(email=current_user.email).first()
        if request.method == 'POST':
            class_Name = request.form.get('className')
            class_category = request.form.get('category')
            class_description = request.form.get('description')
            image_file = request.files.get('image')
            host_chef = request.form.get('host_chef')

            # Build steps structure
            count = 1
            all_class_steps = {'host_chef': host_chef}
            while request.form.get('step_num' + str(count)) is not None:
                cur_image_file = request.files.get('step_url' + str(count))
                cur_image_url = ''
                if cur_image_file and cur_image_file.filename:
                    filename = secure_filename(cur_image_file.filename)
                    chef_folder = os.path.join('static', 'images', str(chef.id))
                    os.makedirs(chef_folder, exist_ok=True)
                    image_path = os.path.join(chef_folder, filename)
                    cur_image_file.save(image_path)
                    cur_image_url = os.path.join('images', str(chef.id), filename)

                step_entry = {
                    'step_num': request.form.get('step_num' + str(count)),
                    'procedure': request.form.get('procedure' + str(count)),
                    'step_url': cur_image_url
                }
                if 'steps' not in all_class_steps:
                    all_class_steps['steps'] = [step_entry]
                else:
                    all_class_steps['steps'].append(step_entry)
                count += 1

            # Build ingredients structure
            count_ingredients = 1
            all_ingredients = {}
            while request.form.get('quantity' + str(count_ingredients)) is not None:
                ingredient_entry = {
                    'quantity': request.form.get('quantity' + str(count_ingredients)),
                    'name': request.form.get('name' + str(count_ingredients))
                }
                if 'ingredients' not in all_ingredients:
                    all_ingredients['ingredients'] = [ingredient_entry]
                else:
                    all_ingredients['ingredients'].append(ingredient_entry)
                count_ingredients += 1

            # Main image
            image_url = ''
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                chef_folder = os.path.join('static', 'images', str(chef.id))
                os.makedirs(chef_folder, exist_ok=True)
                image_path = os.path.join(chef_folder, filename)
                image_file.save(image_path)
                image_url = os.path.join('images', str(chef.id), filename)

            new_class = CookingClass(
                className=class_Name,
                category=class_category,
                description=class_description,
                image_url=image_url,
                hostChef=str(host_chef),
                ingredients=str(all_ingredients),
                steps=str(all_class_steps)
            )
            db.session.add(new_class)
            db.session.commit()

            return jsonify({'success': True, 'message': 'Food item added successfully'})

        return render_template('create_cooking_class.html', user=current_user)

    @app.route('/chef/cooking_classes/view/', methods=['GET'])
    def view_recipe():
        if not current_user.is_authenticated:
            return render_template('homepage.html', alert=True)

        search = request.args.get('search')
        searched_class = CookingClass.query.filter_by(className=search).first()
        if not searched_class:
            return render_template('view_class.html', classes=None, all_ingredients=None,
                                   all_steps=None, is_authenticated=current_user.is_authenticated)

        # Stored as stringified dicts
        all_class_steps = searched_class.steps
        all_ingredients_dict = searched_class.ingredients

        all_steps_dict = eval(all_class_steps) if all_class_steps else None
        all_ingredients_dict_html = eval(all_ingredients_dict) if all_ingredients_dict else None

        return render_template('view_class.html',
                               classes=searched_class,
                               all_ingredients=all_ingredients_dict_html,
                               all_steps=all_steps_dict,
                               is_authenticated=current_user.is_authenticated)

    # ---------------------------
    # Orders (dummy)
    # ---------------------------
    @app.route('/process_order', methods=['POST'])
    def process_order():
        data = request.json
        # card_number = data.get('cardNumber')  # intentionally unused (demo only)
        # expiry_date = data.get('expiryDate')
        # cvv = data.get('cvv')
        print("Get fake credit card!! Do nothing")
        return jsonify({'success': True, 'message': 'Order processed successfully'})

    return app


if __name__ == '__main__':
    # Dev server for local use only; production will use WSGI/gunicorn.
    app = create_app()
    app.run(debug=True)
