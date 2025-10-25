#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from typing import List, Dict, Any

# ==============================================================================
# 补丁配置区域
#
# 在这里定义你所有不同的补丁版本。
# 每个补丁都是一个字典，包含:
#   - "description": (str) 对这个补丁的简短描述，会显示给用户。
#   - "target": (bytes) 要在.so文件中搜索的目标二进制指令串。
#   - "replacement": (bytes) 用于替换目标二进制串的新指令串。
#
# **重要**: 为了保证二进制文件的结构不被破坏，"target" 和 "replacement"
# 的字节长度必须完全相同。
# ==============================================================================
PATCH_CONFIG: List[Dict[str, Any]] = [
    # (2023.03 - 2023.12) patch只需要覆盖b'\x41\x55\x41\x54\x55\x53'，这里为了防止误patch到其他部分，所以保持完整指令流，都包括进来了
    # 这部分的对应的函数是covdb_get_license，通过b'\xb8\x01\x00\x00\x00\xc3'直接给eax寄存器写1并返回，来跳过函数执行部分
    {
        "description": "U-2023.03-SP1",
        "target": b'\x41\x55\x41\x54\x55\x53\x48\x83\xec\x08\x44\x8b\x25\x67\xec\xdf\x00',
        "replacement": b'\xb8\x01\x00\x00\x00\xc3\x48\x83\xec\x08\x44\x8b\x25\x67\xec\xdf\x00',
    },
    {
        "description": "U-2023.03-SP2",
        "target": b'\x41\x55\x41\x54\x55\x53\x48\x83\xec\x08\x44\x8b\x25\x57\x06\xe0\x00',
        "replacement": b'\xb8\x01\x00\x00\x00\xc3\x48\x83\xec\x08\x44\x8b\x25\x57\x06\xe0\x00',
    },
    {
        "description": "U-2023.12-SP1",
        "target": b'\x41\x55\x41\x54\x55\x53\x48\x83\xec\x08\x44\x8b\x25\x47\xd0\xee\x00',
        "replacement": b'\xb8\x01\x00\x00\x00\xc3\x48\x83\xec\x08\x44\x8b\x25\x47\xd0\xee\x00',
    },
    {
        "description": "U-2023.12-SP2",
        "target": b'\x41\x55\x41\x54\x55\x53\x48\x83\xec\x08\x44\x8b\x25\x07\x0c\xef\x00',
        "replacement": b'\xb8\x01\x00\x00\x00\xc3\x48\x83\xec\x08\x44\x8b\x25\x07\x0c\xef\x00',
    },
    # (2024.09 - 2025.06) patch只需要覆盖b'\x55\x48\x89'，这里为了防止误patch到其他部分，所以保持完整指令流，都包括进来了
    # 这部分的对应的函数是执行一个受互斥锁保护的任务，通过b'\x31\xc0\xc3'直接给eax寄存器写0并返回，来跳过函数执行部分
    {
        "description": "W-2024.09",
        "target": b'\x55\x48\x89\xe5\x48\x81\xec\x80\x01\x00\x00',
        "replacement": b'\x31\xc0\xc3\xe5\x48\x81\xec\x80\x01\x00\x00',
    },
    {
        "description": "W-2024.09-SP1",
        "target": b'\x55\x48\x89\xe5\x48\x81\xec\x80\x01\x00\x00',
        "replacement": b'\x31\xc0\xc3\xe5\x48\x81\xec\x80\x01\x00\x00',
    },
    {
        "description": "W-2024.09-SP2",
        "target": b'\x55\x48\x89\xe5\x48\x81\xec\x80\x01\x00\x00',
        "replacement": b'\x31\xc0\xc3\xe5\x48\x81\xec\x80\x01\x00\x00',
    },
    {
        "description": "X-2025.06",
        "target": b'\x55\x48\x89\xe5\x48\x81\xec\x80\x01\x00\x00',
        "replacement": b'\x31\xc0\xc3\xe5\x48\x81\xec\x80\x01\x00\x00',
    },
    {
        "description": "X-2025.06-SP1",
        "target": b'\x55\x48\x89\xe5\x48\x81\xec\x80\x01\x00\x00',
        "replacement": b'\x31\xc0\xc3\xe5\x48\x81\xec\x80\x01\x00\x00',
    },
    # --- 如果有针对其他版本的补丁，可以在这里继续添加 ---
]

def display_patches() -> None:
    """打印所有可用的补丁选项"""
    print("=" * 50)
    print("  Available Patch Versions:")
    print("=" * 50)
    if not PATCH_CONFIG:
        print("  No patches configured. Please edit the script.")
        return

    for i, patch in enumerate(PATCH_CONFIG):
        print(f"  [{i + 1}] {patch['description']}")
    print("-" * 50)


def select_patch() -> Dict[str, Any]:
    """让用户选择一个补丁并返回所选的补丁配置"""
    if len(PATCH_CONFIG) == 1:
        print("Found only one available patch. Auto-selecting it.")
        return PATCH_CONFIG[0]

    while True:
        try:
            choice = input("Please select a patch version to apply (enter number): ")
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(PATCH_CONFIG):
                return PATCH_CONFIG[choice_index]
            else:
                print(f"Error: Invalid selection. Please enter a number between 1 and {len(PATCH_CONFIG)}.", file=sys.stderr)
        except ValueError:
            print("Error: Invalid input. Please enter a number.", file=sys.stderr)
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled by user.", file=sys.stderr)
            sys.exit(1)


def apply_patch(file_path: str, patch_info: Dict[str, Any]) -> bool:
    """
    核心补丁应用函数。
    """
    target_bytes = patch_info['target']
    replacement_bytes = patch_info['replacement']
    version_string = patch_info['description']

    if len(target_bytes) != len(replacement_bytes):
        print("=" * 60, file=sys.stderr)
        print("CRITICAL ERROR: The length of 'target' and 'replacement' bytes must be identical!", file=sys.stderr)
        print(f"  Target length: {len(target_bytes)} bytes", file=sys.stderr)
        print(f"  Replacement length: {len(replacement_bytes)} bytes", file=sys.stderr)
        print("Aborting to prevent file corruption.", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        return False

    print(f"\n[*] Applying patch for version: '{version_string}'")
    print(f"[*] Target file: {file_path}")

    try:
        with open(file_path, 'rb') as f:
            original_data = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'", file=sys.stderr)
        return False
    except IOError as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        return False

    # =================== 新增功能：版本号校验 ===================
    # 将版本描述字符串编码为字节，然后在二进制文件中查找
    version_bytes = version_string.encode('ascii')
    # print(version_bytes)
    if version_bytes not in original_data:
        print(f"\n[!] ERROR: Version mismatch or incorrect file selected.")
        print(f"[!] The version string '{version_string}' was NOT found inside the file '{file_path}'.")
        print(f"[!] Please ensure you are patching the correct file and have selected the right version.")
        return False
    else:
        print(f"[*] Version check passed. Found '{version_string}' in the file.")
    # =====================================================================

    # 检查是否已被Patch
    if replacement_bytes in original_data:
        print("\n[*] Info: The replacement byte sequence already exists in the file.")
        print("[*] The file appears to be already patched. No action needed.")
        return True

    occurrence_count = original_data.count(target_bytes)
    if occurrence_count == 0:
        print("\n[!] Patch failed: Target instruction sequence not found in the file.")
        print("[!] The file seems to be the correct version, but the specific byte sequence to be patched was not found.")
        return False

    print(f"[*] Found {occurrence_count} occurrence(s) of the target sequence.")
    if occurrence_count > 1:
        print("[!] Warning: Multiple occurrences found. Aborting to prevent potential mis-patching.")
        print("[!] Please manually verify the target offsets with a tool like 'objdump'.")
        return False

    patched_data = original_data.replace(target_bytes, replacement_bytes, 1)

    if patched_data == original_data:
        print("\n[!] Patch failed: Data remained unchanged after replacement attempt.", file=sys.stderr)
        return False

    output_path = file_path + ".patched"
    try:
        with open(output_path, 'wb') as f:
            f.write(patched_data)
        print(f"\n[+] Success! Patched file saved to: {output_path}")
        return True
    except IOError as e:
        print(f"Error writing to output file '{output_path}': {e}", file=sys.stderr)
        return False


def main():
    """主函数，负责解析参数和协调流程"""
    parser = argparse.ArgumentParser(
        description="A script to patch binary files like .so based on predefined versions.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("so_file", help="The path to the .so file to be patched.")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    display_patches()
    selected_patch = select_patch()

    if apply_patch(args.so_file, selected_patch):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
