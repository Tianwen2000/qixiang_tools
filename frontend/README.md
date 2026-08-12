# frontend

Vue 3 + Vite 前端目录，当前已经实现：

- 首页工具列表
- 分类筛选
- 前端本地搜索
- 工具详情页
- 文本类工具执行
- 文件类工具上传执行
- 结果复制与下载

## 启动方式

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

默认前端地址：

`http://127.0.0.1:5173`

默认后端 API 地址：

`http://127.0.0.1:8000/api`

如果后端地址不同，修改 `.env.local` 中的 `VITE_API_BASE_URL` 即可。
