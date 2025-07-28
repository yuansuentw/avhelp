#!/usr/bin/env python3
"""啟動 AVHelper GraphQL API 服務器"""

import uvicorn

if __name__ == "__main__":
    print("🚀 啟動 AVHelper GraphQL API...")
    print("📍 GraphQL Endpoint: http://localhost:8001/graphql")
    print("🔍 GraphiQL Interface: http://localhost:8001/graphql")
    print("❤️  Health Check: http://localhost:8001/health")
    print("\n按 Ctrl+C 停止服務器")
    
    uvicorn.run(
        "backend.api.app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,  # 開發模式下自動重載
        log_level="info"
    )