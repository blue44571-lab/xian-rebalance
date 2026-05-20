"""執行此腳本產生 Dashboard 密碼的 SHA-256 雜湊值。"""
import hashlib
import sys

def main():
    if len(sys.argv) > 1:
        pwd = sys.argv[1]
    else:
        pwd = input("請輸入你想設定的 Dashboard 密碼：")
    h = hashlib.sha256(pwd.encode()).hexdigest()
    print(f"\n✅ SHA-256 雜湊值：\n{h}")
    print("\n請將這段雜湊值貼到：")
    print("  1. docs/index.html → 第 134 行 PASSWORD_HASH = \"...\"")
    print("  2. config/settings.yaml → dashboard.password_hash")

if __name__ == "__main__":
    main()
