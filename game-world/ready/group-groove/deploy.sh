#!/bin/bash

# 🎵 GROUP GROOVE DEPLOYMENT SCRIPT
# Run this to deploy the entire platform

set -e

echo "🎵 GROUP GROOVE DEPLOYMENT"
echo "=========================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for required tools
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 is required but not installed.${NC}"
        exit 1
    fi
}

echo "📋 Checking requirements..."
check_tool "node"
check_tool "npm"
echo -e "${GREEN}✅ Node.js and npm found${NC}"

# Install wrangler if not present
if ! command -v wrangler &> /dev/null; then
    echo "📦 Installing Wrangler CLI..."
    npm install -g wrangler
fi
echo -e "${GREEN}✅ Wrangler CLI ready${NC}"

# Get API URL from user
echo ""
echo -e "${YELLOW}📝 Configuration${NC}"
read -p "Enter your Cloudflare account subdomain (e.g., 'john123'): " SUBDOMAIN
API_URL="https://group-groove-api.${SUBDOMAIN}.workers.dev"

echo ""
echo "Your API will be at: $API_URL"
echo ""

# Step 1: Deploy Backend
echo "🚀 Step 1: Deploying Backend..."
cd backend

# Check if logged in
if ! wrangler whoami &> /dev/null; then
    echo "Please login to Cloudflare..."
    wrangler login
fi

# Create D1 database if needed
echo "Creating D1 database..."
DB_OUTPUT=$(wrangler d1 create group-groove-db 2>&1 || true)

if echo "$DB_OUTPUT" | grep -q "already exists"; then
    echo "Database already exists"
else
    DB_ID=$(echo "$DB_OUTPUT" | grep "database_id" | cut -d'"' -f2)
    if [ ! -z "$DB_ID" ]; then
        # Update wrangler.toml with database ID
        sed -i.bak "s/YOUR_DATABASE_ID_HERE/$DB_ID/" wrangler.toml
        echo "Database created with ID: $DB_ID"
    fi
fi

# Deploy worker
echo "Deploying worker..."
wrangler deploy

# Run migrations
echo "Running database migrations..."
curl -X POST "$API_URL/api/migrate" 2>/dev/null || true

echo -e "${GREEN}✅ Backend deployed!${NC}"
cd ..

# Step 2: Update Web App
echo ""
echo "🌐 Step 2: Configuring Web App..."
cd web
sed -i.bak "s|__API_URL__|$API_URL|g" index.html
echo -e "${GREEN}✅ Web app configured!${NC}"

echo ""
echo "To deploy web app to Cloudflare Pages:"
echo "  cd web && npx wrangler pages deploy . --project-name=group-groove"
cd ..

# Step 3: Update Mobile App
echo ""
echo "📱 Step 3: Configuring Mobile App..."
cd mobile
sed -i.bak "s|__API_URL__|$API_URL|g" App.js
echo -e "${GREEN}✅ Mobile app configured!${NC}"

echo ""
echo "To run mobile app:"
echo "  cd mobile && npm install && npx expo start"
cd ..

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "📍 Your endpoints:"
echo "   API:  $API_URL"
echo "   Health: $API_URL/api/health"
echo ""
echo "📝 Next steps:"
echo "   1. Set Spotify credentials:"
echo "      cd backend"
echo "      wrangler secret put SPOTIFY_CLIENT_ID"
echo "      wrangler secret put SPOTIFY_CLIENT_SECRET"
echo ""
echo "   2. Deploy web app:"
echo "      cd web"
echo "      npx wrangler pages deploy . --project-name=group-groove"
echo ""
echo "   3. Run mobile app:"
echo "      cd mobile"
echo "      npm install"
echo "      npx expo start"
echo ""
echo "🎵 Making Music Great Again!"
