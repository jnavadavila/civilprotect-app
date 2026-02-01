#!/bin/bash

# ==================================================================================
# CIVILPROTECT DEPLOYMENT HELPER SCRIPT
# ==================================================================================
# 
# Este script facilita el deployment de CivilProtect con HTTPS
#
# Uso: sudo bash deploy-https.sh
#
# ==================================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Este script debe ejecutarse como root (sudo)"
    exit 1
fi

print_header "CIVILPROTECT DEPLOYMENT SCRIPT V4.5"

# ==================== STEP 1: SYSTEM UPDATE ====================
print_header "PASO 1: Actualizando Sistema"

if command -v apt &> /dev/null; then
    apt update && apt upgrade -y
    print_success "Sistema actualizado (apt)"
elif command -v yum &> /dev/null; then
    yum update -y
    print_success "Sistema actualizado (yum)"
else
    print_error "Package manager no soportado"
    exit 1
fi

# ==================== STEP 2: INSTALL DEPENDENCIES ====================
print_header "PASO 2: Instalando Dependencias"

# Detect OS
if command -v apt &> /dev/null; then
    # Ubuntu/Debian
    apt install -y nginx python3 python3-pip python3-venv certbot python3-certbot-nginx git curl
    print_success "Dependencias instaladas (Debian/Ubuntu)"
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    yum install -y nginx python3 python3-pip certbot python3-certbot-nginx git curl
    print_success "Dependencias instaladas (CentOS/RHEL)"
fi

# ==================== STEP 3: CONFIGURE FIREWALL ====================
print_header "PASO 3: Configurando Firewall"

if command -v ufw &> /dev/null; then
    # UFW (Ubuntu)
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow ssh
    ufw --force enable
    print_success "Firewall configurado (UFW)"
elif command -v firewall-cmd &> /dev/null; then
    # firewalld (CentOS)
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --reload
    print_success "Firewall configurado (firewalld)"
else
    print_warning "Firewall no detectado - configura manualmente"
fi

# ==================== STEP 4: DOMAIN CONFIGURATION ====================
print_header "PASO 4: Configuración de Dominio"

read -p "Ingresa tu dominio (ej: api.civilprotect.com): " DOMAIN

if [ -z "$DOMAIN" ]; then
    print_error "Dominio no puede estar vacío"
    exit 1
fi

print_info "Verificando DNS para $DOMAIN..."

# Check if domain resolves
if host "$DOMAIN" > /dev/null 2>&1; then
    IP=$(host "$DOMAIN" | grep "has address" | awk '{print $4}' | head -n1)
    SERVER_IP=$(curl -s ifconfig.me)
    
    if [ "$IP" == "$SERVER_IP" ]; then
        print_success "DNS configurado correctamente ($IP)"
    else
        print_warning "DNS apunta a $IP pero el servidor es $SERVER_IP"
        print_warning "Asegúrate de que el DNS esté configurado correctamente"
        read -p "¿Continuar de todos modos? (y/n): " CONTINUE
        if [ "$CONTINUE" != "y" ]; then
            exit 1
        fi
    fi
else
    print_error "Dominio no resuelve. Configura el DNS primero."
    exit 1
fi

# ==================== STEP 5: SSL CERTIFICATES ====================
print_header "PASO 5: Obteniendo Certificados SSL"

read -p "Ingresa tu email para notificaciones de Let's Encrypt: " EMAIL

if [ -z "$EMAIL" ]; then
    print_error "Email no puede estar vacío"
    exit 1
fi

print_info "Obteniendo certificado SSL para $DOMAIN..."

# Stop nginx temporarily
systemctl stop nginx || true

# Get certificate
certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos --email "$EMAIL"

if [ $? -eq 0 ]; then
    print_success "Certificado SSL obtenido exitosamente"
else
    print_error "Error obteniendo certificado SSL"
    exit 1
fi

# ==================== STEP 6: NGINX CONFIGURATION ====================
print_header "PASO 6: Configurando Nginx"

# Backup existing config if it exists
if [ -f /etc/nginx/sites-available/civilprotect ]; then
    cp /etc/nginx/sites-available/civilprotect /etc/nginx/sites-available/civilprotect.backup.$(date +%s)
    print_info "Backup de configuración existente creado"
fi

# Copy and modify nginx config
if [ ! -f nginx.conf ]; then
    print_error "nginx.conf no encontrado. Asegúrate de estar en el directorio del proyecto."
    exit 1
fi

cp nginx.conf /etc/nginx/sites-available/civilprotect

# Replace domain in config
sed -i "s/api.civilprotect.com/$DOMAIN/g" /etc/nginx/sites-available/civilprotect

# Create symlink
ln -sf /etc/nginx/sites-available/civilprotect /etc/nginx/sites-enabled/

# Remove default config
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t

if [ $? -eq 0 ]; then
    print_success "Configuración de nginx válida"
    systemctl start nginx
    systemctl enable nginx
    print_success "Nginx iniciado y habilitado"
else
    print_error "Error en configuración de nginx"
    exit 1
fi

# ==================== STEP 7: DEPLOY BACKEND ====================
print_header "PASO 7: Desplegando Backend"

# Create civilprotect user if doesn't exist
if ! id "civilprotect" &>/dev/null; then
    useradd -m -s /bin/bash civilprotect
    print_success "Usuario civilprotect creado"
fi

# Get current directory
PROJECT_DIR=$(pwd)

print_info "Directorio del proyecto: $PROJECT_DIR"

# Install Python dependencies
cd "$PROJECT_DIR/backend"

# Create venv if doesn't exist
if [ ! -d "venv" ]; then
    sudo -u civilprotect python3 -m venv venv
    print_success "Virtual environment creado"
fi

# Activate and install
sudo -u civilprotect bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

if [ $? -eq 0 ]; then
    print_success "Dependencias de Python instaladas"
else
    print_error "Error instalando dependencias"
    exit 1
fi

# Check .env
if [ ! -f .env ]; then
    print_warning ".env no encontrado"
    if [ -f .env.example ]; then
        cp .env.example .env
        print_info ".env creado desde .env.example"
        print_warning "IMPORTANTE: Edita /backend/.env con tus valores reales"
    else
        print_error ".env.example no encontrado"
        exit 1
    fi
fi

# ==================== STEP 8: SYSTEMD SERVICE ====================
print_header "PASO 8: Configurando Servicio Systemd"

cat > /etc/systemd/system/civilprotect.service << EOL
[Unit]
Description=CivilProtect API
After=network.target

[Service]
Type=notify
User=civilprotect
Group=civilprotect
WorkingDirectory=$PROJECT_DIR/backend
Environment="PATH=$PROJECT_DIR/backend/venv/bin"
ExecStart=$PROJECT_DIR/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4

Restart=always
RestartSec=10

NoNewPrivileges=true
PrivateTmp=true

StandardOutput=append:/var/log/civilprotect/app.log
StandardError=append:/var/log/civilprotect/error.log

[Install]
WantedBy=multi-user.target
EOL

# Create log directory
mkdir -p /var/log/civilprotect
chown civilprotect:civilprotect /var/log/civilprotect

# Reload systemd
systemctl daemon-reload
systemctl enable civilprotect

print_success "Servicio systemd configurado"

# ==================== STEP 9: SET PERMISSIONS ====================
print_header "PASO 9: Configurando Permisos"

# Change ownership
chown -R civilprotect:civilprotect "$PROJECT_DIR"

print_success "Permisos configurados"

# ==================== STEP 10: START SERVICES ====================
print_header "PASO 10: Iniciando Servicios"

systemctl start civilprotect

if [ $? -eq 0 ]; then
    print_success "Backend iniciado"
else
    print_error "Error iniciando backend"
    journalctl -u civilprotect -n 20 --no-pager
    exit 1
fi

sleep 2

# Test backend
if curl -s http://localhost:8000 > /dev/null; then
    print_success "Backend respondiendo en localhost:8000"
else
    print_error "Backend no responde"
    exit 1
fi

# ==================== STEP 11: FINAL VERIFICATION ====================
print_header "PASO 11: Verificación Final"

# Test HTTPS
print_info "Testeando HTTPS..."
if curl -s -k "https://$DOMAIN" > /dev/null; then
    print_success "HTTPS funcionando"
else
    print_warning "HTTPS no responde aún (puede tomar unos segundos)"
fi

# ==================== SUCCESS ====================
print_header "🎉 DEPLOYMENT COMPLETADO"

echo -e "${GREEN}"
echo "✅ Nginx configurado y corriendo"
echo "✅ Certificados SSL instalados"
echo "✅ Backend desplegado"
echo "✅ Servicio systemd configurado"
echo -e "${NC}"

echo -e "\n${BLUE}PRÓXIMOS PASOS:${NC}"
echo "1. Edita /backend/.env con tus valores reales"
echo "2. Verifica: https://$DOMAIN"
echo "3. Revisa logs: journalctl -u civilprotect -f"
echo "4. Test SSL: https://www.ssllabs.com/ssltest/"
echo "5. Test Headers: https://securityheaders.com/"

echo -e "\n${BLUE}COMANDOS ÚTILES:${NC}"
echo "- Reiniciar backend: systemctl restart civilprotect"
echo "- Ver logs backend: journalctl -u civilprotect -f"
echo "- Ver logs nginx: tail -f /var/log/nginx/civilprotect_error.log"
echo "- Test nginx: nginx -t"
echo "- Renovar SSL: certbot renew"

print_success "Deployment completado exitosamente!"
