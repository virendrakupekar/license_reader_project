[app]

# ✅ App basic info
title = LicensePlateReader
package.name = license_reader
package.domain = org.kivy
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt
version = 1.0
entrypoint = main.py

# ✅ Python dependencies
requirements = python3,kivy,numpy,opencv,pillow,easyocr


# Optional if using .kv file
# kv_files = ui.kv

# ✅ Kivy and display options
osx.kivy_version = 2.3.0
orientation = portrait
fullscreen = 1

# ✅ Permissions
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# ✅ Supported Android architectures
arch = armeabi-v7a,arm64-v8a

# ✅ Android SDK/NDK
android.api = 33
android.minapi = 24
android.ndk_api = 24
android.ndk = 25b

# ✅ Reduce APK size: prevent PyTorch weights & modules from being bundled
android.blacklist_patterns = *.pt,*.pth,torch/**,torchvision/**,torchaudio/**

# ✅ Build behavior
copy_libs = 1
android.allow_backup = True
log_level = 2
android.logcat_filters = *:S python:D
android.extra_args = --ignore-setup-py

# Optional: custom Java/Kotlin deps (not needed here)
# android.gradle_dependencies = org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.6.10

# Optional: custom recipe path
# p4a.local_recipes = ./recipes

# Optional: if using Numpy optimizations
# android.extra_packages = blas,lapack

