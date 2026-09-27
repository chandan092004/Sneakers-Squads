# 👟 Sneakers Squads

A full-stack modern sneaker eCommerce web application built with **Django** and **MySQL**.

---

## 🚀 Features

- **Storefront & Catalog**: Explore categories (Men, Women, Accessories, and custom admin-created categories).
- **Product Details**: High-resolution sneaker showcases with dynamic data syncing.
- **User Authentication & Accounts**: User registration, login, profile management, and dashboard.
- **Cart & Checkout**: Interactive shopping bag and checkout API.
- **Admin Dashboard**: Full administrative portal for managing inventory, categories, orders, and users.
- **Responsive Modern UI**: Sleek, mobile-friendly design with intuitive navigation.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Django
- **Database**: MySQL / SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Libraries**: Pillow, PyMySQL, Cryptography, Asgiref

---

## 🏁 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/chandan092004/Sneakers-Squads.git
cd Sneakers-Squads
```

### 2. Set up a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 📂 Project Structure

```
├── accounts/          # User authentication and customer portal app
├── sneakerweb/        # Core Django settings, URLs, and view controllers
├── templates/         # HTML templates
├── static/            # Static assets (CSS, JS, images, icons)
├── media/             # Uploaded user avatars and media
├── manage.py          # Django CLI management script
├── requirements.txt   # Project dependencies
└── run_server.bat     # Windows one-click server starter script
```
