#!/bin/bash

# Database setup script for Quiz Platform
# This script attempts to create the database and user if they don't exist

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Setting up PostgreSQL Database ==="
echo ""

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ Error: PostgreSQL is not running on localhost:5432"
    echo "   Please start PostgreSQL first:"
    echo "   sudo systemctl start postgresql"
    exit 1
fi

echo "✓ PostgreSQL is running"
echo ""

# Try to connect and create database/user
echo "Attempting to create database and user..."
echo ""

# Method 1: Try with sudo (if passwordless sudo is configured)
if sudo -n true 2>/dev/null; then
    echo "Using sudo to create database setup..."
    sudo -u postgres psql <<EOF
-- Create user if it doesn't exist
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'quizuser') THEN
      CREATE USER quizuser WITH PASSWORD 'quizpass';
   END IF;
END
\$\$;

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE quizdb OWNER quizuser'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'quizdb')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE quizdb TO quizuser;
ALTER DATABASE quizdb OWNER TO quizuser;
EOF

    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Database 'quizdb' and user 'quizuser' created successfully!"
        exit 0
    fi
fi

# Method 2: Provide manual instructions
echo ""
echo "⚠️  Automatic setup requires sudo access."
echo ""
echo "Please run the following commands manually:"
echo ""
echo "  sudo -u postgres psql <<'SQL'"
echo "  CREATE USER quizuser WITH PASSWORD 'quizpass';"
echo "  CREATE DATABASE quizdb OWNER quizuser;"
echo "  GRANT ALL PRIVILEGES ON DATABASE quizdb TO quizuser;"
echo "  \\q"
echo "  SQL"
echo ""
echo "Or run this single command:"
echo ""
echo "  sudo -u postgres psql -c \"CREATE USER quizuser WITH PASSWORD 'quizpass';\""
echo "  sudo -u postgres psql -c \"CREATE DATABASE quizdb OWNER quizuser;\""
echo "  sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE quizdb TO quizuser;\""
echo ""
echo "After running these commands, you can start the application with: ./start.sh"
echo ""

