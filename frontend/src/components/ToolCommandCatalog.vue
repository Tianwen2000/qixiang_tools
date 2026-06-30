<script setup>
// 文件说明：定义 ToolCommandCatalog 前端组件。
import { computed, ref } from "vue";

import { getCommandCatalog } from "../data/command-catalogs.js";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const keyword = ref("");
const sqlExamplesOpen = ref(false);
const commands = computed(() => getCommandCatalog(props.tool.slug));
const isMysqlCatalog = computed(() => props.tool.slug === "mysql-command-search");
// MySQL 增删改查示例只在 MySQL 命令工具里展示，避免给其它命令集合增加无关按钮。
const mysqlSqlExamples = `-- 建表示例
CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  account VARCHAR(32) NOT NULL UNIQUE,
  nickname VARCHAR(64) NOT NULL,
  status TINYINT NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 新增数据
INSERT INTO users (account, nickname, status)
VALUES ('15573808035', '管理员', 1);

-- 批量新增
INSERT INTO users (account, nickname, status)
VALUES
  ('11111111111', '测试账号A', 1),
  ('12222222222', '测试账号B', 1);

-- 查询全部字段
SELECT * FROM users;

-- 按条件查询
SELECT id, account, nickname, status, created_at
FROM users
WHERE status = 1
ORDER BY id DESC
LIMIT 20;

-- 模糊查询
SELECT id, account, nickname
FROM users
WHERE nickname LIKE CONCAT('%', '测试', '%');

-- 更新数据
UPDATE users
SET nickname = '新昵称'
WHERE id = 1;

-- 软删除 / 禁用
UPDATE users
SET status = 0
WHERE id = 1;

-- 物理删除，执行前务必确认条件
DELETE FROM users
WHERE id = 1;

-- 聚合统计
SELECT status, COUNT(*) AS total
FROM users
GROUP BY status;

-- 分页查询
SELECT id, account, nickname
FROM users
ORDER BY id DESC
LIMIT 20 OFFSET 40;

-- 事务示例
START TRANSACTION;
UPDATE users SET status = 0 WHERE id = 1;
INSERT INTO users (account, nickname) VALUES ('13333333333', '事务新增账号');
COMMIT;

-- 回滚事务
ROLLBACK;

-- 索引示例
CREATE INDEX idx_users_status_created_at ON users (status, created_at);

-- 查询计划
EXPLAIN SELECT * FROM users WHERE status = 1 ORDER BY created_at DESC LIMIT 20;`;
const results = computed(() => {
  const query = keyword.value.trim().toLowerCase();
  if (!query) {
    return commands.value;
  }
  const tokens = query.split(/[\s,，]+/).filter(Boolean);
  return commands.value.filter((item) => {
    const haystack = [item.command, item.summary, ...(item.tags || [])].join(" ").toLowerCase();
    return tokens.every((token) => haystack.includes(token));
  });
});

function openSqlExamples() {
  sqlExamplesOpen.value = true;
}

function closeSqlExamples() {
  sqlExamplesOpen.value = false;
}
</script>

<template>
  <section class="tool-form command-catalog-shell">
    <div class="command-catalog-toolbar">
      <label class="command-catalog-search">
        <span>检索命令</span>
        <input v-model="keyword" type="search" placeholder="输入命令、参数或用途关键词" />
      </label>
      <div class="command-catalog-actions">
        <button v-if="isMysqlCatalog" type="button" class="command-catalog-example-button" @click="openSqlExamples">
          增删改查 SQL 示例
        </button>
        <div class="command-catalog-count">
          <strong>{{ results.length }}</strong>
          <span>/ {{ commands.length }} 条</span>
        </div>
      </div>
    </div>

    <section v-if="!results.length" class="time-tool-empty">没有找到匹配的命令。</section>
    <div v-else class="command-catalog-table-wrap">
      <table class="command-catalog-table">
        <thead>
          <tr>
            <th scope="col">命令</th>
            <th scope="col">说明</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in results" :key="item.command">
            <td><code>{{ item.command }}</code></td>
            <td>{{ item.summary }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <Teleport to="body">
      <div v-if="sqlExamplesOpen" class="command-catalog-modal" @keydown.esc="closeSqlExamples">
        <button type="button" class="command-catalog-modal-backdrop" aria-label="关闭 SQL 示例" @click="closeSqlExamples"></button>
        <section class="command-catalog-modal-card" role="dialog" aria-modal="true" aria-label="MySQL 增删改查 SQL 示例">
          <header class="command-catalog-modal-head">
            <div>
              <span>MYSQL</span>
              <h3>增删改查 SQL 示例</h3>
            </div>
            <button type="button" aria-label="关闭" @click="closeSqlExamples">×</button>
          </header>
          <pre><code>{{ mysqlSqlExamples }}</code></pre>
        </section>
      </div>
    </Teleport>
  </section>
</template>
