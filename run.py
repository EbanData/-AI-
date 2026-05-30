"""启动脚本 — 知识库检索系统

用法：
    cd search
    source venv/Scripts/activate
    python run.py                    # 启动服务
    python run.py --index            # 启动前先索引文献
    python run.py --reindex          # 清空旧索引后重建
"""

import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    args = sys.argv[1:]

    # 加载数据库（从磁盘读取已有索引）
    from app.database import db
    db.load()

    if "--reindex" in args:
        logger.info("===== 执行全量重建索引 =====")
        db.clear()

        from app.document_loader import scan_documents, load_and_chunk
        from app.embedder import embed_texts

        files = scan_documents()
        total = 0
        for file_info in files:
            chunks = load_and_chunk(file_info)
            if not chunks:
                continue
            texts = [c["text"] for c in chunks]
            metadatas = [c["metadata"] for c in chunks]
            ids = [c["id"] for c in chunks]
            embeddings = embed_texts(texts)
            db.add_documents(ids, embeddings, texts, metadatas)
            total += len(chunks)

        from app.retriever import retriever
        retriever._initialized = False
        logger.info(f"===== 重建完成，共索引 {total} 个片段 =====")

    elif "--index" in args:
        logger.info("===== 执行增量索引 =====")
        from app.document_loader import scan_documents, load_and_chunk
        from app.embedder import embed_texts

        files = scan_documents()
        total = 0
        for file_info in files:
            chunks = load_and_chunk(file_info)
            if not chunks:
                continue
            texts = [c["text"] for c in chunks]
            metadatas = [c["metadata"] for c in chunks]
            ids = [c["id"] for c in chunks]
            embeddings = embed_texts(texts)
            db.add_documents(ids, embeddings, texts, metadatas)
            total += len(chunks)

        from app.retriever import retriever
        retriever._initialized = False
        logger.info(f"===== 增量索引完成，新增 {total} 个片段 =====")

    # 启动服务
    logger.info("===== 启动 API 服务 =====")
    from app.main import start
    start()


if __name__ == "__main__":
    main()
