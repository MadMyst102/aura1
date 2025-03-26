import os
import shutil
from cryptography import __file__ as crypto_file

crypto_dir = os.path.dirname(crypto_file)
rust_dir = os.path.join(crypto_dir, 'hazmat', 'bindings')

print(f"Crypto directory: {crypto_dir}")
print(f"Rust bindings directory: {rust_dir}")
for file in os.listdir(rust_dir):
    print(f"Found: {file}")
