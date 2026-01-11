<template>
  <div class="bank-data">
    <!-- 筛选面板 -->
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" :model="filters" @submit.prevent="handleSearch">
        <el-form-item label="银行类型">
          <el-select v-model="filters.bank_type" placeholder="全部" clearable>
            <el-option label="股份制" value="股份制" />
            <el-option label="国有" value="国有" />
            <el-option label="城商行" value="城商行" />
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
        <el-table-column prop="name" label="银行名称" width="200" />
        <el-table-column prop="bank_type" label="银行类型" width="150" />
        <el-table-column prop="total_internet_loan" label="互联网贷款规模(亿元)" width="200" sortable="custom">
          <template #default="{ row }">
            {{ formatNumber(row.total_internet_loan) }}
          </template>
        </el-table-column>
        <el-table-column prop="coop_platform_count" label="合作平台数量" width="150" sortable="custom">
          <template #default="{ row }">
            {{ row.coop_platform_count || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="top3_platform_share" label="前3大平台占比(%)" width="180">
          <template #default="{ row }">
            {{ row.top3_platform_share ? row.top3_platform_share.toFixed(2) : '-' }}
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
import { bankApi, exportApi } from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const exporting = ref(false)
const tableData = ref([])
const dateRange = ref([])

const filters = reactive({
  bank_type: '',
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

    const res = await bankApi.getBankData(params)
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
  filters.bank_type = ''
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
      bank_type: filters.bank_type || undefined,
      start_month: filters.start_month || undefined,
      end_month: filters.end_month || undefined
    }

    const res = await exportApi.exportBank(data)

    // 创建Blob URL并下载
    const blob = new Blob([res], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `bank_data_${new Date().getTime()}.xlsx`
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

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.bank-data {
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
</style>
