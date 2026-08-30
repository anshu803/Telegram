<?php
session_start();

// ---------------------------------------------------------
// CONFIGURATION
// ---------------------------------------------------------
define('ADMIN_PASSWORD', 'admin123'); // Dashboard Password
define('DB_PATH', 'bot_data.db');     // SQLite Database File Path

// ---------------------------------------------------------
// LOGIN / LOGOUT HANDLING
// ---------------------------------------------------------
$error = '';
if (isset($_POST['login_pass'])) {
    if ($_POST['login_pass'] === ADMIN_PASSWORD) {
        $_SESSION['admin_logged_in'] = true;
    } else {
        $error = "Incorrect Password!";
    }
}

if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    session_destroy();
    header("Location: admin.php");
    exit();
}

// Show Login Page if not authenticated
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-dark d-flex align-items-center justify-content-center" style="height: 100vh;">
    <div class="card p-4 shadow-lg text-white bg-secondary" style="width: 350px; border-radius: 12px;">
        <h4 class="text-center mb-3">🔒 Admin Login</h4>
        <?php if ($error): ?>
            <div class="alert alert-danger p-2"><?= $error ?></div>
        <?php endif; ?>
        <form method="POST">
            <div class="mb-3">
                <label class="form-label">Password</label>
                <input type="password" name="login_pass" class="form-control" placeholder="Enter password" required>
            </div>
            <button class="btn btn-primary w-100">Login to Dashboard</button>
        </form>
    </div>
</body>
</html>
<?php
    exit();
}

// ---------------------------------------------------------
// CONNECT TO SQLITE DATABASE
// ---------------------------------------------------------
try {
    $db = new PDO('sqlite:' . DB_PATH);
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (Exception $e) {
    die("<h3 style='color:red; text-align:center; margin-top:50px;'>Database File (bot_data.db) Not Found or Permission Denied!</h3>");
}

// Handle Settings Update (UPI / QR URL)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['update_settings'])) {
    $upi_id = $_POST['upi_id'] ?? '';
    $upi_name = $_POST['upi_name'] ?? '';
    $qr_url = $_POST['qr_url'] ?? '';

    $stmt = $db->prepare("INSERT OR REPLACE INTO settings (key, value) VALUES ('upi_id', ?)");
    $stmt->execute([$upi_id]);

    $stmt = $db->prepare("INSERT OR REPLACE INTO settings (key, value) VALUES ('upi_name', ?)");
    $stmt->execute([$upi_name]);

    $stmt = $db->prepare("INSERT OR REPLACE INTO settings (key, value) VALUES ('qr_url', ?)");
    $stmt->execute([$qr_url]);

    $success_msg = "Settings updated successfully!";
}

// ---------------------------------------------------------
// FETCH DASHBOARD STATS
// ---------------------------------------------------------
// Total Users
$user_count = $db->query("SELECT COUNT(*) FROM users")->fetchColumn();

// Total Earnings (Approved Payments)
$total_earnings = $db->query("SELECT SUM(amount) FROM transactions WHERE status='APPROVED'")->fetchColumn() ?: 0;

// Pending Requests Count
$pending_count = $db->query("SELECT COUNT(*) FROM transactions WHERE status='PENDING'")->fetchColumn();

// Settings Data
$settings = [];
$res = $db->query("SELECT key, value FROM settings");
while ($row = $res->fetch(PDO::FETCH_ASSOC)) {
    $settings[$row['key']] = $row['value'];
}

// Transactions List
$transactions = $db->query("SELECT txn_id, user_id, plan_name, amount, status, created_at FROM transactions ORDER BY created_at DESC LIMIT 50")->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard | Bot Control</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f172a; color: #f8fafc; }
        .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; color: white; }
        .stat-box { background: linear-gradient(135deg, #2563eb, #1d4ed8); }
        .stat-box-2 { background: linear-gradient(135deg, #16a34a, #15803d); }
        .stat-box-3 { background: linear-gradient(135deg, #d97706, #b45309); }
        .table-dark { --bs-table-bg: #1e293b; }
    </style>
</head>
<body>

    <nav class="navbar navbar-dark bg-dark border-bottom border-secondary px-3 mb-4">
        <a class="navbar-brand font-weight-bold" href="#">⚡ Bot Control Admin Panel</a>
        <a href="admin.php?action=logout" class="btn btn-outline-danger btn-sm">Logout</a>
    </nav>

    <div class="container mb-5">

        <?php if (isset($success_msg)): ?>
            <div class="alert alert-success"><?= $success_msg ?></div>
        <?php endif; ?>

        <!-- STATS SECTION -->
        <div class="row g-3 mb-4">
            <div class="col-md-4">
                <div class="card p-3 stat-box shadow">
                    <h5>👥 Total Users</h5>
                    <h2><?= number_format($user_count) ?></h2>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card p-3 stat-box-2 shadow">
                    <h5>💰 Total Revenue</h5>
                    <h2>₹<?= number_format($total_earnings, 2) ?></h2>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card p-3 stat-box-3 shadow">
                    <h5>⏳ Pending Requests</h5>
                    <h2><?= number_format($pending_count) ?></h2>
                </div>
            </div>
        </div>

        <!-- SETTINGS SECTION -->
        <div class="card p-4 mb-4 shadow">
            <h5 class="mb-3 text-warning">⚙️ Payment & QR Settings</h5>
            <form method="POST" class="row g-3">
                <input type="hidden" name="update_settings" value="1">
                <div class="col-md-4">
                    <label class="form-label">UPI ID</label>
                    <input type="text" name="upi_id" class="form-control bg-dark text-white border-secondary" value="<?= htmlspecialchars($settings['upi_id'] ?? '') ?>" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">UPI Name</label>
                    <input type="text" name="upi_name" class="form-control bg-dark text-white border-secondary" value="<?= htmlspecialchars($settings['upi_name'] ?? '') ?>" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Custom QR Code Image URL</label>
                    <input type="text" name="qr_url" class="form-control bg-dark text-white border-secondary" value="<?= htmlspecialchars($settings['qr_url'] ?? '') ?>" placeholder="https://i.ibb.co/...">
                </div>
                <div class="col-12">
                    <button type="submit" class="btn btn-primary">Save Settings</button>
                </div>
            </form>
        </div>

        <!-- TRANSACTIONS TABLE -->
        <div class="card p-4 shadow">
            <h5 class="mb-3 text-info">💳 Recent Payment History</h5>
            <div class="table-responsive">
                <table class="table table-dark table-hover align-middle">
                    <thead>
                        <tr>
                            <th>Txn ID</th>
                            <th>User ID</th>
                            <th>Plan</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php if (count($transactions) > 0): ?>
                            <?php foreach ($transactions as $tx): ?>
                                <tr>
                                    <td><code><?= htmlspecialchars($tx['txn_id']) ?></code></td>
                                    <td><?= htmlspecialchars($tx['user_id']) ?></td>
                                    <td><?= htmlspecialchars($tx['plan_name']) ?></td>
                                    <td>₹<?= htmlspecialchars($tx['amount']) ?></td>
                                    <td>
                                        <?php if ($tx['status'] === 'APPROVED'): ?>
                                            <span class="badge bg-success">APPROVED</span>
                                        <?php elseif ($tx['status'] === 'REJECTED'): ?>
                                            <span class="badge bg-danger">REJECTED</span>
                                        <?php else: ?>
                                            <span class="badge bg-warning text-dark">PENDING</span>
                                        <?php endif; ?>
                                    </td>
                                    <td><small><?= htmlspecialchars($tx['created_at']) ?></small></td>
                                </tr>
                            <?php endforeach; ?>
                        <?php else: ?>
                            <tr>
                                <td colspan="6" class="text-center text-muted">No transactions found yet.</td>
                            </tr>
                        <?php endif; ?>
                    </tbody>
                </table>
            </div>
        </div>

    </div>

</body>
</html>
