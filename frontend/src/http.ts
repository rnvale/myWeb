import axios from 'axios'

const http = axios.create({
    baseURL: 'https://myweb-bwk2.onrender.com/api',  // Render 后端地址
    timeout: 10000
})

export default http