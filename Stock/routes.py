import math
from flask import send_from_directory, render_template, url_for, flash, redirect, request, jsonify, abort, current_app, session
from flask_login import login_user, current_user, logout_user, login_required
from Stock import app, db, bcrypt, photos
from Stock.models import User, Product
from Stock.forms import EditUserForm, LoginForm, UserForm, AddProducts
import os, secrets, re
from functools import wraps



# Custom decorator to restrict access to admin-only routes
def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Check if the current user is an admin
        if not current_user.is_admin:
            # Flash a message and redirect if not an admin
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        # Call the original function if the user is an admin
        return func(*args, **kwargs)
    return decorated_function


#Default route, redirects to the login page
@app.route('/')
def route_default():
    return redirect(url_for('login'))

#Login route, handles user login
@app.route('/login', methods=['GET', "POST"])
def login():
    msg = ""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('home'))
        else:
            msg = "Login unsuccessful, please check your credentials"
    return render_template('login.html', msg=msg, form=form)


# Home route accessible after login, shows basic stats
@app.route('/home', strict_slashes=False)
@login_required
def home():
    users = User.query.count()
    products = Product.query.count()
    return render_template('home.html', users=users, products=products)

# Logout route, logs out the user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
 

#Add user route, accessibl to admin, add new users to the database
@app.route('/addUser', methods=["GET", "POST"])
@login_required
@admin_required
def addUser():
    msg = ""
    form = UserForm()
    if request.method == "POST":
        username = form.username.data.strip()
        email = form.email.data.strip()
        password = bcrypt.generate_password_hash(form.password.data)
        confirm = bcrypt.generate_password_hash(form.confirm.data)
        phone = form.phone.data.strip()
        #check if the username and email already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            msg = "Username already exists. Please choose a different username."
        elif existing_email:
            msg = "email already exists. Please choose a different email."
        elif form.password.data != form.confirm.data:
            msg = "Passwords must match."
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", form.email.data):
            msg = "Invalid email address"
        else:
            user = User(username=username, email=email, password=password,
            phone=phone)
            db.session.add(user)
            db.session.commit()
            msg = "User has been added"
            return redirect(url_for('users'))
    return render_template('add_user.html', form=form, msg=msg)


#View users route, accessible to admin, shows all users
@app.route('/users')
@login_required
@admin_required
def users():
    per_page = request.args.get('per_page', 4)
    page = int(request.args.get('page', 1))
    offset = (int(page) - 1) * int(per_page)
    users = User.query.order_by(User.id.asc()).limit(per_page).offset(offset)
    total_users = User.query.count()
    total_pages = math.ceil(total_users/ int(per_page))
    return render_template('users.html', users=users, per_page=per_page, page=page, total_pages=total_pages)
       


#Delete user route, accessibl to admin, deletes a user from the database
@app.route('/deleteuser/<int:id>', methods=["POST"])
@login_required
@admin_required
def deleteuser(id):
    user = User.query.get_or_404(id)
    if request.method == "POST" and current_user.id != user.id:
        db.session.delete(user)
        db.session.commit()
        flash(f'{user.username} Deleted', 'success')
        return redirect(url_for('users'))
    flash(f'Cant delete {user.username}', 'warning')
    return redirect(url_for('users'))


# Add product route , adds new products to the database
@app.route('/addproduct', methods=["GET", "POST"])
@login_required
def addproduct():
    form = AddProducts()
    msg = ""
    if request.method == "POST":
        name = form.name.data
        price = form.price.data
        description = form.description.data
        quantity = form.quantity.data
        image_1 = photos.save(request.files['image_1'] , name=secrets.token_hex(10) + '.')
        print(f"Image 1 name:{image_1}, its type:{type(image_1)}")
        if not re.match(r"^\d+(\.\d+)?$", form.price.data):
            msg = "invalid Price"
        else:
            product = Product(name=name, price=price, description=description, quantity=quantity,
            image_1=image_1)
            db.session.add(product)
            flash(f"{name} has been added to database.", 'success')
            db.session.commit()
            return redirect(url_for('products'))
    return render_template('add_product.html', form=form, msg=msg)
    

# View products route, shows all products
@app.route('/products')
@login_required
def products():
    per_page = request.args.get('per_page', 2)
    page = int(request.args.get('page', 1))
    offset = (int(page) - 1) * int(per_page)
    products = Product.query.order_by(Product.id.asc()).limit(per_page).offset(offset)
    total_products = Product.query.count()
    total_pages = math.ceil(total_products/ int(per_page))
    return render_template('products.html', products=products, per_page=per_page, page=page, total_pages=total_pages)

# Delete product route, delete a product from database
@app.route('/deleteproduct/<int:id>', methods=["POST"])
@login_required
def deleteproduct(id):
    product = Product.query.get_or_404(id)
    if request.method == "POST":
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_1))
            except Exception as e:
                print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f'{product.name} Deleted', 'success')
        return redirect(url_for('products'))
    flash(f'Cant delete {product.name}', 'warning')
    return redirect(url_for('products'))
        
# Update product route to update product details
@app.route('/updateproduct/<int:id>', methods=["GET", "POST"])
@login_required
def updateproduct(id):
    product = Product.query.get_or_404(id)
    form = AddProducts(request.form)
    msg = ""
    if request.method == "POST":
        form = AddProducts(request.form, obj=product)  # Bind the form to the product instance
        if form.validate_on_submit():
            product.name = form.name.data
            product.price = form.price.data
            product.description = form.description.data
            product.quantity = form.quantity.data
            
            # Handle image upload
            if 'image_1' in request.files:
                image_file = request.files['image_1']
                if image_file:
                    try:
                        # Delete old image if exists
                        if product.image_1:
                            old_image_path = os.path.join(current_app.root_path, 'static/images', product.image_1)
                            if os.path.exists(old_image_path):
                                os.unlink(old_image_path)
                        
                        # Save new image
                        image_filename = photos.save(image_file, name=secrets.token_hex(10) + '.')
                        product.image_1 = image_filename
                    except Exception as e:
                        flash(f"Error saving image: {str(e)}", 'danger')
                        return render_template('edit_product.html', form=form, product=product, msg=msg)
            try:
                db.session.commit()
                flash('Product Updated', 'success')
                return redirect(url_for('products'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error updating product: {str(e)}", 'danger')
    
    form.name.data = product.name
    form.price.data = product.price
    form.description.data = product.description
    form.quantity.data = product.quantity
    
    return render_template('edit_product.html', form=form, product=product, msg=msg)

# Account route accessible to all users
@app.route('/account')
@login_required
def account():
    user = User.query.get_or_404(current_user.id)
    form = EditUserForm(obj=user)
    return render_template('account.html', form=form, user=user) 

# Update account route, allows user to update their account details
@app.route('/updateaccount/<int:id>', methods=["GET", "POST"])
@login_required
def updateaccount(id):
    msg=""
    user = User.query.get_or_404(id)
    form = EditUserForm(request.form)
    if request.method == "POST":
        name = user.username
        email = user.email
        #check if the username and email already exists
        existing_user = User.query.filter_by(username=form.username.data.strip()).first()
        existing_email = User.query.filter_by(email=form.email.data.strip()).first()

        if name != form.username.data.strip() and existing_user:
            msg = "Username already exists. Please choose a different username."
        elif email != form.email.data.strip() and existing_email :
            msg = "email already exists. Please choose a different email."
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", form.email.data):
            msg = "Invalid email address"
        elif not re.match(r'^\d+$', form.phone.data):
            msg = "Invalid Phone Number"
        else:
            user.username = form.username.data.strip()
            user.email = form.email.data.strip()
            user.phone = form.phone.data.strip()
            db.session.commit()
            msg = "Profile Updated"
    form.username.data = user.username
    form.email.data = user.email
    form.phone.data = user.phone
    return render_template('account.html', form=form, user=user, msg=msg)
