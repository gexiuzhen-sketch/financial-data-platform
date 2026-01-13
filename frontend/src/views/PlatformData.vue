<template>
  <div class="platform-data">
    <!-- 筛选面板 -->
    <div class="filter-card glass-card">
      <div class="filter-header">
        <h3>数据筛选</h3>
        <el-button link @click="handleReset">
          <el-icon><RefreshLeft /></el-icon>
          重置
        </el-button>
      </div>
      <el-form :inline="true" :model="filters" @submit.prevent="handleSearch" class="filter-form">
        <el-form-item label="所属集团">
          <el-select v-model="filters.company_group" placeholder="全部" clearable>
            <el-option label="蚂蚁" value="蚂蚁" />
            <el-option label="腾讯" value="腾讯" />
            <el-option label="字节" value="字节" />
            <el-option label="京东" value="京东" />
            <el-option label="美团" value="美团" />
            <el-option label="百度" value="百度" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品类别">
          <el-select v-model="filters.platform_type" placeholder="全部" clearable>
            <el-option label="助贷" value="助贷" />
            <el-option label="联合贷" value="联合贷" />
          </el-select>
        </el-form-item>
        <el-form-item label="贷款用途">
          <el-select v-model="filters.loan_type" placeholder="全部" clearable>
            <el-option label="消费类" value="消费类" />
            <el-option label="经营类" value="经营类" />
          </el-select>
        </el-form-item>
        <el-form-item label="月份范围">
          <el-date-picker
            v-model="dateRange"
            type="monthrange"
            range-separator="至"
            start-placeholder="开始月份"
            end-placeholder="结束月份"
            format="YYYY-MM"
            value-format="YYYY-MM"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <div class="table-card glass-card">
      <div class="table-header">
        <h3>平台数据列表</h3>
        <el-button type="success" :loading="exporting" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
      </div>

      <el-table
        :data="tableData"
        v-loading="loading"
        @sort-change="handleSort"
        class="modern-table"
      >
        <el-table-column prop="report_month" label="报告月份" width="120" sortable="custom">
          <template #default="{ row }">
            <span class="month-badge">{{ row.report_month }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="平台名称" width="150">
          <template #default="{ row }">
            <div class="platform-name">
              <span class="name-text">{{ row.name }}</span>
              <el-tag v-if="row.company_group" size="small" effect="plain">{{ row.company_group }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="platform_type" label="产品类别" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.platform_type === '助贷'" type="warning" effect="dark">助贷</el-tag>
            <el-tag v-else-if="row.platform_type === '联合贷'" type="primary" effect="dark">联合贷</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="loan_type" label="贷款用途" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.loan_type === '消费类'" type="success" effect="dark">消费类</el-tag>
            <el-tag v-else-if="row.loan_type === '经营类'" type="info" effect="dark">经营类</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="loan_balance" label="贷款余额(亿元)" width="150" sortable="custom">
          <template #default="{ row }">
            <span class="number-value">{{ formatNumber(row.loan_balance) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="loan_issued" label="发放规模(亿元)" width="150" sortable="custom">
          <template #default="{ row }">
            <span class="number-value">{{ formatNumber(row.loan_issued) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="yoy_growth" label="同比%" width="120">
          <template #default="{ row }">
            <span v-if="row.yoy_growth !== null" :class="row.yoy_growth >= 0 ? 'trend-up' : 'trend-down'">
              <el-icon><component :is="row.yoy_growth >= 0 ? 'CaretTop' : 'CaretBottom'" /></el-icon>
              {{ formatPercent(row.yoy_growth) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="mom_growth" label="环比%" width="120">
          <template #default="{ row }">
            <span v-if="row.mom_growth !== null" :class="row.mom_growth >= 0 ? 'trend-up' : 'trend-down'">
              <el-icon><component :is="row.mom_growth >= 0 ? 'CaretTop' : 'CaretBottom'" /></el-icon>
              {{ formatPercent(row.mom_growth) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="data_source" label="数据来源" min-width="200" show-overflow-tooltip />
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :total="pagination.total"
          :page-sizes="[20, 50, 100, 200]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          background
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Download, RefreshLeft, CaretTop, CaretBottom } from '@element-plus/icons-vue'

const loading = ref(false)
const exporting = ref(false)
const tableData = ref([])
const dateRange = ref([])

const filters = reactive({
  company_group: '',
  platform_type: '',
  loan_type: '',
  start_month: '',
  end_month: ''
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const fetchData = async () => {
  loading.value = true
  try {
    // 处理日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      filters.start_month = dateRange.value[0]
      filters.end_month = dateRange.value[1]
    }

    const params = new URLSearchParams({
      ...filters,
      page: pagination.page,
      per_page: pagination.per_page
    })

    const res = await fetch(`/api/v1/platforms/data?${params}`)
    const json = await res.json()

    if (json.code === 0) {
      tableData.value = json.data.items
      pagination.total = json.data.total
    }
  } catch (error) {
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  filters.company_group = ''
  filters.platform_type = ''
  filters.loan_type = ''
  filters.start_month = ''
  filters.end_month = ''
  dateRange.value = []
  pagination.page = 1
  fetchData()
}

const handleSort = ({ prop, order }) => {
  fetchData()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchData()
}

const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.page = 1
  fetchData()
}

const handleExport = async () => {
  exporting.value = true
  try {
    // 处理日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      filters.start_month = dateRange.value[0]
      filters.end_month = dateRange.value[1]
    }

    const data = {
      company_group: filters.company_group || undefined,
      platform_type: filters.platform_type || undefined,
      loan_type: filters.loan_type || undefined,
      start_month: filters.start_month || undefined,
      end_month: filters.end_month || undefined
    }

    const res = await fetch('/api/v1/export/platform', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })

    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `platform_data_${new Date().getTime()}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const formatNumber = (num) => {
  return num ? num.toLocaleString('zh-CN', { maximumFractionDigits: 2 }) : '-'
}

const formatPercent = (num) => {
  return num ? `${num.toFixed(2)}%` : '-'
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.platform-data {
  max-width: 1400px;
  margin: 0 auto;
}

/* 玻璃卡片 */
.glass-card {
  background: linear-gradient(145deg, rgba(30, 33, 48, 0.8) 0%, rgba(26, 29, 41, 0.8) 100%);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border-radius: 20px;
  margin-bottom: 25px;
}

/* 筛选面板 */
.filter-card {
  padding: 25px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #e0e0e0;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-form .el-form-item {
  margin-bottom: 0;
}

/* 表格卡片 */
.table-card {
  padding: 25px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #e0e0e0;
}

/* 表格样式 */
:deep(.modern-table) {
  background: transparent;
}

:deep(.modern-table .el-table__row) {
  background: transparent !important;
  transition: all 0.2s ease;
}

:deep(.modern-table .el-table__row:hover > td) {
  background: rgba(102, 126, 234, 0.08) !important;
}

:deep(.modern-table td) {
  border-color: #2a2d3d;
  color: #e0e0e0;
}

:deep(.modern-table th.el-table__cell) {
  background: #1a1d29 !important;
  color: #8b92a8;
  border-color: #2a2d3d;
}

:deep(.modern-table--striped .el-table__body tr.el-table__row--striped td) {
  background: rgba(102, 126, 234, 0.02) !important;
}

/* 月份徽章 */
.month-badge {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(102, 126, 234, 0.15);
  border-radius: 6px;
  font-size: 13px;
  color: #667eea;
  font-weight: 500;
}

/* 平台名称 */
.platform-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name-text {
  font-weight: 500;
  color: #e0e0e0;
}

/* 数值 */
.number-value {
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  font-weight: 600;
  color: #e0e0e0;
}

/* 趋势 */
.trend-up {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #43e97b;
  font-weight: 500;
}

.trend-down {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #f5576c;
  font-weight: 500;
}

/* 分页 */
.pagination {
  margin-top: 25px;
  display: flex;
  justify-content: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .filter-form {
    flex-direction: column;
  }

  .filter-form .el-form-item {
    width: 100%;
  }

  .table-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
}
</style>
