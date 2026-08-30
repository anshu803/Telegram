import sqlite3
from flask import Blueprint, render_template_string, request, redirect, url_for, session

admin_app = Blueprint('admin', __name__)

ADMIN_PASSWORD = "admin123"  # Change your password here
DB_NAME = "bot_data.db"

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def get_setting(key, default=""):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else default

def set_setting(key, value):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# HTML TEMPLATES
# ---------------------------------------------------------
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-dark d-flex align-items-center justify-content-center" style="height: 100vh;">
    <div class="card p-4 shadow-lg text-white bg-secondary" style="width: 350px;">
        <h4 class="text-center mb-3">🔒 Admin Login</h4>
        {% if error %}<div class="alert alert-danger p-2">{{ error }}</div>{% endif %}
        <form action="/login" method="POST">
            <div class="mb-3">
                <label>Password</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button class="btn btn-primary w-100">Login</button>
        </form>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f172a; color: #f8fafc; }
        .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; color: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark px-3 mb-4">
        <a class="navbar-brand font-weight-bold" href="#">⚡ Bot Web Control</a>
        <a href="/logout" class="btn btn-outline-danger btn-sm">Logout</a>
    </nav>

    <div class="container mb-5">
        <div class="row g-3 mb-4">
            <div class="col-md-4"><div class="card p-3 bg-primary"><h5>👥 Total Users</h5><h2>{{ total_users }}</h2></div></div>
            <div class="col-md-4"><div class="card p-3 bg-success"><h5>💰 Total Revenue</h5><h2>₹{{ total_earnings }}</h2></div></div>
            <div class="col-md-4"><div class="card p-3 bg-warning text-dark"><h5>⏳ Pending Requests</h5><h2>{{ pending_count }}</h2></div></div>
        </div>

        <div class="card p-4 mb-4">
            <h5 class="mb-3 text-warning">⚙️ Payment & QR Settings</h5>
            <form action="/update-settings" method="POST" class="row g-3">
                <div class="col-md-4">
                    <label>UPI ID</label>
                    <input type="text" name="upi_id" class="form-control bg-dark text-white" value="{{ upi_id }}" required>
                </div>
                <div class="col-md-4">
                    <label>UPI Name</label>
                    <input type="text" name="upi_name" class="form-control bg-dark text-white" value="{{ upi_name }}" required>
                </div>
                <div class="col-md-4">
                    <label>Custom QR Code Image URL</label>
                    <input type="text" name="qr_url" class="form-control bg-dark text-white" value="{{ qr_url }}">
                </div>
                <div class="col-12"><button type="submit" class="btn btn-primary">Save Settings</button></div>
            </form>
        </div>

        <div class="card p-4">
            <h5 class="mb-3 text-info">💳 Recent Payments</h5>
            <table class="table table-dark table-hover">
                <thead>
                    <tr><th>Txn ID</th><th>User ID</th><th>Plan</th><th>Amount</th><th>Status</th></tr>
                </thead>
                <tbody>
                    {% for tx in transactions %}
                    <tr>
                        <td><code>{{ tx[0] }}</code></td>
                        <td>{{ tx[1] }}</td>
                        <td>{{ tx[3] }}</td>
                        <td>₹{{ tx[4] }}</td>
                        <td>
                            {% if tx[5] == 'APPROVED' %}<span class="badge bg-success">APPROVED</span>
                            {% elif tx[5] == 'REJECTED' %}<span class="badge bg-danger">REJECTED</span>
                            {% else %}<span class="badge bg-warning text-dark">PENDING</span>{% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------
@admin_app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template_string(LOGIN_HTML)
    return redirect('/admin')

@admin_app.route('/admin')
def dashboard():
    if not session.get('logged_in'):
        return render_template_string(LOGIN_HTML)
        
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM transactions WHERE status='APPROVED'")
    total_earnings = c.fetchone()[0] or 0.0
    c.execute("SELECT COUNT(*) FROM transactions WHERE status='PENDING'")
    pending_count = c.fetchone()[0]
    c.execute("SELECT txn_id, user_id, username, plan_name, amount, status FROM transactions ORDER BY created_at DESC LIMIT 50")
    transactions = c.fetchall()
    conn.close()
    
    return render_template_string(
        DASHBOARD_HTML,
        total_users=total_users,
        total_earnings=total_earnings,
        pending_count=pending_count,
        transactions=transactions,
        upi_id=get_setting('upi_id'),
        upi_name=get_setting('upi_name'),
        qr_url=get_setting('qr_url')
    )

@admin_app.route('/login', methods=['POST'])
def login():
    if request.form.get('password') == ADMIN_PASSWORD:
        session['logged_in'] = True
        return redirect('/admin')
    return render_template_string(LOGIN_HTML, error="Incorrect Password!")

@admin_app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

@admin_app.route('/update-settings', methods=['POST'])
def update_settings():
    if not session.get('logged_in'): return redirect('/')
    set_setting('upi_id', request.form.get('upi_id'))
    set_setting('upi_name', request.form.get('upi_name'))
    set_setting('qr_url', request.form.get('qr_url'))
    return redirect('/admin')
