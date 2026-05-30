"""API 测试脚本"""
import urllib.request
import json

BASE = "http://localhost:8001"

def test_get(path):
    resp = urllib.request.urlopen(f"{BASE}{path}")
    return json.loads(resp.read())

def test_post(path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

# 1. 根路径
print("=== GET / ===")
r = test_get("/")
print(f"服务: {r['service']}, Docs: {r['docs']}")

# 2. 统计
print("\n=== GET /api/documents/stats ===")
r = test_get("/api/documents/stats")
print(json.dumps(r, ensure_ascii=False, indent=2))

# 3. 文献列表
print("\n=== GET /api/documents/ ===")
r = test_get("/api/documents/")
print(f"共 {r['total']} 篇文献")
for d in r['documents'][:5]:
    print(f"  - {d['filename']}")

# 4. 混合检索
print("\n=== POST /api/search/ (混合检索: 阿尔茨海默症治疗) ===")
try:
    r = test_post("/api/search/", {"query": "阿尔茨海默症治疗", "mode": "hybrid", "top_k": 5})
    print(f"结果数: {r['total']}")
    for item in r['results'][:3]:
        print(f"  [{item['score']:.4f}] {item['filename']}")
except Exception as e:
    print(f"失败: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8', errors='replace'))

# 5. 语义检索
print("\n=== POST /api/search/ (语义检索: 预防阿尔茨海默症) ===")
try:
    r = test_post("/api/search/", {"query": "预防阿尔茨海默症", "mode": "semantic", "top_k": 3})
    print(f"结果数: {r['total']}")
    for item in r['results']:
        print(f"  [{item['score']:.4f}] {item['filename']}")
except Exception as e:
    print(f"失败: {e}")

# 6. 关键词检索
print("\n=== POST /api/search/ (关键词检索: 中药) ===")
try:
    r = test_post("/api/search/", {"query": "中药", "mode": "keyword", "top_k": 3})
    print(f"结果数: {r['total']}")
    for item in r['results']:
        print(f"  [{item['score']:.4f}] {item['filename']}")
except Exception as e:
    print(f"失败: {e}")

print("\n=== 全部测试完成 ===")
