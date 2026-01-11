import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API请求失败:', error)
    return Promise.reject(error)
  }
)

// 平台数据相关API
export const platformApi = {
  // 获取平台列表
  getPlatforms: (params) => api.get('/platforms', { params }),

  // 获取平台数据
  getPlatformData: (params) => api.get('/platforms/data', { params }),

  // 获取数据概览
  getOverview: () => api.get('/platforms/stats/overview'),

  // 获取平台详情
  getPlatformDetail: (id) => api.get(`/platforms/${id}`),

  // 获取平台时间序列数据
  getPlatformTimeline: (id) => api.get(`/platforms/${id}/timeline`)
}

// 银行数据相关API
export const bankApi = {
  // 获取银行列表
  getBanks: (params) => api.get('/banks', { params }),

  // 获取银行数据
  getBankData: (params) => api.get('/banks/data', { params }),

  // 获取银行数据概览
  getBankOverview: () => api.get('/banks/stats/overview'),

  // 获取银行详情
  getBankDetail: (id) => api.get(`/banks/${id}`),

  // 获取银行时间序列数据
  getBankTimeline: (id) => api.get(`/banks/${id}/timeline`)
}

// 导出相关API
export const exportApi = {
  // 导出平台数据
  exportPlatform: (data) => api.post('/export/platform', data, {
    responseType: 'blob'
  }),

  // 导出银行数据
  exportBank: (data) => api.post('/export/bank', data, {
    responseType: 'blob'
  })
}

export default api
