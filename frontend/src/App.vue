<template>
  <div id="app">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header>
        <div class="header-content">
          <div class="logo-section">
            <div class="logo-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h1 class="title">金融数据聚合平台</h1>
          </div>
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            router
            class="nav-menu"
          >
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/platform">
              <el-icon><Data-Line /></el-icon>
              <span>平台数据</span>
            </el-menu-item>
            <el-menu-item index="/bank">
              <el-icon><Bank /></el-icon>
              <span>银行数据</span>
            </el-menu-item>
            <el-menu-item index="/admin">
              <el-icon><Setting /></el-icon>
              <span>管理后台</span>
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>

      <!-- 主要内容区 -->
      <el-main>
        <router-view />
      </el-main>

      <!-- 底部 -->
      <el-footer>
        <div class="footer-content">
          <p>© {{ currentYear }} 金融数据聚合平台</p>
          <p class="footer-note">数据来源：研究报告、上市公司财报、官方监管数据、财经媒体</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { House, DataLine, Bank, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
const currentYear = new Date().getFullYear()
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
  color: #e0e0e0;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1a1d29;
}

::-webkit-scrollbar-thumb {
  background: #2a2d3d;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #3a3d4d;
}

/* Element Plus 全局样式覆盖 */
.el-container {
  min-height: 100vh;
}

/* 顶部导航栏 */
.el-header {
  background: linear-gradient(145deg, rgba(30, 33, 48, 0.95) 0%, rgba(26, 29, 41, 0.95) 100%);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 30px;
  height: 64px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.logo-icon svg {
  width: 20px;
  height: 20px;
}

.title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.3px;
}

/* 导航菜单 */
.nav-menu {
  border: none;
  background: transparent;
  flex: 1;
  justify-content: flex-end;
}

.nav-menu .el-menu-item {
  color: #8b92a8;
  border: none;
  transition: all 0.2s ease;
  padding: 0 20px;
  height: 64px;
  line-height: 64px;
}

.nav-menu .el-menu-item:hover {
  color: #667eea;
  background: transparent;
}

.nav-menu .el-menu-item.is-active {
  color: #667eea;
  background: transparent;
  position: relative;
}

.nav-menu .el-menu-item.is-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
}

.nav-menu .el-menu-item .el-icon {
  margin-right: 6px;
}

/* 主内容区 */
.el-main {
  max-width: 1600px;
  margin: 0 auto;
  padding: 30px;
  width: 100%;
}

/* 底部 */
.el-footer {
  background: linear-gradient(145deg, rgba(30, 33, 48, 0.95) 0%, rgba(26, 29, 41, 0.95) 100%);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(102, 126, 234, 0.1);
  padding: 25px 0;
  margin-top: auto;
}

.footer-content {
  text-align: center;
  color: #5a5d6d;
  font-size: 14px;
}

.footer-content p {
  margin: 5px 0;
}

.footer-note {
  font-size: 12px;
  color: #4a4d5d;
}

/* 卡片样式 */
.el-card {
  background: linear-gradient(145deg, #1e2130 0%, #1a1d29 100%);
  border: 1px solid #2a2d3d;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.el-card:hover {
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.1);
}

.el-card__header {
  border-bottom: 1px solid #2a2d3d;
  color: #e0e0e0;
}

.el-card__body {
  color: #b0b3c8;
}

/* 表格样式 */
.el-table {
  background: transparent !important;
  color: #e0e0e0;
}

.el-table__row {
  background: transparent !important;
}

.el-table__row:hover > td {
  background: rgba(102, 126, 234, 0.08) !important;
}

.el-table td,
.el-table th {
  border-color: #2a2d3d;
  color: #e0e0e0;
}

.el-table th.el-table__cell {
  background: #1a1d29 !important;
  color: #8b92a8;
}

.el-table--striped .el-table__body tr.el-table__row--striped td {
  background: rgba(102, 126, 234, 0.03) !important;
}

/* 表单样式 */
.el-form-item__label {
  color: #8b92a8;
}

.el-input__wrapper {
  background: #1a1d29;
  border: 1px solid #2a2d3d;
  box-shadow: none;
  transition: all 0.2s ease;
}

.el-input__wrapper:hover {
  border-color: #667eea;
}

.el-input__wrapper.is-focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.el-input__inner {
  color: #e0e0e0;
  background: transparent;
}

.el-input__inner::placeholder {
  color: #5a5d6d;
}

.el-textarea__inner {
  background: #1a1d29;
  border: 1px solid #2a2d3d;
  color: #e0e0e0;
}

.el-textarea__inner::placeholder {
  color: #5a5d6d;
}

/* 选择器 */
.el-select .el-input__wrapper {
  background: #1a1d29;
}

.el-select-dropdown {
  background: #1a1d29;
  border: 1px solid #2a2d3d;
}

.el-select-dropdown__item {
  color: #e0e0e0;
}

.el-select-dropdown__item.hover,
.el-select-dropdown__item:hover {
  background: rgba(102, 126, 234, 0.1);
}

.el-select-dropdown__item.is-selected {
  color: #667eea;
  background: rgba(102, 126, 234, 0.15);
}

/* 日期选择器 */
.el-picker__popper {
  background: #1a1d29;
  border: 1px solid #2a2d3d;
}

.el-picker-panel {
  background: #1a1d29;
  color: #e0e0e0;
}

.el-date-picker__header-label {
  color: #e0e0e0;
}

.el-picker-panel__icon-btn {
  color: #8b92a8;
}

.el-date-table th {
  color: #8b92a8;
  border-color: #2a2d3d;
}

.el-date-table td.available:hover {
  background: rgba(102, 126, 234, 0.1);
}

.el-date-table td.in-range div {
  background: rgba(102, 126, 234, 0.15);
}

.el-date-table td.start-date div,
.el-date-table td.end-date div {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.el-date-table td.current:not(.disabled) div {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

/* 月份选择器 */
.el-month-table td.available:hover {
  background: rgba(102, 126, 234, 0.1);
}

.el-month-table td.in-range div {
  background: rgba(102, 126, 234, 0.15);
}

.el-month-table td.start-date div,
.el-month-table td.end-date div {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.el-month-table td.current:not(.disabled) .cell {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

/* 按钮 */
.el-button {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.el-button--primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.el-button--default {
  background: #1a1d29;
  border: 1px solid #2a2d3d;
  color: #e0e0e0;
}

.el-button--default:hover {
  border-color: #667eea;
  color: #667eea;
}

.el-button--success {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  border: none;
}

.el-button--danger {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  border: none;
}

.el-button--warning {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  border: none;
}

.el-button--info {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border: none;
}

/* 标签 */
.el-tag {
  border-radius: 6px;
  font-weight: 500;
}

/* 分页 */
.el-pagination {
  --el-text-color-regular: #8b92a8;
}

.el-pagination.is-background .el-pager li {
  background: #1a1d29;
  border: 1px solid #2a2d3d;
  color: #8b92a8;
}

.el-pagination.is-background .el-pager li:hover {
  color: #667eea;
}

.el-pagination.is-background .el-pager li.is-active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: #fff;
}

.el-pagination.is-background .btn-prev,
.el-pagination.is-background .btn-next {
  background: #1a1d29;
  border: 1px solid #2a2d3d;
  color: #8b92a8;
}

.el-pagination .el-select .el-input__wrapper {
  background: #1a1d29;
}

/* 对话框 */
.el-dialog {
  background: linear-gradient(145deg, #1e2130 0%, #1a1d29 100%);
  border: 1px solid #2a2d3d;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.el-dialog__header {
  border-bottom: 1px solid #2a2d3d;
}

.el-dialog__title {
  color: #e0e0e0;
}

.el-dialog__body {
  color: #e0e0e0;
}

.el-dialog__footer {
  border-top: 1px solid #2a2d3d;
}

/* 警告框 */
.el-alert {
  border-radius: 10px;
}

.el-alert--info {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
}

.el-alert--success {
  background: rgba(67, 233, 123, 0.1);
  border-color: rgba(67, 233, 123, 0.3);
}

.el-alert--warning {
  background: rgba(250, 112, 154, 0.1);
  border-color: rgba(250, 112, 154, 0.3);
}

.el-alert--error {
  background: rgba(245, 87, 108, 0.1);
  border-color: rgba(245, 87, 108, 0.3);
}

/* 单选框组 */
.el-radio-group {
  background: #1a1d29;
  border-radius: 8px;
  padding: 4px;
}

.el-radio-button__inner {
  background: transparent;
  border: none;
  color: #8b92a8;
  transition: all 0.2s ease;
}

.el-radio-button__original-radio:checked + .el-radio-button__inner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* 输入数字 */
.el-input-number .el-input__wrapper {
  background: #1a1d29;
}

/* 链接按钮 */
.el-button--text {
  color: #667eea;
}

.el-button--text:hover {
  color: #764ba2;
}

/* 菜单项图标 */
.el-menu-item .el-icon {
  font-size: 18px;
}

/* 响应式 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 15px;
  }

  .title {
    font-size: 16px;
  }

  .nav-menu .el-menu-item {
    padding: 0 12px;
  }

  .nav-menu .el-menu-item span {
    display: none;
  }

  .el-main {
    padding: 15px;
  }
}

/* 加载动画 */
.el-loading-mask {
  background: rgba(15, 15, 26, 0.8);
  backdrop-filter: blur(4px);
}

.el-loading-spinner .circular {
  stroke: #667eea;
}

/* 消息提示 */
.el-message {
  background: linear-gradient(145deg, #1e2130 0%, #1a1d29 100%);
  border: 1px solid #2a2d3d;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
}

.el-message--success {
  background: linear-gradient(145deg, #1e2130 0%, #1a1d29 100%);
  border-color: rgba(67, 233, 123, 0.3);
}

.el-message--error {
  background: linear-gradient(145deg, #1e2130 0%, #1a1d29 100%);
  border-color: rgba(245, 87, 108, 0.3);
}

/* 确认框 */
.el-message-box {
  background: linear-gradient(145deg, #1e2130 0%, #1a1d29 100%);
  border: 1px solid #2a2d3d;
  border-radius: 16px;
}

.el-message-box__title {
  color: #e0e0e0;
}

.el-message-box__content {
  color: #b0b3c8;
}

.el-message-box__btns .el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
