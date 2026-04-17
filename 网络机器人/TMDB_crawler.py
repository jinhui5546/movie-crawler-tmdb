
import requests
from lxml import  html
import csv
import os
import re
# 对抓取电影年份进行数据优化
def get_movie_year(movie_year):
    movie_year = movie_year[0].strip() if movie_year else ''
    return movie_year.replace("(","").replace(")","")

# 对电影上映年份数据优化
def get_release_date(release_date):
    release_date = release_date[0].strip() if release_date else ''
    return re.search(r"\d{4}-\d{2}-\d{2}",release_date).group()if re.search(r"\d{4}-\d{2}-\d{2}",release_date) else ''


def get_movie(movie_info_urls):
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    response = requests.get(movie_info_urls,headers= headers)
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
        if page == 0:
            response =requests.get(TMDB_URL)
        else:
           response = requests.post(TMDB_URL2,data = {
    "page": str(current_page),          # 页码（最重要）
    "sort_by": "vote_average.desc",     # 按评分排序
    "vote_count.gte": "300",            # 最少投票数
    "include_adult": "false",           # 排除成人内容
    "release_date.lte": "2026-10-17"    # 上映日期上限
})
        doc = html.fromstring(response.text)
        url_list = doc.xpath("//*[@class='comp:poster-card w-full bg-white border border-light-grey hover:border-gray-300 rounded-lg shadow-lg overflow-hidden']")
        for movie in url_list:
            movie_urls = movie.xpath(".//div/div/a/@href")
            if movie_urls:
                movie_info_urls = TMDB_BASE_URL + movie_urls[0]
                # 通过详情url访问电影详情
                movie_info = get_movie(movie_info_urls)
                all_movie.append(movie_info)
        # 保存到csv
    save_all_movies(all_movie)



if __name__ == '__main__':
    main()