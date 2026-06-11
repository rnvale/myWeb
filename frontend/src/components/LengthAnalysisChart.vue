<template>
  <div class="length-analysis">
    <div ref="chartRef" style="width: 100%; height: 450px;"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import http from '../http'
import emitter from '../utils/eventBus'

interface LengthData {
  length_group: string
  positive: number
  negative: number
  total: number
  positive_rate: number
}

const chartRef = ref<HTMLElement | null>(null)
const loading = ref(true)
let chartInstance: any = null

// 长度区间中文映射
const groupMap: Record<string, string> = {
  '短评论(≤20字)': '📝 短评论\n(≤20字)',
  '中评论(21-50字)': '📄 中评论\n(21-50字)',
  '长评论(51-100字)': '📖 长评论\n(51-100字)',
  '超长评论(>100字)': '📚 超长评论\n(>100字)'
}

const fetchDataAndDraw = async (filters: any = { sentiment: 'all', category: 'all' }) => {
  if (!chartRef.value) return
  
  loading.value = true
  
  try {
    // 使用带筛选的接口
    const res = await http.post('/filtered_length_analysis', filters)
    const data = res.data as LengthData[]
    drawChart(data)
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const drawChart = (data: LengthData[]) => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  const lengthGroups = data.map(d => groupMap[d.length_group] || d.length_group)
  const positiveData = data.map(d => d.positive)
  const negativeData = data.map(d => d.negative)
  const positiveRates = data.map(d => d.positive_rate)
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: '📏 评论长度与情感关联分析',
      subtext: '长评论中负面比例更高 | 短评论更偏向正面',
      left: 'center',
      top: 5,
      textStyle: { fontSize: 16, fontWeight: 'bold', color: '#2c3e50' },
      subtextStyle: { fontSize: 11, color: '#7f8c8d' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(0,0,0,0.85)',
      borderColor: '#333',
      borderWidth: 1,
      borderRadius: 8,
      textStyle: { color: '#fff', fontSize: 12 },
      formatter: (params: any) => {
        const idx = params[0].dataIndex
        const d = data[idx]
        if (!d) return ''
        return `<strong style="color: #fff">${d.length_group}</strong><br/>
                <span style="color: #52c41a">👍 正面: ${d.positive} 条 (${d.positive_rate}%)</span><br/>
                <span style="color: #ff4d4f">👎 负面: ${d.negative} 条</span><br/>
                📊 总计: ${d.total} 条`
      }
    },
    legend: {
      data: ['正面评论', '负面评论', '正面率'],
      left: 'left',
      top: 35,
      itemWidth: 25,
      itemHeight: 12,
      textStyle: { fontSize: 12, fontWeight: 'bold' }
    },
    grid: {
      left: '8%',
      right: '8%',
      top: '18%',
      bottom: '10%',
      containLabel: true,
      backgroundColor: '#fafafa',
      borderWidth: 0,
      borderRadius: 8
    },
    xAxis: {
      type: 'category',
      data: lengthGroups,
      name: '评论长度分类',
      nameLocation: 'middle',
      nameGap: 45,
      nameTextStyle: { fontSize: 12, fontWeight: 'bold', color: '#555' },
      axisLabel: { 
        fontSize: 11, 
        fontWeight: 'bold', 
        color: '#2c3e50',
        lineHeight: 20
      },
      axisLine: { lineStyle: { color: '#ccc', width: 1 } },
      axisTick: { show: false }
    },
    yAxis: [
      {
        type: 'value',
        name: '评论数量',
        nameLocation: 'middle',
        nameGap: 45,
        nameTextStyle: { fontSize: 12, fontWeight: 'bold', color: '#555' },
        axisLabel: { fontSize: 11, color: '#666', formatter: '{value}条' },
        splitLine: { lineStyle: { color: '#e8e8e8', type: 'dashed' } }
      },
      {
        type: 'value',
        name: '正面率',
        nameLocation: 'middle',
        nameGap: 45,
        nameTextStyle: { fontSize: 12, fontWeight: 'bold', color: '#555' },
        min: 0,
        max: 100,
        axisLabel: { fontSize: 11, color: '#faad14', formatter: '{value}%' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '正面评论',
        type: 'bar',
        data: positiveData,
        barWidth: '30%',
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#73d13d' },
              { offset: 1, color: '#52c41a' }
            ]
          },
          borderRadius: [8, 8, 0, 0],
          shadowColor: 'rgba(82, 196, 26, 0.3)',
          shadowBlur: 10,
          shadowOffsetY: 4
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}条',
          fontSize: 11,
          fontWeight: 'bold',
          color: '#52c41a'
        },
        animation: true,
        animationDuration: 1000,
        animationEasing: 'cubicOut'
      },
      {
        name: '负面评论',
        type: 'bar',
        data: negativeData,
        barWidth: '30%',
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#ff7875' },
              { offset: 1, color: '#ff4d4f' }
            ]
          },
          borderRadius: [8, 8, 0, 0],
          shadowColor: 'rgba(255, 77, 79, 0.3)',
          shadowBlur: 10,
          shadowOffsetY: 4
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}条',
          fontSize: 11,
          fontWeight: 'bold',
          color: '#ff4d4f'
        },
        animation: true,
        animationDuration: 1000,
        animationEasing: 'cubicOut'
      },
      {
        name: '正面率',
        type: 'line',
        data: positiveRates,
        smooth: true,
        symbol: 'circle',
        symbolSize: 10,
        lineStyle: {
          color: '#faad14',
          width: 3,
          type: 'solid',
          shadowColor: 'rgba(250, 173, 20, 0.3)',
          shadowBlur: 8
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(250, 173, 20, 0.3)' },
              { offset: 1, color: 'rgba(250, 173, 20, 0.05)' }
            ]
          }
        },
        yAxisIndex: 1,
        label: {
          show: true,
          formatter: '{c}%',
          position: 'top',
          fontSize: 11,
          fontWeight: 'bold',
          color: '#faad14',
          backgroundColor: 'rgba(255,255,255,0.8)',
          padding: [2, 6, 2, 6],
          borderRadius: 12
        }
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
.length-analysis { 
  width: 100%; 
  min-height: 450px;
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  border-radius: 12px;
}
.loading { 
  text-align: center; 
  padding: 50px; 
  color: #999;
  font-size: 14px;
}
</style>