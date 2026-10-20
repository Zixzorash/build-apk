#!/usr/bin/env python3
import argparse
import os
import re
from pathlib import Path

def find_app_build_files(project_root: str, project_type: str):
    root = Path(project_root)
    candidates = []

    if project_type == "flutter":
        candidates += list(root.glob("android/app/build.gradle*"))
    elif project_type == "react-native":
        candidates += list(root.glob("android/app/build.gradle*"))
    else:
        candidates += list(root.glob("app/build.gradle*"))
        candidates += list(root.glob("**/app/build.gradle*"))

    seen = set()
    result = []
    for c in candidates:
        if c.resolve() not in seen and c.exists():
            seen.add(c.resolve())
            result.append(c)
    return result

def inject_groovy(content: str, keystore: str, store_pass: str, alias: str, key_pass: str) -> str:
    signing_block = f'''
    signingConfigs {{
        release {{
            storeFile file("{keystore}")
            storePassword "{store_pass}"
            keyAlias "{alias}"
            keyPassword "{key_pass}"
        }}
    }}
'''
    if "signingConfigs" in content:
        content = re.sub(
            r'signingConfigs\s*\{[^}]*release\s*\{[^}]*\}[^}]*\}',
            signing_block.strip(),
            content,
            flags=re.DOTALL
        )
    else:
        content = re.sub(
            r'(android\s*\{)',
            r'\1\n' + signing_block,
            content,
            count=1
        )

    content = re.sub(
        r'(release\s*\{[^}]*)(minifyEnabled|proguardFiles|debuggable)',
        r'\1signingConfig signingConfigs.release\n            \2',
        content,
        count=1,
        flags=re.DOTALL
    )
    content = re.sub(
        r'(release\s*\{\s*)(\})',
        r'\1signingConfig signingConfigs.release\n        \2',
        content,
        count=1
    )
    return content

def inject_kts(content: str, keystore: str, store_pass: str, alias: str, key_pass: str) -> str:
    signing_block = f'''
    signingConfigs {{
        create("release") {{
            storeFile = file("{keystore}")
            storePassword = "{store_pass}"
            keyAlias = "{alias}"
            keyPassword = "{key_pass}"
        }}
    }}
'''
    if "signingConfigs" in content:
        content = re.sub(
            r'signingConfigs\s*\{.*?create\("release"\).*?\}.*?\}',
            signing_block.strip(),
            content,
            flags=re.DOTALL
        )
    else:
        content = re.sub(
            r'(android\s*\{)',
            r'\1\n' + signing_block,
            content,
            count=1
        )

    content = re.sub(
        r'(getByName\("release"\)\s*\{[^}]*)(isMinifyEnabled|proguardFiles)',
        r'\1signingConfig = signingConfigs.getByName("release")\n            \2',
        content,
        count=1,
        flags=re.DOTALL
    )
    content = re.sub(
        r'(getByName\("release"\)\s*\{\s*)(\})',
        r'\1signingConfig = signingConfigs.getByName("release")\n        \2',
        content,
        count=1
    )
    return content

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--project-type", required=True)
    parser.add_argument("--keystore", required=True)
    parser.add_argument("--store-password", required=True)
    parser.add_argument("--key-alias", required=True)
    parser.add_argument("--key-password", required=True)
    parser.add_argument("--package-override", default="")
    args = parser.parse_args()

    files = find_app_build_files(args.project_root, args.project_type)
    if not files:
        print("⚠️ ไม่พบไฟล์ build.gradle / build.gradle.kts ของ app module")
        return

    abs_keystore = os.path.abspath(args.keystore)

    for f in files:
        print(f"Injecting into → {f}")
        content = f.read_text(encoding="utf-8")

        if f.suffix == ".kts":
            new_content = inject_kts(content, abs_keystore, args.store_password, args.key_alias, args.key_password)
        else:
            new_content = inject_groovy(content, abs_keystore, args.store_password, args.key_alias, args.key_password)

        if args.package_override:
            new_content = re.sub(
                r'applicationId\s+["\'][^"\']+["\']',
                f'applicationId "{args.package_override}"',
                new_content
            )
            new_content = re.sub(
                r'applicationId\s*=\s*["\'][^"\']+["\']',
                f'applicationId = "{args.package_override}"',
                new_content
            )

        f.write_text(new_content, encoding="utf-8")
        print(f"✅ Injected signing into {f}")

if __name__ == "__main__":
    main()
