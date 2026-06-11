from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# 加载数据
print("正在加载数据...")
df = pd.read_csv('data/AWARE_Comprehensive.csv')
print(f"数据加载完成！共 {len(df)} 条记录")

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'message': '后端连接成功！', 'status': 'ok'})

@app.route('/api/summary', methods=['GET'])
def get_summary():
    sentiment_counts = df['sentiment'].value_counts().to_dict()
    aspect_counts = df['category'].value_counts().to_dict()
    return jsonify({'sentiment': sentiment_counts, 'aspect': aspect_counts})

@app.route('/api/aspect_sentiment', methods=['GET'])
def get_aspect_sentiment():
    result = []
    for category in df['category'].unique():
        if pd.isna(category):
            continue
        subset = df[df['category'] == category]
        result.append({
            'aspect': category,
            'positive': len(subset[subset['sentiment'] == 'positive']),
            'negative': len(subset[subset['sentiment'] == 'negative'])
        })
    return jsonify(result)

@app.route('/api/filtered_summary', methods=['POST'])
def get_filtered_summary():
    filters = request.json
    filtered_df = df.copy()
    
    if filters.get('sentiment') and filters.get('sentiment') != 'all':
        filtered_df = filtered_df[filtered_df['sentiment'] == filters['sentiment']]
    
    if filters.get('category') and filters.get('category') != 'all':
        filtered_df = filtered_df[filtered_df['category'] == filters['category']]
    
    sentiment_counts = filtered_df['sentiment'].value_counts().to_dict()
    return jsonify({
        'sentiment': sentiment_counts,
        'total': len(filtered_df)
    })

@app.route('/api/filtered_aspect_sentiment', methods=['POST'])
def get_filtered_aspect_sentiment():
    filters = request.json
    filtered_df = df.copy()
    
    if filters.get('sentiment') and filters.get('sentiment') != 'all':
        filtered_df = filtered_df[filtered_df['sentiment'] == filters.get('sentiment')]
    
    if filters.get('category') and filters.get('category') != 'all':
        filtered_df = filtered_df[filtered_df['category'] == filters.get('category')]
    
    result = []
    for category in filtered_df['category'].unique():
        if pd.isna(category):
            continue
        subset = filtered_df[filtered_df['category'] == category]
        result.append({
            'aspect': category,
            'positive': len(subset[subset['sentiment'] == 'positive']),
            'negative': len(subset[subset['sentiment'] == 'negative'])
        })
    return jsonify(result)

@app.route('/api/rating_sentiment', methods=['GET'])
def get_rating_sentiment():
    valid_df = df[df['rating'].notna()]
    result = []
    for rating in range(1, 6):
        rating_df = valid_df[valid_df['rating'] == rating]
        if len(rating_df) > 0:
            positive = len(rating_df[rating_df['sentiment'] == 'positive'])
            negative = len(rating_df[rating_df['sentiment'] == 'negative'])
            total = positive + negative
            result.append({
                'rating': rating,
                'positive': positive,
                'negative': negative,
                'positive_rate': round(positive / total * 100, 1) if total > 0 else 0,
                'total': total
            })
    return jsonify(result)

@app.route('/api/domain_compare', methods=['GET'])
def get_domain_compare():
    valid_df = df[df['domain'].notna()]
    result = []
    for domain in valid_df['domain'].unique():
        domain_df = valid_df[valid_df['domain'] == domain]
        positive = len(domain_df[domain_df['sentiment'] == 'positive'])
        negative = len(domain_df[domain_df['sentiment'] == 'negative'])
        total = positive + negative
        result.append({
            'domain': domain,
            'positive': positive,
            'negative': negative,
            'positive_rate': round(positive / total * 100, 1) if total > 0 else 0,
            'total': total
        })
    return jsonify(result)

# ========== 新增接口 ==========

@app.route('/api/top_apps', methods=['GET'])
def get_top_apps():
    """热门App情感排行"""
    app_counts = df['app'].value_counts().head(15).index
    result = []
    for app in app_counts:
        if pd.isna(app):
            continue
        app_df = df[df['app'] == app]
        positive = len(app_df[app_df['sentiment'] == 'positive'])
        negative = len(app_df[app_df['sentiment'] == 'negative'])
        total = positive + negative
        result.append({
            'app': app,
            'positive': positive,
            'negative': negative,
            'total': total,
            'positive_rate': round(positive / total * 100, 1) if total > 0 else 0
        })
    result.sort(key=lambda x: x['total'], reverse=True)
    return jsonify(result)

@app.route('/api/filtered_top_apps', methods=['POST'])
def get_filtered_top_apps():
    """支持筛选的热门App情感排行"""
    filters = request.json
    filtered_df = df.copy()
    
    # 应用筛选
    if filters.get('sentiment') and filters.get('sentiment') != 'all':
        filtered_df = filtered_df[filtered_df['sentiment'] == filters['sentiment']]
    
    if filters.get('category') and filters.get('category') != 'all':
        filtered_df = filtered_df[filtered_df['category'] == filters['category']]
    
    # 获取评论最多的前15个App
    app_counts = filtered_df['app'].value_counts().head(15).index
    result = []
    for app in app_counts:
        if pd.isna(app):
            continue
        app_df = filtered_df[filtered_df['app'] == app]
        positive = len(app_df[app_df['sentiment'] == 'positive'])
        negative = len(app_df[app_df['sentiment'] == 'negative'])
        total = positive + negative
        result.append({
            'app': app,
            'positive': positive,
            'negative': negative,
            'total': total,
            'positive_rate': round(positive / total * 100, 1) if total > 0 else 0
        })
    result.sort(key=lambda x: x['total'], reverse=True)
    return jsonify(result)

@app.route('/api/length_analysis', methods=['GET'])
def get_length_analysis():
    """评论长度与情感分析"""
    temp_df = df.copy()
    temp_df['text_length'] = temp_df['sentence'].fillna('').astype(str).str.len()
    
    bins = [0, 20, 50, 100, float('inf')]
    labels = ['短评论(≤20字)', '中评论(21-50字)', '长评论(51-100字)', '超长评论(>100字)']
    
    temp_df['length_group'] = pd.cut(temp_df['text_length'], bins=bins, labels=labels, right=False)
    
    result = []
    for group in labels:
        group_df = temp_df[temp_df['length_group'] == group]
        positive = len(group_df[group_df['sentiment'] == 'positive'])
        negative = len(group_df[group_df['sentiment'] == 'negative'])
        total = positive + negative
        result.append({
            'length_group': group,
            'positive': positive,
            'negative': negative,
            'total': total,
            'positive_rate': round(positive / total * 100, 1) if total > 0 else 0
        })
    return jsonify(result)

@app.route('/api/filtered_length_analysis', methods=['POST'])
def get_filtered_length_analysis():
    """支持筛选的评论长度与情感分析"""
    filters = request.json
    filtered_df = df.copy()
    
    if filters.get('sentiment') and filters.get('sentiment') != 'all':
        filtered_df = filtered_df[filtered_df['sentiment'] == filters['sentiment']]
    
    if filters.get('category') and filters.get('category') != 'all':
        filtered_df = filtered_df[filtered_df['category'] == filters['category']]
    
    temp_df = filtered_df.copy()
    temp_df['text_length'] = temp_df['sentence'].fillna('').astype(str).str.len()
    
    bins = [0, 20, 50, 100, float('inf')]
    labels = ['短评论(≤20字)', '中评论(21-50字)', '长评论(51-100字)', '超长评论(>100字)']
    
    temp_df['length_group'] = pd.cut(temp_df['text_length'], bins=bins, labels=labels, right=False)
    
    result = []
    for group in labels:
        group_df = temp_df[temp_df['length_group'] == group]
        positive = len(group_df[group_df['sentiment'] == 'positive'])
        negative = len(group_df[group_df['sentiment'] == 'negative'])
        total = positive + negative
        result.append({
            'length_group': group,
            'positive': positive,
            'negative': negative,
            'total': total,
            'positive_rate': round(positive / total * 100, 1) if total > 0 else 0
        })
    return jsonify(result)

@app.route('/api/filtered_domain_compare', methods=['POST'])
def get_filtered_domain_compare():
    """支持筛选的不同App领域情感对比"""
    filters = request.json
    filtered_df = df.copy()
    
    if filters.get('sentiment') and filters.get('sentiment') != 'all':
        filtered_df = filtered_df[filtered_df['sentiment'] == filters['sentiment']]
    
    if filters.get('category') and filters.get('category') != 'all':
        filtered_df = filtered_df[filtered_df['category'] == filters['category']]
    
    valid_df = filtered_df[filtered_df['domain'].notna()]
    result = []
    for domain in valid_df['domain'].unique():
        domain_df = valid_df[valid_df['domain'] == domain]
        positive = len(domain_df[domain_df['sentiment'] == 'positive'])
        negative = len(domain_df[domain_df['sentiment'] == 'negative'])
        total = positive + negative
        result.append({
            'domain': domain,
            'positive': positive,
            'negative': negative,
            'positive_rate': round(positive / total * 100, 1) if total > 0 else 0,
            'total': total
        })
    return jsonify(result)

@app.route('/api/filtered_rating_sentiment', methods=['POST'])
def get_filtered_rating_sentiment():
    """支持筛选的评分-情感一致性分析"""
    filters = request.json
    filtered_df = df.copy()
    
    if filters.get('sentiment') and filters.get('sentiment') != 'all':
        filtered_df = filtered_df[filtered_df['sentiment'] == filters['sentiment']]
    
    if filters.get('category') and filters.get('category') != 'all':
        filtered_df = filtered_df[filtered_df['category'] == filters['category']]
    
    valid_df = filtered_df[filtered_df['rating'].notna()]
    result = []
    for rating in range(1, 6):
        rating_df = valid_df[valid_df['rating'] == rating]
        if len(rating_df) > 0:
            positive = len(rating_df[rating_df['sentiment'] == 'positive'])
            negative = len(rating_df[rating_df['sentiment'] == 'negative'])
            total = positive + negative
            result.append({
                'rating': rating,
                'positive': positive,
                'negative': negative,
                'positive_rate': round(positive / total * 100, 1) if total > 0 else 0,
                'total': total
            })
    return jsonify(result)

@app.route('/api/app_ratings', methods=['GET'])
def get_app_ratings():
    """各App平均评分"""
    valid_df = df[df['rating'].notna()]
    result = []
    for app in valid_df['app'].unique():
        if pd.isna(app):
            continue
        app_df = valid_df[valid_df['app'] == app]
        avg_rating = app_df['rating'].mean()
        total = len(app_df)
        result.append({
            'app': app,
            'avg_rating': round(avg_rating, 2),
            'total': total
        })
    result.sort(key=lambda x: x['total'], reverse=True)
    return jsonify(result[:15])

@app.route('/api/emotion_heatmap', methods=['GET'])
def get_emotion_heatmap():
    """方面类别 × 情感 × 评分的三维热力图数据"""
    # 简化：返回方面类别 × 评分的正面率
    result = []
    for rating in range(1, 6):
        rating_df = df[df['rating'] == rating]
        for category in df['category'].unique():
            if pd.isna(category):
                continue
            cat_df = rating_df[rating_df['category'] == category]
            if len(cat_df) == 0:
                continue
            positive = len(cat_df[cat_df['sentiment'] == 'positive'])
            negative = len(cat_df[cat_df['sentiment'] == 'negative'])
            total = positive + negative
            result.append({
                'rating': rating,
                'category': category,
                'positive_rate': round(positive / total * 100, 1) if total > 0 else 0,
                'total': total
            })
    return jsonify(result)

@app.route('/api/filtered_emotion_heatmap', methods=['POST'])
def get_filtered_emotion_heatmap():
    """支持筛选的情感热力图"""
    filters = request.json
    filtered_df = df.copy()
    
    if filters.get('sentiment') and filters.get('sentiment') != 'all':
        filtered_df = filtered_df[filtered_df['sentiment'] == filters['sentiment']]
    
    if filters.get('category') and filters.get('category') != 'all':
        filtered_df = filtered_df[filtered_df['category'] == filters['category']]
    
    result = []
    for rating in range(1, 6):
        rating_df = filtered_df[filtered_df['rating'] == rating]
        for category in filtered_df['category'].unique():
            if pd.isna(category):
                continue
            cat_df = rating_df[rating_df['category'] == category]
            if len(cat_df) == 0:
                continue
            positive = len(cat_df[cat_df['sentiment'] == 'positive'])
            negative = len(cat_df[cat_df['sentiment'] == 'negative'])
            total = positive + negative
            result.append({
                'rating': rating,
                'category': category,
                'positive_rate': round(positive / total * 100, 1) if total > 0 else 0,
                'total': total
            })
    return jsonify(result)

@app.route('/api/filtered_app_ratings', methods=['POST'])
def get_filtered_app_ratings():
    """支持筛选的App评分排行"""
    filters = request.json
    filtered_df = df.copy()
    
    if filters.get('sentiment') and filters.get('sentiment') != 'all':
        filtered_df = filtered_df[filtered_df['sentiment'] == filters['sentiment']]
    
    if filters.get('category') and filters.get('category') != 'all':
        filtered_df = filtered_df[filtered_df['category'] == filters['category']]
    
    valid_df = filtered_df[filtered_df['rating'].notna()]
    result = {}
    for app in valid_df['app'].unique():
        if pd.isna(app):
            continue
        app_df = valid_df[valid_df['app'] == app]
        avg_rating = app_df['rating'].mean()
        total = len(app_df)
        result[app] = {
            'app': app,
            'avg_rating': round(avg_rating, 2),
            'total': total
        }
    result_list = list(result.values())
    result_list.sort(key=lambda x: x['total'], reverse=True)
    return jsonify(result_list[:15])

from collections import Counter
import re

# 术语中英文映射表
TERM_MAP = {
    'update': '更新', 'page': '页面', 'money': '价格', 'text': '文本',
    'sync': '同步', 'list': '列表', 'photo': '照片', 'notification': '通知',
    'version': '版本', 'design': '设计', 'chat': '聊天', 'account': '账户',
    'group': '群组', 'document': '文档', 'functionality': '功能', 'price': '价格',
    'interface': '界面', 'tag': '标签', 'color': '颜色', 'sound': '声音',
    'new version': '新版本', 'user interface': '用户界面', 'customer service': '客服',
    'battery': '电池', 'performance': '性能', 'speed': '速度', 'crash': '崩溃',
    'bug': '漏洞', 'feature': '功能', 'experience': '体验', 'quality': '质量',
    'design': '设计', 'support': '支持', 'update': '更新', 'fix': '修复',
    'improve': '改进', 'add': '添加', 'remove': '移除', 'change': '更改',
    'easy': '容易', 'simple': '简单', 'useful': '有用', 'helpful': '有帮助',
    'great': '很棒', 'good': '好', 'excellent': '优秀', 'amazing': '惊艳',
    'awesome': '超棒', 'perfect': '完美', 'love': '喜爱', 'like': '喜欢',
    'recommend': '推荐', 'suggest': '建议', 'hope': '希望', 'want': '想要',
    'problem': '问题', 'issue': '问题', 'error': '错误', 'fail': '失败',
    'slow': '慢', 'fast': '快', 'smooth': '流畅', 'stable': '稳定',
    'unstable': '不稳定', 'crash': '闪退', 'freeze': '卡死', 'lag': '卡顿'
}

from collections import Counter
import re

@app.route('/api/filtered_wordcloud', methods=['POST'])
def get_filtered_wordcloud():
    """支持筛选的词云数据"""
    filters = request.json
    filtered_df = df.copy()
    
    if filters.get('sentiment') and filters.get('sentiment') != 'all':
        filtered_df = filtered_df[filtered_df['sentiment'] == filters['sentiment']]
    
    if filters.get('category') and filters.get('category') != 'all':
        filtered_df = filtered_df[filtered_df['category'] == filters['category']]
    
    # 停用词列表（过滤无意义的词）
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'so', 'for', 'of', 'to', 'in', 'on', 'at', 
                 'with', 'without', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'this', 'that', 'these',
                 'those', 'it', 'its', 'it\'s', 'they', 'them', 'their', 'we', 'our', 'you', 'your',
                 'he', 'she', 'his', 'her', 'i', 'me', 'my', 'mine', 'app', 'apps', 'use', 'used', 'using',
                 'get', 'got', 'make', 'made', 'like', 'would', 'could', 'should', 'very', 'really', 'also',
                 '甚至', '非常', '一个', '这个', '那个', '这些', '那些', '可以', '能够', '需要', '想要', '觉得', '感觉',
                 '的', '了', '和', '与', '或', '但是', '所以', '因为', '如果', '虽然', '然而', '由于', '为了'}
    
    # 正面评论文本
    positive_texts = filtered_df[filtered_df['sentiment'] == 'positive']['term'].dropna().tolist()
    # 负面评论文本
    negative_texts = filtered_df[filtered_df['sentiment'] == 'negative']['term'].dropna().tolist()
    
    def process_texts(texts):
        word_counts = Counter()
        for text in texts:
            # 简单分词（按空格和特殊字符分割）
            words = re.findall(r'[a-zA-Z]+(?:[-\'][a-zA-Z]+)*|[\\u4e00-\\u9fa5]+', text.lower())
            for word in words:
                word_lower = word.lower()
                if len(word_lower) < 3 or word_lower in stopwords:
                    continue
                word_counts[word_lower] += 1
        return [{'name': word, 'value': count} for word, count in word_counts.most_common(50)]
    
    result = {
        'positive': process_texts(positive_texts),
        'negative': process_texts(negative_texts)
    }
    
    return jsonify(result)

@app.route('/api/quadrant_scatter', methods=['GET'])
def get_quadrant_scatter():
    """四象限散点图数据：评分 vs 评论数量"""
    valid_df = df[df['rating'].notna()]
    
    # 聚合每个App的评分和评论数
    result = []
    for app in valid_df['app'].unique():
        if pd.isna(app):
            continue
        app_df = valid_df[valid_df['app'] == app]
        avg_rating = app_df['rating'].mean()
        total_reviews = len(app_df)
        positive_rate = len(app_df[app_df['sentiment'] == 'positive']) / total_reviews * 100
        
        result.append({
            'app': app,
            'avg_rating': round(avg_rating, 2),
            'total_reviews': total_reviews,
            'positive_rate': round(positive_rate, 1)
        })
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)