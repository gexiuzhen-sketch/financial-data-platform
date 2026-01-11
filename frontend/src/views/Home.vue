<template>
  <div class="home">
    <!-- 数据概览卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background-color: #409eff">
              <el-icon><Coin /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ formatNumber(overview.total_balance) }}</div>
              <div class="stat-label">总贷款余额（亿元）</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background-color: #67c23a">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ formatNumber(overview.total_issued) }}</div>
              <div class="stat-label">总发放规模（亿元）</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background-color: #e6a23c">
              <el-icon><Platform /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overview.platform_count }}</div>
              <div class="stat-label">平台数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background-color: #909399">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overview.latest_month || '-' }}</div>
              <div class="stat-label">最新数据月份</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速入口 -->
    <el-row :gutter="20" class="quick-links">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>平台数据</span>
              <el-button type="primary" text @click="$router.push('/platform')">
                查看详情
              </el-button>
            </div>
          </template>
          <p>查看各互联网助贷平台的贷款规模数据，包括蚂蚁系、腾讯系、字节系、度小满、京东、美团等平台。</p>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>银行数据</span>
              <el-button type="primary" text @click="$router.push('/bank')">
                查看详情
              </el-button>
            </div>
          </template>
          <p>查看全国股份制银行与平台合作的互联网贷款业务数据，包括贷款规模、合作平台数量等。</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- 按集团统计 -->
    <el-card shadow="hover" class="group-stats">
      <template #header>
        <div class="card-header">
          <span>按集团统计</span>
          <el-tag type="info">{{ overview.latest_month || '暂无数据' }}</el-tag>
        </div>
      </template>
      <el-table :data="overview.by_group" stripe>
        <el-table-column prop="group" label="集团" width="150" />
        <el-table-column prop="total_balance" label="贷款余额（亿元）">
          <template #default="{ row }">
            {{ formatNumber(row.total_balance) }}
          </template>
        </el-table-column>
        <el-table-column prop="platform_count" label="平台数量" width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { platformApi } from '@/api'
import { ElMessage } from 'element-plus'

const overview = ref({
  total_balance: 0,
  total_issued: 0,
  platform_count: 0,
  latest_month: null,
  by_group: []
})

const fetchOverview = async () => {
  try {
    const res = await platformApi.getOverview()
    if (res.code === 0) {
      overview.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取数据概览失败')
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

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.quick-links {
  margin-bottom: 20px;
}

.quick-links .el-card p {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.group-stats {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
