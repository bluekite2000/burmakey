#!/usr/bin/env bash
# Host-JVM unit test for the on-device learning engine (no emulator needed).
# Proves: candidate promotion by recency, save/load persistence, learnRaw.
set -e
cd "$(dirname "$0")/.."
export JAVA_HOME="${JAVA_HOME:-/usr/local/opt/openjdk}"
export PATH="$JAVA_HOME/bin:$PATH"
OUT="build/test"
mkdir -p "$OUT"
javac -d "$OUT" src/com/burmakey/ime/Engine.java test/EngineTest.java
java -cp "$OUT" EngineTest
