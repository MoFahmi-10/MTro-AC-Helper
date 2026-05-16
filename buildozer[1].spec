[app]
title = MTro AC Helper
package.name = mtroachelper
package.domain = org.mohammed.mtro
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
entrypoint = main.py
requirements = python3,kivy==2.2.1,kivymd==1.2.0,pillow==9.5.0
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/icon.png
orientation = portrait
android.permissions = INTERNET
android.minapi = 26
android.api = 31
android.ndk = 25b
android.ndk_path = /root/.buildozer/android/platform/android-ndk-r25b
android.sdk_path = /root/.buildozer/android/platform/android-sdk
android.archs = arm64-v8a
android.allow_backup = True
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
