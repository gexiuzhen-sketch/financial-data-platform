<template>
  <div class="home">
    <!-- 数据概览卡片 -->
    <div class="stats-grid">
      <div class="stat-card glass-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
          <el-icon><Coin /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(overview.total_balance) }}</div>
          <div class="stat-label">总贷款余额（亿元）</div>
        </div>
        <div class="stat-trend positive" v-if="overview.total_balance">
          <el-icon><TrendCharts /></el-icon>
          <span>实时数据</span>
        </div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(overview.total_issued) }}</div>
          <div class="stat-label">总发放规模（亿元）</div>
        </div>
        <div class="stat-trend positive" v-if="overview.total_issued">
          <el-icon><TrendCharts /></el-icon>
          <span>持续增长</span>
        </div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
          <el-icon><Platform /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.platform_count }}</div>
          <div class="stat-label">平台数量</div>
        </div>
        <div class="stat-badge">{{ overview.latest_month || '暂无数据' }}</div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
          <el-icon><Data-Line /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.by_group?.length || 0 }}</div>
          <div class="stat-label">覆盖集团</div>
        </div>
        <div class="stat-badge">行业领先</div>
      </div>
    </div>

    <!-- 快速入口 -->
    <div class="quick-links">
      <div class="quick-card glass-card" @click="$router.push('/platform')">
        <div class="quick-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="7" width="20" height="14" rx="2" stroke="currentColor" stroke-width="2"/>
            <path d="M7 7V5C7 3.34315 8.34315 2 10 2H14C15.6569 2 17 3.34315 17 5V7" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <div class="quick-content">
          <h3>平台数据</h3>
          <p>查看各互联网助贷平台的贷款规模数据，包括蚂蚁系、腾讯系、字节系、度小满、京东、美团等平台</p>
        </div>
        <div class="quick-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="quick-card glass-card" @click="$router.push('/bank')">
        <div class="quick-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 21H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M5 21V7L12 3L19 7V21" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
            <path d="M9 21V15H15V21" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <div class="quick-content">
          <h3>银行数据</h3>
          <p>查看全国股份制银行与平台合作的互联网贷款业务数据，包括贷款规模、合作平台数量等</p>
        </div>
        <div class="quick-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="quick-card glass-card admin-card" @click="$router.push('/admin')">
        <div class="quick-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
            <path d="M12 1V3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M12 21V23" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M4.22 4.22L5.64 5.64" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M18.36 18.36L19.78 19.78" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M1 12H3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M21 12H23" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M4.22 19.78L5.64 18.36" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M18.36 5.64L19.78 4.22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="quick-content">
          <h3>管理后台</h3>
          <p>数据管理、批量导入、手动更新，支持按日期筛选和删除数据</p>
        </div>
        <div class="quick-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- 按集团统计 -->
    <div class="group-stats glass-card" v-if="overview.by_group && overview.by_group.length > 0">
      <div class="card-header">
        <h3>按集团统计</h3>
        <el-tag type="info" effect="dark">{{ overview.latest_month || '暂无数据' }}</el-tag>
      </div>
      <div class="group-grid">
        <div
          v-for="item in overview.by_group"
          :key="item.group"
          class="group-item"
        >
          <div class="group-icon">{{ item.group?.charAt(0) || '?' }}</div>
          <div class="group-info">
            <div class="group-name">{{ item.group || '未知' }}</div>
            <div class="group-balance">{{ formatNumber(item.total_balance) }} 亿元</div>
          </div>
          <div class="group-count">
            <span class="count">{{ item.platform_count }}</span>
            <span class="label">平台</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state glass-card" v-if="overview.platform_count === 0">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h3>暂无数据</h3>
      <p>请通过管理后台添加数据或批量导入</p>
      <el-button type="primary" @click="$router.push('/admin')">
        <el-icon><Setting /></el-icon>
        前往管理后台
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowRight, Setting } from '@element-plus/icons-vue'

const overview = ref({
  total_balance: 0,
  total_issued: 0,
  platform_count: 0,
  latest_month: null,
  by_group: []
})

const fetchOverview = async () => {
  try {
    const res = await fetch('/api/v1/platforms/stats/overview')
    const json = await res.json()
    if (json.code === 0) {
      overview.value = json.data
    }
  } catch (error) {
    console.error('获取数据概览失败', error)
  }
}

const formatNumber = (num) => {
  if (num === null || num === undefined) return '-'
  return num.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
}

onMounted(() => {
  fetchOverview()
})
</script>

<style scoped>
.home {
  max-width: 1400px;
  margin: 0 auto;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
  margin-bottom: 35px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 25px;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, currentColor, transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card:hover::before {
  opacity: 0.5;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 32px;
  flex-shrink: 0;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #e0e0e0 0%, #b0b3c8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 13px;
  color: #8b92a8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 20px;
}

.stat-trend.positive {
  color: #43e97b;
  background: rgba(67, 233, 123, 0.1);
}

.stat-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 6px 12px;
  background: rgba(102, 126, 234, 0.15);
  border-radius: 20px;
  font-size: 12px;
  color: #8b92a8;
}

/* 玻璃卡片 */
.glass-card {
  background: linear-gradient(145deg, rgba(30, 33, 48, 0.8) 0%, rgba(26, 29, 41, 0.8) 100%);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* 快速入口 */
.quick-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
  margin-bottom: 35px;
}

.quick-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 25px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

.quick-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.quick-icon svg {
  width: 28px;
  height: 28px;
}

.quick-content {
  flex: 1;
}

.quick-content h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #e0e0e0;
}

.quick-content p {
  margin: 0;
  font-size: 14px;
  color: #8b92a8;
  line-height: 1.5;
}

.quick-arrow {
  color: #5a5d6d;
  transition: all 0.3s ease;
}

.quick-card:hover .quick-arrow {
  color: #667eea;
  transform: translateX(4px);
}

.admin-card {
  background: linear-gradient(145deg, rgba(67, 233, 123, 0.1) 0%, rgba(56, 249, 215, 0.05) 100%);
  border-color: rgba(67, 233, 123, 0.2);
}

/* 集团统计 */
.group-stats {
  padding: 25px;
  border-radius: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #e0e0e0;
}

.group-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.group-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 18px;
  background: rgba(26, 29, 41, 0.5);
  border-radius: 14px;
  border: 1px solid #2a2d3d;
  transition: all 0.2s ease;
}

.group-item:hover {
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
}

.group-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.group-info {
  flex: 1;
}

.group-name {
  font-size: 14px;
  font-weight: 600;
  color: #e0e0e0;
  margin-bottom: 4px;
}

.group-balance {
  font-size: 13px;
  color: #8b92a8;
}

.group-count {
  text-align: center;
}

.group-count .count {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #667eea;
}

.group-count .label {
  font-size: 11px;
  color: #5a5d6d;
}

/* 空状态 */
.empty-state {
  padding: 60px 40px;
  text-align: center;
  border-radius: 20px;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 25px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
}

.empty-icon svg {
  width: 40px;
  height: 40px;
}

.empty-state h3 {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
  color: #e0e0e0;
}

.empty-state p {
  margin: 0 0 25px 0;
  font-size: 16px;
  color: #8b92a8;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .quick-links {
    grid-template-columns: 1fr;
  }

  .group-grid {
    grid-template-columns: 1fr;
  }

  .stat-value {
    font-size: 28px;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }
}
</style>
