#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试AI服务API
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("测试健康检查 API...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_summarize():
    """测试案件总结API"""
    print("=" * 60)
    print("测试案件总结 API...")
    try:
        data = {
            "file_names": ["合同.pdf", "证据1.docx"],
            "identity": "plaintiff"
        }
        response = requests.post(
            f"{BASE_URL}/api/case/summarize",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"成功: {result.get('success')}")
            if result.get('summary'):
                print(f"总结长度: {len(result['summary'])} 字符")
                print(f"总结预览: {result['summary'][:200]}...")
            return True
        else:
            print(f"响应内容: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    print("开始测试AI服务API...")
    print()
    
    health_ok = test_health()
    print()
    
    if health_ok:
        summarize_ok = test_summarize()
        print()
        
        if summarize_ok:
            print("=" * 60)
            print("✅ 所有测试通过！")
        else:
            print("=" * 60)
            print("❌ 案件总结API测试失败")
    else:
        print("=" * 60)
        print("❌ 健康检查失败，服务可能未运行或有问题")
        print("请检查：")
        print("1. Python Flask服务是否在运行（python ai_service/app.py）")
        print("2. 服务是否运行在5000端口")
        print("3. 检查服务日志是否有错误")

