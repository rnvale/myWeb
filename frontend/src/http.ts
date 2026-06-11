import axios from 'axios'

const http = axios.create({
    baseURL: 'http://localhost:5000/api',  // 后端地址，后面启动Flask后会用
    timeout: 10000
})

export default http