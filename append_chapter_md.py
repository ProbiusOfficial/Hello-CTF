import os

def append_md_files(src_dir, dest_path):
    if not os.path.isdir(src_dir):
        raise FileNotFoundError(f"Source directory not found: {src_dir}")
    files = [f for f in os.listdir(src_dir) if f.lower().endswith('.md')]
    files.sort()
    if not files:
        print("No markdown files found.")
        return
    with open(dest_path, 'a', encoding='utf-8') as dest:
        for name in files:
            src_file = os.path.join(src_dir, name)
            try:
                with open(src_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(src_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            dest.write("\n\n")
            dest.write(f"<!-- Imported from {src_file} -->\n")
            dest.write(content)
            dest.write("\n")
            print(f"Appended: {src_file}")

if __name__ == "__main__":
    src_dir = r"D:\\Book\\Crypto\\Chapter99"
    dest_path = os.path.join(os.getcwd(), "docs", "hc-crypto", "Moderncipher.md")
    append_md_files(src_dir, dest_path)
