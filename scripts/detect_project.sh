#!/bin/bash
set -e

ROOT="$1"

if [ -f "$ROOT/pubspec.yaml" ]; then
  echo "flutter"
elif [ -f "$ROOT/package.json" ] && [ -d "$ROOT/android" ]; then
  echo "react-native"
elif [ -f "$ROOT/settings.gradle" ] || [ -f "$ROOT/settings.gradle.kts" ] || \
     [ -f "$ROOT/build.gradle" ] || [ -f "$ROOT/build.gradle.kts" ]; then
  echo "native"
else
  if find "$ROOT" -name "pubspec.yaml" | grep -q .; then
    echo "flutter"
  elif find "$ROOT" -name "package.json" | head -1 | xargs dirname | xargs -I{} test -d {}/android && echo "react-native"; then
    echo "react-native"
  else
    echo "native"
  fi
fi
