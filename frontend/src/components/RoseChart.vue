<template>
  <div class="rose-chart">
    <div ref="chartRef" style="width: 100%; height: 500px;"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import http from '../http'
import emitter from '../utils/eventBus'
import { categoryMap } from '../utils/chineseMap'

const chartRef = ref<HTMLElement | null>(null)
const loading = ref(true)
let chartInstance: any = null

const fetchDataAndDraw = async (filters: any = { sentiment: 'all', category: 'all' }) => {
  if (!chartRef.value) return
  
  loading.value = true
  
  try {
    const res = await http.post('/filtered_aspect_sentiment', filters)
    const data = res.data
    
    const validData = data.filter((d: any) => d.aspect && d.aspect !== 'NaN')
    
    const roseData = validData.map((d: any) => ({
      name: categoryMap[d.aspect] || d.aspect,
      value: d.positive + d.negative,
      positive: d.positive,
      negative: d.negative,
      positiveRate: (d.positive / (d.positive + d.negative) * 100).toFixed(1)
    }))
    
    await nextTick()
    drawChart(roseData)
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const drawChart = (data: any[]) => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  // 获取实际容器宽度，动态调整玫瑰图大小
  const containerWidth = chartRef.value.clientWidth
  const isSmallScreen = containerWidth < 600
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: '🌹 方面类别评论数量分布（玫瑰图）',
      left: 'center',
      top: 5,
      textStyle: { fontSize: 14, fontWeight: 'normal' }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const item = data[params.dataIndex]
        if (!item) return ''
        return `<strong>${item.name}</strong><br/>
                总评论: ${item.value} 条<br/>
                正面: ${item.positive} 条 (${item.positiveRate}%)<br/>
                负面: ${item.negative} 条`
      }
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      textStyle: { fontSize: isSmallScreen ? 8 : 10 }
    },
    series: [{
      type: 'pie',
      radius: isSmallScreen ? ['15%', '55%'] : ['20%', '65%'],
      center: ['55%', '50%'],
      roseType: 'area',
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: (params: any) => {
          const item = data[params.dataIndex]
          if (!item) return ''
          // 小屏幕时只显示百分比
          if (isSmallScreen) {
            return `${params.percent}%`
          }
          return `${item.name}\n${params.percent}%`
        },
        fontSize: isSmallScreen ? 8 : 9,
        fontWeight: 'bold'
      },
      data: data.map((item: any) => ({
        name: item.name,
        value: item.value,
        itemStyle: {
          color: parseFloat(item.positiveRate) > 50 ? '#52c41a' : '#ff4d4f'
        }
      }))
    }]
  }
  
  chartInstance.setOption(option)
  chartInstance.resize()
}

const handleFilterChange = (filters: any) => {
  fetchDataAndDraw(filters)
}

// 窗口大小变化时重新调整
const handleWindowResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(() => {
  emitter.on('filter-change', handleFilterChange)
  window.addEventListener('resize', handleWindowResize)
  fetchDataAndDraw({ sentiment: 'all', category: 'all' })
})

onUnmounted(() => {
  emitter.off('filter-change', handleFilterChange)
  window.removeEventListener('resize', handleWindowResize)
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped>
.rose-chart { 
  width: 100%; 
  min-height: 500px;
}
.loading { 
  text-align: center; 
  padding: 50px; 
  color: #999;
}
</style>