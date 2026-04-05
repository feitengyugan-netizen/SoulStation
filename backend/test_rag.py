"""临时测试脚本 - 直接调用 ChromaDB 验证 RAG 检索，不依赖 app 模块"""
import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
COLLECTION_NAME = "psychology_kb"

print("=" * 60)
print("RAG 知识库检索测试")
print("=" * 60)

print("\n正在加载嵌入模型（首次稍慢）...")
ef = SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=ef)

count = collection.count()
print(f"✅ 知识库记录数: {count}")

if count == 0:
    print("❌ 知识库为空，请先运行: python seeds/load_psychology_rag.py")
    exit(1)

test_queries = [
    "我最近感到很焦虑，不知道该怎么办",
    "我睡眠很差，总是睡不着觉",
    "我感觉工作压力很大，很累",
    "我和伴侣关系出现了问题",
]

for query in test_queries:
    print(f"\n{'─' * 50}")
    print(f"用户消息: {query}")
    results = collection.query(query_texts=[query], n_results=3)
    docs = results["documents"][0]
    dists = results["distances"][0]
    metas = results["metadatas"][0]
    print(f"检索到 {len(docs)} 条相关案例:")
    for i, (doc, dist, meta) in enumerate(zip(docs, dists, metas), 1):
        print(f"  [{i}] 距离={round(dist,4)}  相似问题: {doc[:45]}...")
        print(f"       参考回答: {meta.get('output','')[:60]}...")

print("\n" + "=" * 60)
print("✅ RAG 检索功能正常！")
