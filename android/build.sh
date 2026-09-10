#!/bin/bash
set -e
export ANDROID_HOME="$HOME/Library/Android/sdk"
export JAVA_HOME="/usr/local/opt/openjdk"
BT="$ANDROID_HOME/build-tools/34.0.0"
JAR="$ANDROID_HOME/platforms/android-34/android.jar"
PATH="$JAVA_HOME/bin:$PATH"
cd "$(dirname "$0")"
rm -rf build && mkdir -p build/compiled build/gen build/classes build/dex

# 1. compile + link resources, emit R.java and a base APK (resources+manifest)
"$BT/aapt2" compile --dir res -o build/compiled/res.zip
"$BT/aapt2" link -o build/base.apk -I "$JAR" \
  --manifest AndroidManifest.xml \
  --java build/gen \
  --min-sdk-version 24 --target-sdk-version 34 \
  -A assets \
  build/compiled/res.zip

# 2. compile Java (app sources + generated R.java) against android.jar
find src build/gen -name '*.java' > build/srcs.txt
javac -source 17 -target 17 -classpath "$JAR" -d build/classes @build/srcs.txt

# 3. dex
"$BT/d8" --min-api 24 --lib "$JAR" --output build/dex \
  $(find build/classes -name '*.class')

# 4. add classes.dex into the base apk
cp build/base.apk build/app-unsigned.apk
(cd build/dex && zip -q ../app-unsigned.apk classes.dex)

# 5. align + sign with a debug keystore
KS="$HOME/.android/debug.keystore"
if [ ! -f "$KS" ]; then
  keytool -genkeypair -keystore "$KS" -storepass android -keypass android \
    -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10000 \
    -dname "CN=Android Debug,O=Android,C=US" >/dev/null 2>&1
fi
"$BT/zipalign" -f -p 4 build/app-unsigned.apk build/app-aligned.apk
"$BT/apksigner" sign --ks "$KS" --ks-pass pass:android --key-pass pass:android \
  --ks-key-alias androiddebugkey --out build/burmakey.apk build/app-aligned.apk
echo "BUILT: $(ls -la build/burmakey.apk | awk '{print $5}') bytes"
