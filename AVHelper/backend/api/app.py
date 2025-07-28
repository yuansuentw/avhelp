"""FastAPI application with GraphQL integration"""

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry

from .resolvers import Query, Mutation
from database import DatabaseManager, DEFAULT_DATABASE_URL


# 創建 GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# 創建 GraphQL router
graphql_app = GraphQLRouter(schema, graphiql=True)

# 創建 FastAPI 應用
app = FastAPI(
    title="AVHelper GraphQL API",
    description="GraphQL API for AVHelper - Adult Video Management System",
    version="1.0.0"
)

# 初始化數據庫
db_manager = DatabaseManager(DEFAULT_DATABASE_URL)
db_manager.create_tables()

# 添加 GraphQL 路由
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "AVHelper GraphQL API",
        "graphql_endpoint": "/graphql",
        "graphiql_interface": "/graphql (GET request)"
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)