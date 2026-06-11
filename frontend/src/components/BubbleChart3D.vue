<template>
  <div class="bubble-chart">
    <div ref="chartRef" style="width: 100%; height: 550px;"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import 'echarts-gl'
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
    
    const bubbleData = validData.map((d: any, idx: number) => {
      const total = d.positive + d.negative
      return [idx, d.positive, d.negative, total / 30]
    })
    
    const categories = validData.map((d: any) => categoryMap[d.aspect] || d.aspect)
    
    await nextTick()
    drawChart(bubbleData, categories)
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const drawChart = (data: any[], categories: string[]) => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  // 动态计算相机距离
  const containerWidth = chartRef.value.clientWidth
  const distance = containerWidth < 700 ? 220 : 280
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: '💎 方面类别3D气泡图',
      left: 'center',
      top: 10,
      textStyle: { fontSize: 14, fontWeight: 'normal' }
    },
    tooltip: {
      formatter: (params: any) => {
        if (params.data) {
          const idx = params.data[0]
          if (idx === undefined || !categories[idx]) return ''
          return `<strong>${categories[idx]}</strong><br/>
                  正面评论: ${params.data[1]} 条<br/>
                  负面评论: ${params.data[2]} 条<br/>
                  总计: ${(params.data[1] + params.data[2])} 条`
        }
        return ''
      }
    },
    xAxis3D: {
      type: 'category',
      data: categories,
      name: '方面类别',
      axisLabel: { rotate: 35, interval: 0, fontSize: 10 }
    },
    yAxis3D: {
      type: 'value',
      name: '正面评论数量'
    },
    zAxis3D: {
      type: 'value',
      name: '负面评论数量'
    },
    grid3D: {
      viewControl: {
        autoRotate: true,
        rotateSpeed: 5,
        zoomSpeed: 1,
        distance: distance,
        alpha: 35,
        beta: 45
      },
      light: { main: { intensity: 1.2 }, ambient: { intensity: 0.5 } }
    },
    series: [{
      type: 'scatter3D',
      data: data,
      symbolSize: (params: any) => Math.max(6, params[3] || 8),
      itemStyle: {
        color: (params: any) => {
          const positive = params.data[1]
          const negative = params.data[2]
          return positive > negative ? '#52c41a' : '#ff4d4f'
        },
        opacity: 0.8,
        borderWidth: 1,
        borderColor: '#fff'
      },
      label: {
        show: true,
        formatter: (params: any) => {
          const idx = params.data[0]
          return idx !== undefined && categories[idx] ? categories[idx] : ''
        },
        position: 'top',
        textStyle: { fontSize: 9, fontWeight: 'bold' }
      },
      emphasis: { scale: 1.5 }
    }]
  }
  
  chartInstance.setOption(option)
  chartInstance.resize()
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

const handleFilterChange = (filters: any) => {
  fetchDataAndDraw(filters)
}

onMounted(() => {
  emitter.on('filter-change', handleFilterChange)
  window.addEventListener('resize', handleResize)
  fetchDataAndDraw({ sentiment: 'all', category: 'all' })
})

onUnmounted(() => {
  emitter.off('filter-change', handleFilterChange)
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped>
.bubble-chart { 
  width: 100%; 
  min-height: 550px;
}
.loading { 
  text-align: center; 
  padding: 50px; 
  color: #999;
}
</style>