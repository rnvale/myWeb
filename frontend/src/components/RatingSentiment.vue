<template>
  <div class="rating-sentiment">
    <div ref="chartRef" style="width: 100%; height: 400px;"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import http from '../http'
import emitter from '../utils/eventBus'

interface RatingData {
  rating: number
  positive: number
  negative: number
  positive_rate: number
  total: number
}

// 方面类别中文映射
const categoryMap: Record<string, string> = {
  'usability': '可用性',
  'general': '整体评价',
  'effectiveness': '有效性',
  'cost': '价格',
  'compatibility': '兼容性',
  'reliability': '可靠性',
  'efficiency': '效率',
  'security': '安全性',
  'safety': '安全',
  'enjoyability': '娱乐性',
  'learnability': '易学性',
  'aesthetics': '美观性'
}

const chartRef = ref<HTMLElement | null>(null)
const loading = ref(true)
let chartInstance: any = null

const fetchDataAndDraw = async (filters: any = { sentiment: 'all', category: 'all' }) => {
  if (!chartRef.value) return
  
  loading.value = true
  
  try {
    const res = await http.post('/filtered_rating_sentiment', filters)
    const data = res.data as RatingData[]
    drawChart(data, filters)
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const drawChart = (data: RatingData[], filters: any) => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  const ratings = data.map((d: RatingData) => `${d.rating}星`)
  const positiveRates = data.map((d: RatingData) => d.positive_rate)
  const totalCounts = data.map((d: RatingData) => d.total)
  
  // 生成副标题 - 包含情感和方面类别
  let subtitle = ''
  if (filters.sentiment === 'positive') subtitle = '（仅正面评论）'
  else if (filters.sentiment === 'negative') subtitle = '（仅负面评论）'
  else subtitle = '（全部评论）'
  
  // 添加方面类别筛选提示
  if (filters.category && filters.category !== 'all') {
    const categoryCn = categoryMap[filters.category] || filters.category
    subtitle += ` | 方面: ${categoryCn}`
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: `⭐ 评分与情感一致性分析 ${subtitle}`,
      left: 'center',
      top: 5,
      textStyle: { fontSize: 14, fontWeight: 'normal', color: '#333' }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const idx = params[0].dataIndex
        const d = data[idx]
        if (!d) return ''
        return `<strong>${d.rating}星</strong><br/>
                正面评论: ${d.positive} 条 (${d.positive_rate}%)<br/>
                负面评论: ${d.negative} 条<br/>
                总计: ${d.total} 条`
      },
      backgroundColor: 'rgba(0,0,0,0.8)',
      borderColor: '#333',
      borderWidth: 1,
      borderRadius: 8,
      textStyle: { color: '#fff', fontSize: 12 }
    },
    legend: {
      data: ['正面率 (%)', '评论总数'],
      left: 'left',
      top: 25,
      textStyle: { fontSize: 12, color: '#333' }
    },
    grid: {
      left: '10%',
      right: '8%',
      top: '15%',
      bottom: '12%',
      containLabel: true,
      backgroundColor: '#fafafa',
      borderWidth: 0,
      borderRadius: 8
    },
    xAxis: {
      type: 'category',
      data: ratings,
      name: '用户评分',
      nameLocation: 'middle',
      nameGap: 38,
      nameTextStyle: { fontSize: 12, fontWeight: 'bold', color: '#555' },
      axisLabel: { fontSize: 11, color: '#666' },
      axisLine: { lineStyle: { color: '#ccc' } }
    },
    yAxis: [
      {
        type: 'value',
        name: '正面率 (%)',
        nameLocation: 'middle',
        nameGap: 45,
        nameTextStyle: { fontSize: 12, fontWeight: 'bold', color: '#52c41a' },
        min: 0,
        max: 100,
        axisLabel: { fontSize: 11, color: '#52c41a', formatter: '{value}%' },
        splitLine: { lineStyle: { color: '#ddd', type: 'dashed' } }
      },
      {
        type: 'value',
        name: '评论总数',
        nameLocation: 'middle',
        nameGap: 45,
        nameTextStyle: { fontSize: 12, fontWeight: 'bold', color: '#5470c6' },
        axisLabel: { fontSize: 11, color: '#5470c6', formatter: '{value}条' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '正面率 (%)',
        type: 'line',
        data: positiveRates,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#52c41a', width: 3 },
        areaStyle: { color: 'rgba(82, 196, 26, 0.1)' },
        yAxisIndex: 0,
        label: { show: true, formatter: '{c}%', position: 'top', color: '#52c41a', fontWeight: 'bold' }
      },
      {
        name: '评论总数',
        type: 'bar',
        data: totalCounts,
        itemStyle: {
          color: '#5470c6',
          borderRadius: [4, 4, 0, 0],
          shadowColor: 'rgba(0,0,0,0.2)',
          shadowBlur: 6
        },
        yAxisIndex: 1,
        label: { show: true, position: 'top', formatter: '{c}条', fontSize: 10, fontWeight: 'bold' },
        barWidth: '30%'
      }
    ],
    backgroundColor: '#fff'
  }
  
  chartInstance.setOption(option)
}

const handleFilterChange = (filters: any) => {
  fetchDataAndDraw(filters)
}

onMounted(() => {
  emitter.on('filter-change', handleFilterChange)
  fetchDataAndDraw({ sentiment: 'all', category: 'all' })
})

onUnmounted(() => {
  emitter.off('filter-change', handleFilterChange)
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped>
.rating-sentiment { width: 100%; min-height: 400px; }
.loading { text-align: center; padding: 50px; color: #999; }
</style>