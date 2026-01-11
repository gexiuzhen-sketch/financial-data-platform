<template>
  <div id="app">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header>
        <div class="header-content">
          <h1 class="title">金融数据聚合平台</h1>
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            router
            class="nav-menu"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/platform">平台数据</el-menu-item>
            <el-menu-item index="/bank">银行数据</el-menu-item>
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
          <p>© {{ currentYear }} 金融数据聚合平台 | 数据来源：研究报告、上市公司财报、官方监管数据、财经媒体</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
const currentYear = new Date().getFullYear()
</script>

<style scoped>
#app {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
}

.title {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.nav-menu {
  border: none;
}

.el-main {
  max-width: 1400px;
  margin: 20px auto;
  padding: 20px;
}

.el-footer {
  background-color: #fff;
  border-top: 1px solid #ebeef5;
  padding: 20px 0;
}

.footer-content {
  text-align: center;
  color: #909399;
  font-size: 14px;
}

.footer-content p {
  margin: 0;
}
</style>
