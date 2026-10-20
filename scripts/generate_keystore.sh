#!/bin/bash
set -e

keytool -genkeypair -v \
  -keystore release.keystore \
  -alias aistudio \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -storepass android \
  -keypass android \
  -dname "CN=AI Studio Simulated Key, OU=Mobile Build, O=FreeBuilder, L=Bangkok, ST=Bangkok, C=TH"

echo "✅ Keystore generated: release.keystore"
echo "   Alias     : aistudio"
echo "   Password  : android"
