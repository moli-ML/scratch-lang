#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ScratchLang 急救编译器
当IDE未响应时使用此工具直接编译.sl文件
"""
import os
import sys

def main():
    print("=" * 50)
    print("ScratchLang 急救编译器")
    print("=" * 50)
    print()

    # 输入.sl文件路径
    while True:
        sl_file = input("请输入.sl文件路径: ").strip().strip('"')
        if not sl_file:
            print("❌ 文件路径不能为空")
            continue
        if not os.path.exists(sl_file):
            print(f"❌ 文件不存在: {sl_file}")
            continue
        if not sl_file.endswith('.sl'):
            print("❌ 文件必须是.sl格式")
            continue
        break

    # 输入.sb3输出路径
    sb3_file = input("请输入.sb3输出路径 (留空则自动生成): ").strip().strip('"')
    if not sb3_file:
        sb3_file = sl_file.rsplit('.', 1)[0] + '.sb3'
        print(f"→ 输出文件: {sb3_file}")

    print()
    print("开始编译...")
    print("-" * 50)

    try:
        from compiler.parser import ScratchLangParser

        parser = ScratchLangParser()
        parser.parse_file(sl_file)
        parser.compile(sb3_file)

        print("-" * 50)
        print(f"✅ 编译成功!")
        print(f"输出文件: {sb3_file}")

    except Exception as e:
        print("-" * 50)
        print(f"❌ 编译失败: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)

    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
