#!/bin/bash
# Script to generate RSA key pair for JWT signing

KEY_DIR="${1:-./keys}"
mkdir -p "$KEY_DIR"

echo "Generating RSA key pair in $KEY_DIR..."

# Generate private key
openssl genrsa -out "$KEY_DIR/private.pem" 2048

# Generate public key
openssl rsa -in "$KEY_DIR/private.pem" -pubout -out "$KEY_DIR/public.pem"

echo "Keys generated successfully:"
echo "  Private: $KEY_DIR/private.pem"
echo "  Public:  $KEY_DIR/public.pem"
echo ""
echo "To use in Docker, add to Dockerfile:"
echo "  COPY keys/ /app/keys/"
