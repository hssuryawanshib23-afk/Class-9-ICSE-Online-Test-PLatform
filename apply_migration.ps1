# Run this script to apply the admin test migration to your LOCAL SQLite database

Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host "APPLYING ADMIN TEST MIGRATION TO SQLite"
Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host ""

$dbPath = "database\quiz.db"
$sqlFile = "add_admin_tests_sqlite.sql"

# Check if database exists
if (-Not (Test-Path $dbPath)) {
    Write-Host "❌ Error: Database file not found at: $dbPath" -ForegroundColor Red
    Write-Host "Please make sure you're in the correct directory." -ForegroundColor Yellow
    exit 1
}

# Check if SQL file exists
if (-Not (Test-Path $sqlFile)) {
    Write-Host "❌ Error: SQL file not found: $sqlFile" -ForegroundColor Red
    exit 1
}

Write-Host "📂 Database: $dbPath" -ForegroundColor Cyan
Write-Host "📄 SQL File: $sqlFile" -ForegroundColor Cyan
Write-Host ""

# Apply migration
Write-Host "🔄 Applying migration..." -ForegroundColor Yellow

try {
    # Read SQL file
    $sql = Get-Content $sqlFile -Raw
    
    # Execute SQL using sqlite3 command line
    # If sqlite3 is not in PATH, you can use DB Browser for SQLite instead
    
    if (Get-Command sqlite3 -ErrorAction SilentlyContinue) {
        # sqlite3 is available
        $sql | sqlite3 $dbPath
        Write-Host "✅ Migration applied successfully!" -ForegroundColor Green
    } else {
        # sqlite3 not available, provide manual instructions
        Write-Host "⚠️  sqlite3 command not found in PATH" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Please use one of these methods:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "METHOD 1: Install sqlite3" -ForegroundColor White
        Write-Host "  Download from: https://www.sqlite.org/download.html"
        Write-Host "  Then run this script again"
        Write-Host ""
        Write-Host "METHOD 2: Use DB Browser for SQLite (Recommended)" -ForegroundColor White
        Write-Host "  1. Download from: https://sqlitebrowser.org/"
        Write-Host "  2. Open: $dbPath" -ForegroundColor Yellow
        Write-Host "  3. Go to 'Execute SQL' tab"
        Write-Host "  4. Copy and paste contents of: $sqlFile" -ForegroundColor Yellow
        Write-Host "  5. Click 'Execute'"
        Write-Host "  6. Click 'Write Changes'"
        Write-Host ""
        Write-Host "METHOD 3: Use Python sqlite3 module" -ForegroundColor White
        Write-Host "  Run: python apply_migration.py" -ForegroundColor Yellow
        Write-Host ""
        
        # Create a Python helper script
        $pythonScript = @"
import sqlite3

print("Applying migration using Python...")

# Read SQL file
with open('$sqlFile', 'r') as f:
    sql = f.read()

# Connect and execute
conn = sqlite3.connect('$dbPath')
cursor = conn.cursor()

try:
    # Split by semicolon and execute each statement
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        cursor.execute(stmt)
    
    conn.commit()
    print("✅ Migration applied successfully!")
    
    # Verify tables created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'admin%'")
    tables = cursor.fetchall()
    print(f"✅ Created {len(tables)} admin tables:")
    for table in tables:
        print(f"   - {table[0]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
    
finally:
    conn.close()
"@
        
        # Save Python script
        Set-Content -Path "apply_migration_temp.py" -Value $pythonScript
        Write-Host "Created helper script: apply_migration_temp.py" -ForegroundColor Green
        Write-Host "Run it with: python apply_migration_temp.py" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Error applying migration: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test connection: python test_db_connection.py" -ForegroundColor White
Write-Host "2. Run app: streamlit run streamlit_app.py" -ForegroundColor White
Write-Host "=" -NoNewline; Write-Host ("=" * 59)
