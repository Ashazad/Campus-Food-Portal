import os
from flask import render_template, request, jsonify, render_template_string, redirect, url_for
from flask import Flask
from werkzeug.utils import secure_filename
from extensions import db, login_manager
from flask_login import LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Chef, Food, CookingClass
from datetime import datetime
from sqlalchemy.orm import joinedload
from flask_login import current_user
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
import json

# def add_sample_foods():
#     if not Food.query.first():
#         food1 = Food(foodID=1, foodName="cereal", dietary_category="dairy", price="12.5", image_url="images/dish1.png", chef_id="27b0bbf2-a82d-444d-97d2-4906c9f8c6c7")
#         food2 = Food(foodID=2, foodName="caesar salad", dietary_category="vegetarian", price="12.5", image_url="images/dish2.png", chef_id="a682141f-56ac-4a5e-a5ff-0a7c4c475fdb")
#         food3 = Food(foodID=3, foodName="beef steak", dietary_category="meat", price="12.5", image_url="images/dish3.png", chef_id="a682141f-56ac-4a5e-a5ff-0a7c4c475fdb")
#         db.session.add_all([food1, food2, food3])
#         db.session.commit()
#         print("Sample foods added to the database.")


def create_app():
    app = Flask(__name__, static_url_path='', static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cuisine_connect.db'
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_ECHO'] = True

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login_view'
    with app.app_context():
        db.create_all()
        # add_sample_foods()

    @login_manager.user_loader
    def load_user(user_uuid):
        # Attempt to load the user from the User table
        user = User.query.filter_by(id=user_uuid).first()
        if user:
            return user

        chef = Chef.query.filter_by(id=user_uuid).first()
        if chef:
            return chef

        return None

    @app.route('/')
    def index():
        return render_template('homepage.html')

    @app.route('/logout')
    def logout():
        logout_user()
        return render_template('landing.html')

    @app.route('/landing')
    def landing():
        return render_template('landing.html')

    # Add a new route to process the order
    @app.route('/process_order', methods=['POST'])
    def process_order():
        # Retrieve credit card information from the request
        data = request.json
        card_number = data.get('cardNumber')
        expiry_date = data.get('expiryDate')
        cvv = data.get('cvv')

        print("Get fake credit card!! Do nothing")


        return jsonify({'success': True, 'message': 'Order processed successfully'})
    @app.route('/create_account', methods=['GET', 'POST'])
    def create_account():
        if request.method == 'POST':
            data = request.get_json()
            email = data.get('email')
            first_name = data.get('first-name', '')
            last_name = data.get('last-name', '')
            dob_str = data.get('dob')
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            password_hash = generate_password_hash(data.get('password'))
            account_type = data.get('account-type')
            user_exists = User.query.filter(User.email == email, User.role == 'user').first() is not None
            chef_exists = User.query.filter(User.email == email, User.role == 'chef').first() is not None
            if user_exists and account_type == 'consumer':
                return jsonify({'success': False, 'message': 'Account already exists with this email.'}), 400
            if chef_exists and account_type == 'chef':
                return jsonify({'success': False, 'message': 'Account already exists with this email.'}), 400
            if account_type == 'consumer':
                user = User(email=email, first_name=first_name, last_name=last_name, password=password_hash, dob=dob, role="user")
                db.session.add(user)
            else:
                business_name = data.get('business-name')
                order_location = data.get('map-options')
                location = data.get('location')
                user = User(email=email, first_name=first_name, last_name=last_name, password=password_hash, dob=dob, role="chef")
                chef = Chef(email=email, first_name=first_name, last_name=last_name, password=password_hash, dob=dob, business_name=business_name, location=location, order_location=order_location)
                db.session.add(user)
                db.session.add(chef)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Account created successfully'})
        return render_template('create_account.html')

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
                    return jsonify({'success': True, 'message': 'Logged in successfully',
                                    'redirect_url': url_for('chef_marketplace_home_page')})
                else:
                    return jsonify({'success': True, 'message': 'Logged in successfully',
                                    'redirect_url': url_for('marketplace_home_page')})

            return jsonify({'success': False, 'message': 'Login failed. Please check your credentials and try again.'})

        return render_template('login.html')

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
                filtered_foods = Food.query.options(joinedload(Food.chef)).filter_by(dietary_category=category).all()

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
        else:
            all_foods = Food.query.all()
            return render_template('marketplace_home_page.html', foods=all_foods, is_authenticated=current_user.is_authenticated)

    @app.route('/chef/marketplace_home_page', methods=['GET', 'POST'])
    def chef_marketplace_home_page():
        if not current_user.is_authenticated or current_user.role != 'chef':
            # Redirect to homepage with alert if user is not authenticated or not a chef
            return render_template('homepage.html', alert=True)
        if request.method == 'POST':
            data = request.json
            category = data.get('diet-category', 'none')
            chef = Chef.query.filter_by(email=current_user.email).first()
            # Filter foods based on the dietary category and current chef's ID
            if category == 'none':
                filtered_foods = Food.query.filter_by(chef_id=chef.id).all()
            else:
                filtered_foods = Food.query.options(joinedload(Food.chef)).filter(Food.dietary_category == category,
                                                                                  Food.chef_id == chef.id).all()

            foods_html = render_template_string('''
                {% if foods %}
                    {% for food in foods %}
                    <div class="food-item">
                        <img src="{{ url_for('static', filename=food.image_url) }}" alt="{{ food.foodName }}" class="food-image">
                        <div class="food-info">
                            <h3 class="food-name">{{ food.foodName }}</h3>
                            <p class="food-price">{{ food.price }} CAD</p>
                            <p class="food-category">{{ food.dietary_category }}</p>
                            <p class="food-chef">Created By {{ chef.first_name}} {{ chef.last_name }}</p>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p>No foods found.</p>
                {% endif %}
            ''', foods=filtered_foods, chef=chef)
            return jsonify({'foods_html': foods_html})
        else:
            # Display all foods created by the current chef
            chef = Chef.query.filter_by(email=current_user.email).first()

            if chef:
                all_foods = Food.query.filter_by(chef_id=chef.id).all()
            else:
                all_foods = None

            start_time = chef.start_time
            end_time = chef.end_time
            all_foods = Food.query.filter_by(chef_id=chef.id).all()
            return render_template('chef_marketplace_home_page.html', foods=all_foods, chef=chef,start_time=start_time, end_time=end_time)

    @app.route('/chef/add_food_item', methods=['GET', 'POST'])
    def add_food_item():
        if not current_user.is_authenticated:
            return render_template('homepage.html', alert=True)
        chef = Chef.query.filter_by(email=current_user.email).first()
        if request.method == 'POST':
            food_name = request.form.get('foodName')
            dietary_category = request.form.get('dietary_category')
            price = request.form.get('price')
            image_file = request.files['image']

            if image_file:
                filename = secure_filename(image_file.filename)
                chef_folder = os.path.join('static', 'images', str(chef.id))
                if not os.path.exists(chef_folder):
                    os.makedirs(chef_folder)
                image_path = os.path.join(chef_folder, filename)
                image_file.save(image_path)
                image_url = '/' + 'images/' + str(chef.id) + '/' + filename
            else:
                image_url = ''
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

    @app.route('/chef/cooking_classes', methods=['GET', 'POST'])
    def chef_cooking_classes_homepage():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)
        else:
            if request.method == 'POST':
                data = request.json
                html_category = data.get('class-category', 'none')
                print(html_category)
                # quered_classes = CookingClass.query.filter_by(category=html_category).all()
                # Filter foods based on the dietary category and current chef's ID
                if html_category == 'none':
                    filtered_class = CookingClass.query.filter_by().all()
                else:
                    filtered_class = CookingClass.query.filter_by(category=html_category).all()

                cooking_class_home = render_template_string('''
                    {% if classes %}
                        {% for class in classes %}
                            <div class="class-card">
                                <img src="{{ url_for('static', filename=class.image_url) }}" alt="{{ class.className }}" class="food-image">
                                <div class="food-info">
                                    <h3 class="food-name">{{ class.className}}</h3>
                                    <p class="food-category">Dietary category: {{ class.category | title }}</p>
                                    <p class="food-chef">Created By {{ class.host_chef }}</p>
                                    <a href="cooking_classes/view/?search={{class.className}}" class="class-card-link"></a>
                                </div>
                            </div>
                        {% endfor %}
                    {% else %}
                        <p>No Classes found.</p>
                    {% endif %}
                ''', all_classes=filtered_class)
                return jsonify({'chef_cooking_classes_home': cooking_class_home})
            else:
                all_classes = CookingClass.query.all()
                return render_template('chef_cooking_classes_home.html', classes=all_classes, is_authenticated=current_user.is_authenticated)
        
    @app.route('/cooking_classes', methods=['GET'])
    def cooking_classes_homepage():
        if not current_user.is_authenticated:
            return render_template('homepage.html', alert=True)
        else:
            all_classes = CookingClass.query.all()
            return render_template('cooking_classes_home.html', classes=all_classes, is_authenticated=current_user.is_authenticated)
        
    @app.route('/chef/create_cooking_class', methods=['GET', 'POST'])
    def add_cooking_class():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)
        chef = Chef.query.filter_by(email=current_user.email).first()
        if request.method == 'POST':
            class_Name = request.form.get('className')
            class_category = request.form.get('category')
            class_description = request.form.get('description')
            image_file = request.files['image']
            host_chef = request.form.get('host_chef')

            count = 1
            cur_image_url = ''
            all_class_steps = {'host_chef': host_chef}
            # Getting the Steps from form
            while request.form.get('step_num' + str(count)) != None:
                cur_image_file = request.files['step_url' + str(count)]
                
                if cur_image_file:
                    filename = secure_filename(cur_image_file.filename)
                    chef_folder = os.path.join('static', 'images', str(chef.id))
                    if not os.path.exists(chef_folder):
                        os.makedirs(chef_folder)
                    image_path = os.path.join(chef_folder, filename)
                    cur_image_file.save(image_path)
                    cur_image_url = '/' + os.path.join('images', str(chef.id), filename)
                else:
                    cur_image_url = ''
                if 'steps' not in all_class_steps:
                    all_class_steps['steps'] = [{'step_num': request.form.get('step_num' + str(count))
                                                , 'procedure': request.form.get('procedure' + str(count)),
                                                'step_url': cur_image_url}]
                else:
                    all_class_steps['steps'].append({'step_num': request.form.get('step_num' + str(count))
                                                , 'procedure': request.form.get('procedure' + str(count)),
                                                'step_url': cur_image_url})
                count += 1
            
            count_ingredients = 1
            all_ingredients = {}
            # Getting the Ingredients from form
            while request.form.get('quantity' + str(count_ingredients)) != None:
                if 'ingredients' not in all_ingredients:
                    all_ingredients['ingredients'] = [{'quantity': request.form.get('quantity' + str(count_ingredients))
                                                , 'name': request.form.get('name' + str(count_ingredients))}]
                else:
                    all_ingredients['ingredients'].append({'quantity': request.form.get('quantity' + str(count_ingredients))
                                                , 'name': request.form.get('name' + str(count_ingredients))})
                count_ingredients += 1





            if image_file:
                filename = secure_filename(image_file.filename)
                chef_folder = os.path.join('static', 'images', str(chef.id))
                if not os.path.exists(chef_folder):
                    os.makedirs(chef_folder)
                image_path = os.path.join(chef_folder, filename)
                image_file.save(image_path)
                image_url = '/' + os.path.join('images', str(chef.id), filename)
            else:
                image_url = ''


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
        search = request.args.get('search')
        if not current_user.is_authenticated:
            return render_template('homepage.html', alert=True)
        else:
            searched_class = CookingClass.query.filter_by(className=search).first()
            all_class_steps = searched_class.steps
            all_ingredients_dict = searched_class.ingredients
            if all_class_steps is not None:
                all_steps_dict = eval(all_class_steps)
                # all_class_steps_data = json.loads(all_class_steps)
                # step_nums = sorted(list(all_class_steps_data.keys()))
                # for step in step_nums:
                #     if not step.isnumeric():
                #         step_nums.remove(step)
            else:
                all_steps_dict = None
                # step_nums = None
            return render_template('view_class.html', classes=searched_class, all_ingredients=all_ingredients_dict,
                                   all_steps=all_steps_dict, is_authenticated=current_user.is_authenticated)
        
    
    @app.route('/chef/modify_open_hours', methods=['GET', 'POST'])
    def modify_open_hours():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)
        if request.method == 'POST':
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')

            # Find the current chef
            chef = Chef.query.filter_by(email=current_user.email).first()
            # Update the start and end times
            chef.start_time = start_time
            chef.end_time = end_time

            # Commit changes to the database
            db.session.commit()
        return render_template('modify_open_hours.html')


    @app.route('/chef/remove_food_item', methods=['GET', 'POST'])
    def remove_food_item():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)

        if request.method == 'POST':
            # Extract the food ID from the request data
            food_id = request.form.get('foodID')

            food = Food.query.get(food_id)
            if food:
                food_data = {
                    'foodID': food.foodID,
                    'foodName': food.foodName,
                    'dietary_category': food.dietary_category,
                    'price': str(food.price),
                    'image_url': food.image_url,
                    'chef_id': food.chef_id
                }
                db.session.delete(food)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Food item removed successfully'})
            else:
                return jsonify({'success': False, 'message': food_id})
        chef = Chef.query.filter_by(email=current_user.email).first()
        all_foods = Food.query.filter_by(chef_id=chef.id).all()
        return render_template('remove_food_item.html', foods=all_foods)



    @app.route('/chef/edit_profile', methods=['GET', 'POST'])
    def edit_profile():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)

        chef = Chef.query.filter_by(email=current_user.email).first()
        if not chef:
            return jsonify({'success': False, 'message': 'Chef not found'}), 404

        if request.method == 'POST':
            chef.about_me = request.form.get('about_me')

            chef_folder = os.path.join('static/images', str(chef.id))
            if not os.path.exists(chef_folder):
                os.makedirs(chef_folder)

            profile_picture = request.files.get('profile')
            if profile_picture and profile_picture.filename:
                filename = secure_filename(profile_picture.filename)
                filepath = os.path.join(chef_folder, filename)
                profile_picture.save(filepath)
                chef.profile_url = os.path.join('images', str(chef.id), filename)

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


    @app.route('/chef/cooking_classes', methods=['GET', 'POST'])
    def chef_cooking_classes_homepage():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)
        else:
            if request.method == 'POST':
                data = request.json
                html_category = data.get('class-category', 'none')
                print(html_category)
                # quered_classes = CookingClass.query.filter_by(category=html_category).all()
                # Filter foods based on the dietary category and current chef's ID
                if html_category == 'none':
                    filtered_class = CookingClass.query.filter_by().all()
                else:
                    filtered_class = CookingClass.query.filter_by(category=html_category).all()

                cooking_class_home = render_template_string('''
                    {% if classes %}
                        {% for class in classes %}
                            <div class="class-card">
                                <img src="{{ url_for('static', filename=class.image_url) }}" alt="{{ class.className }}" class="food-image">
                                <div class="food-info">
                                    <h3 class="food-name">{{ class.className}}</h3>
                                    <p class="food-category">Dietary category: {{ class.category | title }}</p>
                                    <p class="food-chef">Created By {{ class.host_chef }}</p>
                                    <a href="cooking_classes/view/?search={{class.className}}" class="class-card-link"></a>
                                </div>
                            </div>
                        {% endfor %}
                    {% else %}
                        <p>No Classes found.</p>
                    {% endif %}
                ''', all_classes=filtered_class)
                return jsonify({'chef_cooking_classes_home': cooking_class_home})
            else:
                all_classes = CookingClass.query.all()
                return render_template('chef_cooking_classes_home.html', classes=all_classes, is_authenticated=current_user.is_authenticated)
        
    @app.route('/cooking_classes', methods=['GET'])
    def cooking_classes_homepage():
        if not current_user.is_authenticated:
            return render_template('homepage.html', alert=True)
        else:
            all_classes = CookingClass.query.all()
            return render_template('cooking_classes_home.html', classes=all_classes, is_authenticated=current_user.is_authenticated)
        
    @app.route('/chef/create_cooking_class', methods=['GET', 'POST'])
    def add_cooking_class():
        if not current_user.is_authenticated or current_user.role != 'chef':
            return render_template('homepage.html', alert=True)
        chef = Chef.query.filter_by(email=current_user.email).first()
        if request.method == 'POST':
            class_Name = request.form.get('className')
            class_category = request.form.get('category')
            class_description = request.form.get('description')
            image_file = request.files['image']
            host_chef = request.form.get('host_chef')

            count = 1
            cur_image_url = ''
            all_class_steps = {'host_chef': host_chef}
            # Getting the Steps from form
            while request.form.get('step_num' + str(count)) != None:
                cur_image_file = request.files['step_url' + str(count)]
                
                if cur_image_file:
                    filename = secure_filename(cur_image_file.filename)
                    chef_folder = os.path.join('static', 'images', str(chef.id))
                    if not os.path.exists(chef_folder):
                        os.makedirs(chef_folder)
                    image_path = os.path.join(chef_folder, filename)
                    cur_image_file.save(image_path)
                    cur_image_url = '/' + os.path.join('images', str(chef.id), filename)
                else:
                    cur_image_url = ''
                if 'steps' not in all_class_steps:
                    all_class_steps['steps'] = [{'step_num': request.form.get('step_num' + str(count))
                                                , 'procedure': request.form.get('procedure' + str(count)),
                                                'step_url': cur_image_url}]
                else:
                    all_class_steps['steps'].append({'step_num': request.form.get('step_num' + str(count))
                                                , 'procedure': request.form.get('procedure' + str(count)),
                                                'step_url': cur_image_url})
                count += 1
            
            count_ingredients = 1
            all_ingredients = {}
            # Getting the Ingredients from form
            while request.form.get('quantity' + str(count_ingredients)) != None:
                if 'ingredients' not in all_ingredients:
                    all_ingredients['ingredients'] = [{'quantity': request.form.get('quantity' + str(count_ingredients))
                                                , 'name': request.form.get('name' + str(count_ingredients))}]
                else:
                    all_ingredients['ingredients'].append({'quantity': request.form.get('quantity' + str(count_ingredients))
                                                , 'name': request.form.get('name' + str(count_ingredients))})
                count_ingredients += 1





            if image_file:
                filename = secure_filename(image_file.filename)
                chef_folder = os.path.join('static', 'images', str(chef.id))
                if not os.path.exists(chef_folder):
                    os.makedirs(chef_folder)
                image_path = os.path.join(chef_folder, filename)
                image_file.save(image_path)
                image_url = '/' + os.path.join('images', str(chef.id), filename)
            else:
                image_url = ''


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
        search = request.args.get('search')
        if not current_user.is_authenticated:
            return render_template('homepage.html', alert=True)
        else:
            searched_class = CookingClass.query.filter_by(className=search).first()
            all_class_steps = searched_class.steps
            all_ingredients_dict = searched_class.ingredients

            if all_class_steps is not None:
                all_steps_dict = eval(all_class_steps)
            else:
                all_steps_dict = None

            if all_ingredients_dict is not None:
                all_ingredients_dict_html = eval(all_ingredients_dict)
            else:
                all_ingredients_dict_html = None
                # step_nums = None
            return render_template('view_class.html', classes=searched_class, all_ingredients=all_ingredients_dict_html,
                                   all_steps=all_steps_dict, is_authenticated=current_user.is_authenticated)

    return app


if __name__ == '__main__':
    
    app = create_app()
    app.secret_key = 'jonathanchoi'
    app.run(debug=True)
