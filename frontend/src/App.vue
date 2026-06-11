<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="logo" @click="sidebarCollapsed = !sidebarCollapsed">
        <div class="logo-icon">📱</div>
        <div class="logo-text" v-if="!sidebarCollapsed">
          <h2>AppInsight</h2>
          <span>情感分析系统</span>
        </div>
      </div>
      
      <nav class="nav-menu">
        <div class="nav-item" :class="{ active: currentSection === 'overview' }" @click="currentSection = 'overview'">
          <span class="nav-icon">📊</span>
          <span v-if="!sidebarCollapsed">总览仪表盘</span>
        </div>
        <div class="nav-item" :class="{ active: currentSection === 'sentiment' }" @click="currentSection = 'sentiment'">
          <span class="nav-icon">💬</span>
          <span v-if="!sidebarCollapsed">情感分析</span>
        </div>
        <div class="nav-item" :class="{ active: currentSection === 'aspect' }" @click="currentSection = 'aspect'">
          <span class="nav-icon">🔍</span>
          <span v-if="!sidebarCollapsed">方面挖掘</span>
        </div>
        <div class="nav-item" :class="{ active: currentSection === 'apps' }" @click="currentSection = 'apps'">
          <span class="nav-icon">📱</span>
          <span v-if="!sidebarCollapsed">App排行</span>
        </div>
      </nav>
      
      <div class="sidebar-footer" v-if="!sidebarCollapsed">
        <div class="data-badge">
          <span>📊 11,321条</span>
          <span>评论数据</span>
        </div>
      </div>
    </aside>
    
    <main class="main-content">
      <header class="top-bar">
        <div class="page-title">
          <h1>{{ pageTitle }}</h1>
          <p>{{ pageSubtitle }}</p>
        </div>
        <div class="filter-wrapper">
          <FilterBar />
        </div>
      </header>
      
      <div class="content-section">
        
        <!-- 总览仪表盘 -->
        <div v-if="currentSection === 'overview'">
          <div class="kpi-grid">
            <div class="kpi-card">📝 11,321<span>总评论数</span></div>
            <div class="kpi-card positive">👍 5,310<span>正面评论</span></div>
            <div class="kpi-card negative">👎 5,291<span>负面评论</span></div>
            <div class="kpi-card rating">⭐ 3.8<span>平均评分</span></div>
          </div>
          
          <div class="chart-card">
            <div class="chart-header">
              <h3>情感仪表盘</h3>
            </div>
            <div class="chart-body">
              <SentimentGauge />
            </div>
          </div>
          
          <div class="chart-card">
            <div class="chart-header">
              <h3>评分情感分析</h3>
            </div>
            <div class="chart-body">
              <RatingSentiment />
            </div>
          </div>
          
          <div class="chart-card">
            <div class="chart-header">
              <h3>领域对比</h3>
            </div>
            <div class="chart-body">
              <DomainCompare />
            </div>
          </div>
        </div>
        
        <!-- 情感分析 -->
        <div v-if="currentSection === 'sentiment'">
          <div class="chart-card">
            <div class="chart-header">
              <h3>评论长度情感分析</h3>
            </div>
            <div class="chart-body">
              <LengthAnalysisChart />
            </div>
          </div>
          
          <div class="chart-card">
            <div class="chart-header">
              <h3>☁️ 正负面关键词词云</h3>
            </div>
            <div class="chart-body">
              <WordCloud />
            </div>
          </div>
          
          <div class="chart-card">
            <div class="chart-header">
              <h3>🔥 评分-方面情感热力图</h3>
            </div>
            <div class="chart-body">
              <EmotionHeatmap />
            </div>
          </div>
        </div>
        
        <!-- 方面挖掘 -->
        <div v-if="currentSection === 'aspect'">
          <div class="chart-card">
            <div class="chart-header">
              <h3>玫瑰图 - 方面类别评论数量分布</h3>
            </div>
            <div class="chart-body">
              <RoseChart />
            </div>
          </div>
          
          <div class="chart-card">
            <div class="chart-header">
              <h3>3D气泡图 - 方面类别正负面对比</h3>
            </div>
            <div class="chart-body">
              <BubbleChart3D />
            </div>
          </div>
        </div>
        
        <!-- App排行 -->
        <div v-if="currentSection === 'apps'">
          <div class="chart-card">
            <div class="chart-header">
              <h3>🏆 热门App情感河流图</h3>
            </div>
            <div class="chart-body">
              <TopAppsChart />
            </div>
          </div>
          
          <div class="chart-card">
            <div class="chart-header">
              <h3>⭐ App 评分排行榜</h3>
            </div>
            <div class="chart-body">
              <AppRatings />
            </div>
          </div>
          
          <div class="chart-card">
            <div class="chart-header">
              <h3>🎯 App 四象限分析图</h3>
            </div>
            <div class="chart-body">
              <QuadrantScatter />
            </div>
          </div>
        </div>
        
      </div>
      
      <footer class="dashboard-footer">
        <p>数据来源：AWARE 数据集 | 共 11,321 条评论</p>
      </footer>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import FilterBar from './components/FilterBar.vue'
import SentimentGauge from './components/SentimentGauge.vue'
import RatingSentiment from './components/RatingSentiment.vue'
import DomainCompare from './components/DomainCompare.vue'
import RoseChart from './components/RoseChart.vue'
import BubbleChart3D from './components/BubbleChart3D.vue'
import TopAppsChart from './components/TopAppsChart.vue'
import LengthAnalysisChart from './components/LengthAnalysisChart.vue'
import AppRatings from './components/AppRatings.vue'
import EmotionHeatmap from './components/EmotionHeatmap.vue'
import WordCloud from './components/WordCloud.vue'
import QuadrantScatter from './components/QuadrantScatter.vue'

const currentSection = ref('overview')
const sidebarCollapsed = ref(false)

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    overview: '总览仪表盘',
    sentiment: '情感分析',
    aspect: '方面挖掘',
    apps: 'App排行'
  }
  return titles[currentSection.value]
})

const pageSubtitle = computed(() => {
  const subtitles: Record<string, string> = {
    overview: '全局数据概览与核心指标',
    sentiment: '深入分析用户情感倾向',
    aspect: '方面级别评论挖掘',
    apps: '各App情感表现对比'
  }
  return subtitles[currentSection.value]
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --primary-light: #60a5fa;
  --success: #10b981;
  --danger: #ef4444;
  --warning: #f59e0b;
  --bg-sidebar: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  --border: #e2e8f0;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
}

body {
  background: linear-gradient(135deg, #e8f0f8 0%, #d9e4ec 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.dashboard-container {
  display: flex;
  min-height: 100vh;
}

/* 侧边栏 - 深灰蓝 */
.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  color: #fff;
  flex-shrink: 0;
  transition: width 0.3s ease;
  overflow-x: hidden;
}

.sidebar.collapsed {
  width: 70px;
}

.logo {
  padding: 24px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  white-space: nowrap;
}

.sidebar.collapsed .logo {
  justify-content: center;
  padding: 24px 0;
}

.logo-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.logo-text h2 {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.logo-text span {
  font-size: 10px;
  opacity: 0.6;
}

.nav-menu {
  padding: 20px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  transition: all 0.2s;
  white-space: nowrap;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 10px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.nav-item.active {
  background: var(--primary);
  color: #fff;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.nav-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 20px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.data-badge {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 12px;
  text-align: center;
  font-size: 12px;
}

.data-badge span:first-child {
  font-weight: 700;
  font-size: 16px;
  color: #94a3b8;
}

/* 主内容 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  width: 100%;
}

/* 顶部栏 */
.top-bar {
  background: #ffffff;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
  gap: 16px;
  border-radius: 20px 20px 0 0;
}

.page-title h1 {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.page-title p {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

/* 内容区域 */
.content-section {
  padding: 24px;
  flex: 1;
  width: 100%;
}

/* KPI卡片 */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.kpi-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  box-shadow: var(--shadow-md);
  transition: all 0.2s;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.kpi-card span {
  font-size: 12px;
  font-weight: normal;
  color: #64748b;
  margin-left: 8px;
}

/* 图表卡片 */
.chart-card {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: var(--shadow-md);
  overflow: hidden;
  margin-bottom: 28px;
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.chart-card:hover {
  box-shadow: var(--shadow-lg);
}

.chart-header {
  padding: 16px 24px 0;
  border-bottom: 1px solid var(--border);
}

.chart-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-header h3::before {
  content: '';
  width: 4px;
  height: 18px;
  background: linear-gradient(180deg, var(--primary), var(--primary-light));
  border-radius: 2px;
}

.chart-body {
  padding: 16px 20px 20px;
  width: 100%;
  min-height: 450px;
  overflow-x: auto;
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #e2e8f0;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: #94a3b8;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

/* 图表容器 */
.sentiment-gauge,
.rating-sentiment,
.domain-compare,
.rose-chart,
.bubble-chart,
.top-apps-chart,
.length-analysis,
.app-ratings,
.emotion-heatmap {
  width: 100% !important;
  min-width: 900px;
  overflow-x: auto;
  overflow-y: visible;
}

.chart-body > div,
.chart-body > div > div,
.chart-body canvas {
  width: 100% !important;
}

/* 页脚 */
.dashboard-footer {
  background: #ffffff;
  padding: 12px 24px;
  text-align: center;
  border-top: 1px solid var(--border);
  font-size: 11px;
  color: #64748b;
  border-radius: 0 0 20px 20px;
}

/* 响应式 */
@media (max-width: 1000px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }
  
  .sidebar .logo-text,
  .sidebar .nav-item span:last-child,
  .sidebar .sidebar-footer {
    display: none;
  }
  
  .nav-item {
    justify-content: center;
    padding: 12px !important;
  }
  
  .top-bar {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-wrapper {
    width: 100%;
  }
  
  .content-section {
    padding: 16px;
  }
  
  .chart-body {
    padding: 12px 16px 16px;
    min-height: 350px;
  }
  
  .sentiment-gauge,
  .rating-sentiment,
  .domain-compare,
  .rose-chart,
  .bubble-chart,
  .top-apps-chart,
  .length-analysis,
  .app-ratings,
  .emotion-heatmap {
    min-width: 600px;
  }
}
</style>