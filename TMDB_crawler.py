
import requests
from lxml import  html
import csv
import os
import re
import time
import random
# User-Agent池，模拟不同浏览器
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
]

# 获取随机请求头
def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
    }

# 带重试的请求函数
def safe_request(url, method='GET', data=None, max_retries=3, delay_range=(2, 5)):
    """
    安全的请求函数，包含重试机制和随机延迟
    :param url: 请求URL
    :param method: 请求方法 GET 或 POST
    :param data: POST请求的数据
    :param max_retries: 最大重试次数
    :param delay_range: 请求间隔时间范围(秒)
    :return: response对象或None
    """
    for attempt in range(max_retries):
        try:
            headers = get_random_headers()
            # 随机延迟，模拟人类行为
            time.sleep(random.uniform(*delay_range))
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.post(url, headers=headers, data=data, timeout=10)
            
            response.raise_for_status()  # 如果状态码不是200，抛出异常
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {url} - {str(e)}")
            if attempt < max_retries - 1:
                wait_time = random.uniform(5, 10)  # 重试前等待更长时间
                print(f"等待 {wait_time:.1f} 秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"请求最终失败: {url}")
                return None

# 对抓取电影年份进行数据优化
def get_movie_year(movie_year):
    movie_year = movie_year[0].strip() if movie_year else ''
    return movie_year.replace("(","").replace(")","")

# 对电影上映年份数据优化
def get_release_date(release_date):
    release_date = release_date[0].strip() if release_date else ''
    return re.search(r"\d{4}-\d{2}-\d{2}",release_date).group()if re.search(r"\d{4}-\d{2}-\d{2}",release_date) else ''


def get_movie(movie_info_urls):
    response = safe_request(movie_info_urls, method='GET')
    if not response:
        return None
    
    doc = html.fromstring(response.text)
    movie_name = doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/a/text()")
    # print(movie_name)
    movie_year = doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/span/text()")
    release_date = doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[2]/text()")
    movie_genre = doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[3]/a/text()")
    movie_duration = doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[4]/text()")
    movie_rating = doc.xpath("//*[@id='consensus_pill']/div/div[1]/div/div/@data-percent")
    movie_language = doc.xpath("//*[@id='media_v4']/div/div/div[2]/div/section/div[1]/div/section[1]/p[3]/text()")
    movie_director = doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/ol/li[1]/p[1]/a/text()")
    movie_novel = doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/ol/li[2]/p[1]/a/text()")
    movie_slogan = doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/h3[1]/text()")
    movie_synopsis = doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/div/p/text()")
    movie_info = {
        "电影名":movie_name[0].strip()if movie_name else '',
        "上映年份":get_movie_year(movie_year) ,
        "上映时间":get_release_date(release_date),
        "电影类型":",".join(movie_genre) if movie_genre else '',
        "电影时长":movie_duration[0].strip() if movie_duration else '',
        "评分":movie_rating[0].strip() if movie_rating else '',
        "语言":movie_language[0].strip() if movie_language else '',
        "导演":movie_director[0].strip() if movie_director else '',
        "编剧":movie_novel[0].strip() if movie_novel else '',
        "电影简介":movie_synopsis[0].strip() if movie_synopsis else '',
        "电影标语":movie_slogan[0].strip() if movie_slogan else ''


    }
    return movie_info


def save_all_movies(all_movie):
    os.makedirs('csv_data',exist_ok=True)
    with open('csv_data/all_movie.csv','w',encoding='utf-8-sig',newline='')as f:
        writer = csv.DictWriter(f,fieldnames=["电影名","上映年份","上映时间","电影类型","电影时长","评分","语言","导演","编剧","电影简介","电影标语"])
        writer.writeheader()
        writer.writerows(all_movie)


def main():
    #获取页面所有电影详情url
    TMDB_BASE_URL = "https://www.themoviedb.org"
    TMDB_URL = "https://www.themoviedb.org/movie/top-rated"#第一页
    TMDB_URL2 = "https://www.themoviedb.org/discover/movie/items"#第二页及以后
    page_num = int(input("输入采取页数") )
    all_movie = []
    for page in range(page_num):
        current_page = page+1
        print(f"\n正在爬取第 {current_page}/{page_num} 页...")
        
        if page == 0:
            response = safe_request(TMDB_URL, method='GET')
        else:
            response = safe_request(TMDB_URL2, method='POST', data={
                "page": str(current_page),          # 页码（最重要）
                "sort_by": "vote_average.desc",     # 按评分排序
                "vote_count.gte": "300",            # 最少投票数
                "include_adult": "false",           # 排除成人内容
                "release_date.lte": "2026-10-17"    # 上映日期上限
            })
        
        if not response:
            print(f"第 {current_page} 页获取失败，跳过")
            continue
        doc = html.fromstring(response.text)
        url_list = doc.xpath("//*[@class='comp:poster-card w-full bg-white border border-light-grey hover:border-gray-300 rounded-lg shadow-lg overflow-hidden']")
        for movie in url_list:
            movie_urls = movie.xpath(".//div/div/a/@href")
            if movie_urls:
                movie_info_urls = TMDB_BASE_URL + movie_urls[0]
                # 通过详情url访问电影详情
                movie_info = get_movie(movie_info_urls)
                if movie_info:  # 只添加成功获取的信息
                    all_movie.append(movie_info)
                    print(f"  ✓ 已获取: {movie_info['电影名']}")
                else:
                    print(f"  ✗ 获取失败")
        
        print(f"第 {current_page} 页完成，当前共获取 {len(all_movie)} 部电影")
        
        # 每页之间额外延迟，进一步降低被封风险
        if page < page_num - 1:
            extra_delay = random.uniform(3, 6)
            print(f"等待 {extra_delay:.1f} 秒...")
            time.sleep(extra_delay)
        # 保存到csv
    save_all_movies(all_movie)



if __name__ == '__main__':
    main()