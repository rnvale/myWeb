好的，我为你撰写一份适合放在 GitHub 仓库的 `README.md` 文件，内容涵盖项目简介、功能特点、技术栈、安装运行、部署地址、数据来源、图表说明等。

```markdown
# App评论情感分析可视化系统

基于 AWARE 数据集的 App 评论情感分析可视化系统，提供多维度、交互式的数据分析与可视化展示。

## 📊 项目简介

本项目是一个完整的全栈数据可视化应用，旨在帮助产品经理和开发者快速洞察用户评论中的情感倾向和关注重点。系统从整体情感倾向、评分一致性、领域差异、方面类别分布、具体 App 表现、评论行为特征、关键词词云、App 四象限定位等多个维度，对用户评论进行深入挖掘。

## ✨ 功能特点

- **多维度分析**：覆盖整体情感、评分一致性、领域对比、方面挖掘、App 排行等 11 个分析维度
- **丰富的可视化**：仪表盘、雷达图、玫瑰图、3D 气泡图、河流图、热力图、词云图、四象限图等 11 种图表
- **交互式筛选**：支持按情感类型（正面/负面/全部）和方面类别进行筛选，所有图表实时联动更新
- **悬停提示与动画**：每个图表均支持鼠标悬停查看详情，渲染时带有平滑动画效果
- **前后端分离**：Vue3 + Flask 架构，代码清晰，易于维护和扩展
- **云端部署**：前端部署于 Vercel，后端部署于 Render，支持公网访问

## 🛠 技术栈

### 前端
- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite
- **图表库**：ECharts、ECharts GL、echarts-wordcloud、D3.js
- **UI 组件**：Element Plus
- **网络请求**：Axios
- **事件通信**：Mitt

### 后端
- **框架**：Flask
- **跨域支持**：Flask-CORS
- **数据处理**：Pandas

### 部署
- **前端**：Vercel
- **后端**：Render
- **代码托管**：GitHub

## 📁 项目结构

```
VisProject/
├── frontend/               # Vue3 前端项目
│   ├── src/
│   │   ├── components/     # 11 个图表组件 + 筛选器组件
│   │   ├── utils/          # 中英文映射、事件总线
│   │   ├── App.vue         # 主布局（侧边栏导航 + 页面切换）
│   │   └── main.ts         # 入口文件
│   └── package.json
├── backend/                # Flask 后端项目
│   ├── app.py              # API 接口（数据分析与筛选）
│   ├── data/               # AWARE 数据集
│   └── requirements.txt    # Python 依赖
└── README.md
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/YYJXX-lab/myWeb.git
cd myWeb
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

后端服务将在 `http://localhost:5000` 启动。

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端服务将在 `http://localhost:5173` 启动。

### 4. 访问系统

打开浏览器访问 `http://localhost:5173` 即可使用。

## 📊 图表清单

| 序号 | 图表名称 | 图表类型 | 分析维度 |
|------|----------|----------|----------|
| 1 | 情感仪表盘 | 仪表盘 + 环形图 | 整体情感倾向 |
| 2 | 评分情感分析 | 折线图 + 柱状图 | 评分与情感一致性 |
| 3 | 领域雷达图 | 雷达图 | 不同领域 App 对比 |
| 4 | 方面玫瑰图 | 南丁格尔玫瑰图 | 方面类别关注度 |
| 5 | 3D 气泡图 | 3D 气泡图 | 方面类别正负面对比 |
| 6 | 热门 App 河流图 | 堆叠面积图 | 具体 App 情感表现 |
| 7 | 评论长度分析 | 分组柱状图 + 折线图 | 评论长度与情感关系 |
| 8 | 情感热力图 | 热力图 | 评分-方面情感分布 |
| 9 | 关键词词云 | 词云图 | 正负面关键词对比 |
| 10 | 四象限分析图 | 四象限散点图 | App 产品定位 |
| 11 | App 评分排行榜 | 水平条形图 | 热门 App 评分排名 |

## 📈 核心结论

1. **整体评价趋于平衡**：正面 50.1%，负面 49.9%
2. **三星用户是矛盾群体**：正面率 44.3%，最值得关注
3. **游戏 App 正面率最高**（52.4%），社交网络最低（44.7%）
4. **娱乐性是亮点**（正面率 69%），**可靠性是痛点**（负面率 73%）
5. **整体评价类最受关注**（约 3000 条评论）
6. **长评论更倾向于负面表达**

## 📦 部署地址

- **前端**：[https://my-web-olive-ten.vercel.app](https://my-web-olive-ten.vercel.app)
- **后端**：[https://myweb-bwk2.onrender.com](https://myweb-bwk2.onrender.com)

## 📚 数据来源

- **数据集名称**：AWARE（App Review Analysis with Weak REcognition）
- **访问地址**：[https://opendatalab.com/OpenDataLab/AWARE](https://opendatalab.com/OpenDataLab/AWARE)
- **数据规模**：11,321 条标注评论，12 个方面类别

## 📄 开源协议

本项目仅供学习交流使用。

## 👤 作者

- **GitHub**：[YYJXX-lab](https://github.com/YYJXX-lab)
```
