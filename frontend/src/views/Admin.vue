<template>
  <div class="admin-panel">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card dark-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
          <el-icon><Platform /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.platform_count }}</div>
          <div class="stat-label">平台数据</div>
        </div>
      </div>
      <div class="stat-card dark-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
          <el-icon><Office-building /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.bank_count }}</div>
          <div class="stat-label">银行数据</div>
        </div>
      </div>
      <div class="stat-card dark-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.latest_platform_month || '-' }}</div>
          <div class="stat-label">平台数据月份</div>
        </div>
      </div>
      <div class="stat-card dark-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.scheduled_jobs?.length || 0 }}</div>
          <div class="stat-label">定时任务</div>
        </div>
      </div>
    </div>

    <!-- 操作区 -->
    <div class="action-bar">
      <el-radio-group v-model="activeTab" size="large" class="dark-radio-group">
        <el-radio-button value="platform">平台数据</el-radio-button>
        <el-radio-button value="bank">银行数据</el-radio-button>
      </el-radio-group>

      <div class="action-buttons">
        <el-button type="primary" :icon="Plus" @click="showAddDialog">添加数据</el-button>
        <el-button :icon="Upload" @click="showImportDialog">批量导入</el-button>
        <el-button :icon="Delete" @click="showDeleteDialog" type="danger">按日期删除</el-button>
        <el-button :icon="Refresh" @click="refreshData">刷新</el-button>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="dark-card table-card">
      <el-table
        :data="tableData"
        stripe
        v-loading="loading"
        class="dark-table"
        :header-cell-style="{ background: '#1a1d2d', color: #8b92a8 }"
      >
        <el-table-column prop="report_month" label="报告月份" width="120" />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column v-if="activeTab === 'platform'" prop="company_group" label="所属集团" width="100" />
        <el-table-column v-if="activeTab === 'platform'" prop="platform_type" label="产品类别" width="100" />
        <el-table-column v-if="activeTab === 'platform'" prop="loan_type" label="贷款用途" width="100" />
        <el-table-column v-if="activeTab === 'bank'" prop="bank_type" label="银行类型" width="120" />
        <el-table-column prop="data_source" label="数据来源" min-width="150" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="Edit" @click="editItem(row)">编辑</el-button>
            <el-button type="danger" link :icon="Delete" @click="deleteItem(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :total="pagination.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchData"
          @current-change="fetchData"
          background
        />
      </div>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingItem?.id ? '编辑数据' : '添加数据'"
      width="600px"
      class="dark-dialog"
    >
      <el-form :model="formData" label-width="120px" class="dark-form">
        <el-form-item label="名称">
          <el-input v-model="formData.name" placeholder="请输入名称" />
        </el-form-item>

        <template v-if="activeTab === 'platform'">
          <el-form-item label="所属集团">
            <el-select v-model="formData.company_group" placeholder="请选择">
              <el-option label="蚂蚁" value="蚂蚁" />
              <el-option label="腾讯" value="腾讯" />
              <el-option label="字节" value="字节" />
              <el-option label="京东" value="京东" />
              <el-option label="美团" value="美团" />
              <el-option label="百度" value="百度" />
            </el-select>
          </el-form-item>
          <el-form-item label="产品类别">
            <el-select v-model="formData.platform_type" placeholder="请选择">
              <el-option label="助贷" value="助贷" />
              <el-option label="联合贷" value="联合贷" />
            </el-select>
          </el-form-item>
          <el-form-item label="贷款用途">
            <el-select v-model="formData.loan_type" placeholder="请选择">
              <el-option label="消费类" value="消费类" />
              <el-option label="经营类" value="经营类" />
            </el-select>
          </el-form-item>
          <el-form-item label="贷款余额">
            <el-input-number v-model="formData.loan_balance" :min="0" :precision="2" />
          </el-form-item>
          <el-form-item label="发放规模">
            <el-input-number v-model="formData.loan_issued" :min="0" :precision="2" />
          </el-form-item>
          <el-form-item label="同比增长率">
            <el-input-number v-model="formData.yoy_growth" :precision="2" />
          </el-form-item>
          <el-form-item label="环比增长率">
            <el-input-number v-model="formData.mom_growth" :precision="2" />
          </el-form-item>
        </template>

        <template v-if="activeTab === 'bank'">
          <el-form-item label="银行类型">
            <el-select v-model="formData.bank_type" placeholder="请选择">
              <el-option label="股份制" value="股份制" />
              <el-option label="国有" value="国有" />
              <el-option label="城商行" value="城商行" />
            </el-select>
          </el-form-item>
          <el-form-item label="互联网贷款规模">
            <el-input-number v-model="formData.total_internet_loan" :min="0" :precision="2" />
          </el-form-item>
          <el-form-item label="合作平台数">
            <el-input-number v-model="formData.coop_platform_count" :min="0" />
          </el-form-item>
          <el-form-item label="前3平台占比">
            <el-input-number v-model="formData.top3_platform_share" :min="0" :max="100" :precision="2" />
          </el-form-item>
        </template>

        <el-form-item label="报告月份">
          <el-date-picker
            v-model="formData.report_month"
            type="month"
            format="YYYY-MM"
            value-format="YYYY-MM"
            placeholder="选择月份"
          />
        </el-form-item>

        <el-form-item label="数据来源">
          <el-input v-model="formData.data_source" placeholder="请输入数据来源" />
        </el-form-item>

        <el-form-item label="来源URL">
          <el-input v-model="formData.source_url" placeholder="请输入来源URL（可选）" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入"
      width="700px"
      class="dark-dialog"
    >
      <div class="import-content">
        <el-alert
          title="导入说明"
          type="info"
          :closable="false"
          show-icon
        >
          <p>请按照JSON格式输入数据，每行一条记录。支持从Excel转换后导入。</p>
        </el-alert>

        <el-input
          v-model="importData"
          type="textarea"
          :rows="15"
          placeholder='请粘贴JSON数据，例如：
[
  {
    "name": "花呗",
    "company_group": "蚂蚁",
    "platform_type": "联合贷",
    "loan_type": "消费类",
    "report_month": "2024-12",
    "loan_balance": 1800.5,
    "loan_issued": 320.8,
    "yoy_growth": 15.2,
    "mom_growth": 2.5,
    "data_source": "手动录入"
  }
]'
          class="import-textarea"
        />

        <div class="import-tips">
          <p><strong>平台数据字段：</strong>name, company_group, platform_type, loan_type, report_month, loan_balance, loan_issued, yoy_growth, mom_growth, data_source</p>
          <p><strong>银行数据字段：</strong>name, bank_type, report_month, total_internet_loan, coop_platform_count, top3_platform_share, data_source</p>
        </div>
      </div>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="importData" :loading="importing">导入</el-button>
      </template>
    </el-dialog>

    <!-- 按日期删除对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="按日期范围删除数据"
      width="500px"
      class="dark-dialog"
    >
      <el-form :model="deleteForm" label-width="100px" class="dark-form">
        <el-form-item label="数据类型">
          <el-radio-group v-model="deleteForm.data_type">
            <el-radio value="platform">平台数据</el-radio>
            <el-radio value="bank">银行数据</el-radio>
            <el-radio value="all">全部</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="开始月份">
          <el-date-picker
            v-model="deleteForm.start_month"
            type="month"
            format="YYYY-MM"
            value-format="YYYY-MM"
            placeholder="选择开始月份"
          />
        </el-form-item>
        <el-form-item label="结束月份">
          <el-date-picker
            v-model="deleteForm.end_month"
            type="month"
            format="YYYY-MM"
            value-format="YYYY-MM"
            placeholder="选择结束月份"
          />
        </el-form-item>
      </el-form>

      <el-alert
        title="警告：此操作不可撤销！"
        type="error"
        :closable="false"
        show-icon
        style="margin-top: 15px;"
      />

      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="deleteByDate" :loading="deleting">确认删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Upload, Refresh, Platform as PlatformIcon, OfficeBuilding, Calendar, Timer } from '@element-plus/icons-vue'

const activeTab = ref('platform')
const loading = ref(false)
const saving = ref(false)
const importing = ref(false)
const deleting = ref(false)
const tableData = ref([])
const stats = ref({
  platform_count: 0,
  bank_count: 0,
  latest_platform_month: null,
  latest_bank_month: null,
  scheduled_jobs: []
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const dialogVisible = ref(false)
const editingItem = ref(null)
const formData = reactive({
  name: '',
  company_group: '',
  platform_type: '',
  loan_type: '',
  bank_type: '',
  report_month: '',
  loan_balance: null,
  loan_issued: null,
  yoy_growth: null,
  mom_growth: null,
  total_internet_loan: null,
  coop_platform_count: null,
  top3_platform_share: null,
  data_source: '手动录入',
  source_url: ''
})

const importDialogVisible = ref(false)
const importData = ref('')

const deleteDialogVisible = ref(false)
const deleteForm = reactive({
  data_type: 'platform',
  start_month: '',
  end_month: ''
})

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await fetch('/api/v1/admin/stats')
    const json = await res.json()
    if (json.code === 0) {
      stats.value = json.data
    }
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

// 获取表格数据
const fetchData = async () => {
  loading.value = true
  try {
    const endpoint = activeTab.value === 'platform' ? '/api/v1/admin/platforms' : '/api/v1/admin/banks'
    const params = new URLSearchParams({
      page: pagination.page,
      per_page: pagination.per_page
    })

    const res = await fetch(`${endpoint}?${params}`)
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

// 显示添加对话框
const showAddDialog = () => {
  editingItem.value = null
  Object.assign(formData, {
    name: '',
    company_group: '',
    platform_type: '',
    loan_type: '',
    bank_type: '',
    report_month: '',
    loan_balance: null,
    loan_issued: null,
    yoy_growth: null,
    mom_growth: null,
    total_internet_loan: null,
    coop_platform_count: null,
    top3_platform_share: null,
    data_source: '手动录入',
    source_url: ''
  })
  dialogVisible.value = true
}

// 编辑项目
const editItem = (item) => {
  editingItem.value = item
  Object.assign(formData, item)
  dialogVisible.value = true
}

// 保存项目
const saveItem = async () => {
  saving.value = true
  try {
    const endpoint = activeTab.value === 'platform'
      ? (editingItem.value ? `/api/v1/admin/platforms/${editingItem.value.id}` : '/api/v1/admin/platforms')
      : (editingItem.value ? `/api/v1/admin/banks/${editingItem.value.id}` : '/api/v1/admin/banks')

    const method = editingItem.value ? 'PUT' : 'POST'

    const res = await fetch(endpoint, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    })

    const json = await res.json()

    if (json.code === 0) {
      ElMessage.success(editingItem.value ? '更新成功' : '添加成功')
      dialogVisible.value = false
      fetchData()
      fetchStats()
    } else {
      ElMessage.error(json.message || '操作失败')
    }
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

// 删除项目
const deleteItem = async (id) => {
  try {
    await ElMessageBox.confirm('确认删除此条数据？', '提示', {
      type: 'warning'
    })

    const endpoint = activeTab.value === 'platform'
      ? `/api/v1/admin/platforms/${id}`
      : `/api/v1/admin/banks/${id}`

    const res = await fetch(endpoint, { method: 'DELETE' })
    const json = await res.json()

    if (json.code === 0) {
      ElMessage.success('删除成功')
      fetchData()
      fetchStats()
    } else {
      ElMessage.error(json.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 显示导入对话框
const showImportDialog = () => {
  importData.value = ''
  importDialogVisible.value = true
}

// 导入数据
const importData = async () => {
  importing.value = true
  try {
    const data = JSON.parse(importData.value)

    if (!Array.isArray(data)) {
      throw new Error('数据格式错误：应为数组')
    }

    const endpoint = activeTab.value === 'platform'
      ? '/api/v1/admin/platforms/batch'
      : '/api/v1/admin/banks/batch'

    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data })
    })

    const json = await res.json()

    if (json.code === 0) {
      ElMessage.success(json.message || '导入成功')
      importDialogVisible.value = false
      fetchData()
      fetchStats()
    } else {
      ElMessage.error(json.message || '导入失败')
    }
  } catch (error) {
    ElMessage.error('导入失败：' + error.message)
  } finally {
    importing.value = false
  }
}

// 显示删除对话框
const showDeleteDialog = () => {
  deleteForm.data_type = 'platform'
  deleteForm.start_month = ''
  deleteForm.end_month = ''
  deleteDialogVisible.value = true
}

// 按日期删除
const deleteByDate = async () => {
  if (!deleteForm.start_month || !deleteForm.end_month) {
    ElMessage.warning('请选择开始和结束月份')
    return
  }

  deleting.value = true
  try {
    const res = await fetch('/api/v1/admin/data/delete-by-date', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(deleteForm)
    })

    const json = await res.json()

    if (json.code === 0) {
      ElMessage.success(json.message || '删除成功')
      deleteDialogVisible.value = false
      fetchData()
      fetchStats()
    } else {
      ElMessage.error(json.message || '删除失败')
    }
  } catch (error) {
    ElMessage.error('删除失败')
  } finally {
    deleting.value = false
  }
}

// 刷新数据
const refreshData = () => {
  fetchData()
  fetchStats()
}

// 监听标签切换
const handleTabChange = () => {
  pagination.page = 1
  fetchData()
}

onMounted(() => {
  fetchStats()
  fetchData()
})
</script>

<style scoped>
.admin-panel {
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 120px);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 25px;
  border-radius: 16px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 28px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 13px;
  color: #8b92a8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 操作栏 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

/* 表格卡片 */
.table-card {
  border-radius: 16px;
  overflow: hidden;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 深色卡片基础样式 */
.dark-card {
  background: linear-gradient(145deg, #1e2130 0%, #1a1d29 100%);
  border: 1px solid #2a2d3d;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

/* 深色主题表格 */
:deep(.dark-table) {
  background: transparent;
}

:deep(.dark-table .el-table__row) {
  background: transparent !important;
}

:deep(.dark-table .el-table__row:hover > td) {
  background: rgba(102, 126, 234, 0.1) !important;
}

:deep(.dark-table td) {
  border-color: #2a2d3d;
  color: #e0e0e0;
}

:deep(.dark-table .el-table__body tr.current-row > td) {
  background: rgba(102, 126, 234, 0.15) !important;
}

/* 深色单选按钮组 */
:deep(.dark-radio-group) {
  --el-bg-color: #1e2130;
  --el-border-color: #2a2d3d;
  --el-text-color-regular: #e0e0e0;
}

:deep(.dark-radio-group .el-radio-button__inner) {
  background: #1e2130;
  border-color: #2a2d3d;
  color: #8b92a8;
  transition: all 0.2s ease;
}

:deep(.dark-radio-group .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: #fff;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

/* 深色表单 */
:deep(.dark-form .el-input__wrapper) {
  background: #1a1d29;
  border-color: #2a2d3d;
  box-shadow: none;
}

:deep(.dark-form .el-input__wrapper:hover) {
  border-color: #667eea;
}

:deep(.dark-form .el-input__inner) {
  color: #e0e0e0;
}

:deep(.dark-form .el-input__inner::placeholder) {
  color: #5a5d6d;
}

:deep(.dark-form .el-textarea__inner) {
  background: #1a1d29;
  border-color: #2a2d3d;
  color: #e0e0e0;
}

:deep(.dark-form .el-select .el-input__wrapper) {
  background: #1a1d29;
}

:deep(.dark-form .el-form-item__label) {
  color: #8b92a8;
}

/* 深色对话框 */
:deep(.dark-dialog) {
  --el-bg-color: #1e2130;
  --el-border-color: #2a2d3d;
}

:deep(.dark-dialog .el-dialog__header) {
  border-bottom: 1px solid #2a2d3d;
}

:deep(.dark-dialog .el-dialog__title) {
  color: #e0e0e0;
}

:deep(.dark-dialog .el-dialog__body) {
  background: #1a1d29;
  color: #e0e0e0;
}

:deep(.dark-dialog .el-dialog__footer) {
  border-top: 1px solid #2a2d3d;
  background: #1a1d29;
}

/* 导入区域 */
.import-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.import-textarea {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
}

.import-tips {
  padding: 15px;
  background: #1a1d29;
  border-radius: 8px;
  font-size: 13px;
  color: #8b92a8;
}

.import-tips p {
  margin: 5px 0;
}

.import-tips strong {
  color: #667eea;
}

/* 按钮样式优化 */
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.2s ease;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

:deep(.el-button--danger) {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  border: none;
}

:deep(.el-button--danger:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
}

/* 分页器深色主题 */
:deep(.el-pagination.is-background .el-pager li) {
  background: #1a1d29;
  border: 1px solid #2a2d3d;
  color: #8b92a8;
}

:deep(.el-pagination.is-background .el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: #fff;
}

:deep(.el-pagination.is-background .btn-prev),
:deep(.el-pagination.is-background .btn-next) {
  background: #1a1d29;
  border: 1px solid #2a2d3d;
  color: #8b92a8;
}

:deep(.el-pagination) {
  --el-text-color-regular: #8b92a8;
}

:deep(.el-pagination .el-select .el-input__wrapper) {
  background: #1a1d29;
}

/* 响应式 */
@media (max-width: 768px) {
  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .action-buttons {
    flex-wrap: wrap;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
