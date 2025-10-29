#!/bin/bash

# Test complet du workflow : Register → Login → Create DB → Activate → Create Person → Verify

API_URL="http://localhost:8000"
USERNAME="testuser_$(date +%s)"
PASSWORD="TestPass123!"
EMAIL="${USERNAME}@test.com"

echo "=========================================="
echo "Test du workflow complet"
echo "=========================================="
echo ""

# 1. REGISTER
echo "1️⃣  REGISTER - Création d'un nouvel utilisateur..."
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"${USERNAME}\",
    \"password\": \"${PASSWORD}\",
    \"email\": \"${EMAIL}\",
    \"full_name\": \"Test User\"
  }")

echo "Response: $REGISTER_RESPONSE"
echo ""

# Vérifier si le register a réussi
if echo "$REGISTER_RESPONSE" | grep -q '"id"'; then
    echo "✅ Register réussi!"
else
    echo "❌ Register échoué!"
    exit 1
fi
echo ""

# 2. LOGIN
echo "2️⃣  LOGIN - Connexion avec les identifiants..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"${USERNAME}\",
    \"password\": \"${PASSWORD}\"
  }")

echo "Response: $LOGIN_RESPONSE"
echo ""

# Extraire le token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Login échoué - pas de token!"
    exit 1
fi

echo "✅ Login réussi! Token: ${ACCESS_TOKEN:0:50}..."
echo ""

# 3. CREATE DATABASE
echo "3️⃣  CREATE DATABASE - Création d'une nouvelle base de données..."
DB_NAME="test_db_$(date +%s)"
CREATE_DB_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/database/databases" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d "{
    \"name\": \"${DB_NAME}\",
    \"set_active\": false
  }")

echo "Response: $CREATE_DB_RESPONSE"
echo ""

if echo "$CREATE_DB_RESPONSE" | grep -q "success"; then
    echo "✅ Database créée: ${DB_NAME}"
else
    echo "❌ Création de database échouée!"
    exit 1
fi
echo ""

# 4. ACTIVATE DATABASE
echo "4️⃣  ACTIVATE DATABASE - Activation de la base de données..."
ACTIVATE_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/database/databases/${DB_NAME}/activate" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "Response: $ACTIVATE_RESPONSE"
echo ""

if echo "$ACTIVATE_RESPONSE" | grep -q "success"; then
    echo "✅ Database activée: ${DB_NAME}"
else
    echo "❌ Activation de database échouée!"
    exit 1
fi
echo ""

# 5. CREATE PERSON
echo "5️⃣  CREATE PERSON - Création d'une personne..."
CREATE_PERSON_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/persons/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "first_name": "Jean",
    "last_name": "Dupont",
    "sex": "male",
    "birth_date": "1980-05-15",
    "birth_place": "Paris, France"
  }')

echo "Response: $CREATE_PERSON_RESPONSE"
echo ""

# Extraire l'ID de la personne
PERSON_ID=$(echo "$CREATE_PERSON_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -z "$PERSON_ID" ]; then
    echo "❌ Création de personne échouée!"
    exit 1
fi

echo "✅ Personne créée! ID: ${PERSON_ID}"
echo ""

# 6. GET PERSON - Vérifier que la personne existe
echo "6️⃣  GET PERSON - Vérification que la personne existe..."
GET_PERSON_RESPONSE=$(curl -s -X GET "${API_URL}/api/v1/persons/${PERSON_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "Response: $GET_PERSON_RESPONSE"
echo ""

if echo "$GET_PERSON_RESPONSE" | grep -q "Jean" && echo "$GET_PERSON_RESPONSE" | grep -q "Dupont"; then
    echo "✅ Personne trouvée et vérifiée!"
else
    echo "❌ Personne non trouvée!"
    exit 1
fi
echo ""

# 7. LIST PERSONS - Lister toutes les personnes
echo "7️⃣  LIST PERSONS - Liste de toutes les personnes..."
LIST_PERSONS_RESPONSE=$(curl -s -X GET "${API_URL}/api/v1/persons/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "Response: $LIST_PERSONS_RESPONSE"
echo ""

if echo "$LIST_PERSONS_RESPONSE" | grep -q "Jean"; then
    echo "✅ Liste des personnes OK!"
else
    echo "⚠️  Personne non trouvée dans la liste"
fi
echo ""

# 8. Vérifier dans la base de données directement
echo "8️⃣  VERIFY IN DATABASE - Vérification dans la base de données GeneWeb..."
echo "Database path devrait être: src/data/${DB_NAME}.gwb"

if [ -d "src/data/${DB_NAME}.gwb" ]; then
    echo "✅ Dossier de base de données existe!"
    ls -la "src/data/${DB_NAME}.gwb/"
else
    echo "⚠️  Dossier de base de données non trouvé"
fi
echo ""

echo "=========================================="
echo "✅ WORKFLOW COMPLET RÉUSSI!"
echo "=========================================="
echo ""
echo "Résumé:"
echo "- Utilisateur: ${USERNAME}"
echo "- Database: ${DB_NAME}"
echo "- Personne: Jean Dupont (${PERSON_ID})"
echo ""
