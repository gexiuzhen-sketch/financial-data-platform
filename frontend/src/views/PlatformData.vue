<template>
  <div class="platform-data">
    <!-- 筛选面板 -->
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" :model="filters" @submit.prevent="handleSearch">
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
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" :loading="exporting" @click="handleExport">
            导出Excel
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="hover" class="data-card">
      <el-table
        :data="tableData"
        stripe
        border
        v-loading="loading"
        @sort-change="handleSort"
      >
        <el-table-column prop="report_month" label="报告月份" width="120" sortable="custom" />
        <el-table-column prop="name" label="平台名称" width="150" />
        <el-table-column prop="company_group" label="所属集团" width="120" />
        <el-table-column prop="platform_type" label="产品类别" width="120" />
        <el-table-column prop="loan_type" label="贷款用途" width="120" />
        <el-table-column prop="loan_balance" label="贷款余额(亿元)" width="150" sortable="custom">
          <template #default="{ row }">
            {{ formatNumber(row.loan_balance) }}
          </template>
        </el-table-column>
        <el-table-column prop="loan_issued" label="发放规模(亿元)" width="150" sortable="custom">
          <template #default="{ row }">
            {{ formatNumber(row.loan_issued) }}
          </template>
        </el-table-column>
        <el-table-column prop="yoy_growth" label="同比%" width="120">
          <template #default="{ row }">
            <span :class="row.yoy_growth >= 0 ? 'positive' : 'negative'">
              {{ formatPercent(row.yoy_growth) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="mom_growth" label="环比%" width="120">
          <template #default="{ row }">
            <span :class="row.mom_growth >= 0 ? 'positive' : 'negative'">
              {{ formatPercent(row.mom_growth) }}
            </span>
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
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { platformApi, exportApi } from '@/api'
import { ElMessage } from 'element-plus'

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

    const params = {
      ...filters,
      page: pagination.page,
      per_page: pagination.per_page
    }

    const res = await platformApi.getPlatformData(params)
    if (res.code === 0) {
      tableData.value = res.data.items
      pagination.total = res.data.total
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
  // 可以在这里添加排序逻辑
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

    const res = await exportApi.exportPlatform(data)

    // 创建Blob URL并下载
    const blob = new Blob([res], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
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

.filter-card {
  margin-bottom: 20px;
}

.data-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.positive {
  color: #67c23a;
}

.negative {
  color: #f56c6c;
}
</style>
