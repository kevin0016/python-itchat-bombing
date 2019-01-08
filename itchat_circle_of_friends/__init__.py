import pandas as pd
import itchat
from pyecharts import Pie, Map, Style, Page, Bar
import jieba
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import numpy
import PIL.Image as Image
import os


def get_attr(friends, key):
    return list(map(lambda user: user.get(key), friends))


def get_friends():
    itchat.auto_login(hotReload=True)
    friends = itchat.get_friends()
    users = dict(province=get_attr(friends, "Province"),
                 city=get_attr(friends, "City"),
                 nickname=get_attr(friends, "NickName"),
                 sex=get_attr(friends, "Sex"),
                 signature=get_attr(friends, "Signature"),
                 remarkname=get_attr(friends, "RemarkName"),
                 pyquanpin=get_attr(friends, "PYQuanPin"),
                 displayname=get_attr(friends, "DisplayName"),
                 isowner=get_attr(friends, "IsOwner"))
    return users


def sex_stats(users):
    df = pd.DataFrame(users)
    sex_arr = df.groupby(['sex'], as_index=True)['sex'].count()
    data = dict(zip(list(sex_arr.index), list(sex_arr)))
    data['不告诉你'] = data.pop(0)
    data['帅哥'] = data.pop(1)
    data['美女'] = data.pop(2)
    return data.keys(), data.values()


def prov_stats(users):
    prv = pd.DataFrame(users)
    prv_cnt = prv.groupby('province', as_index=True)['province'].count().sort_values()
    attr = list(map(lambda x: x if x != '' else '未知', list(prv_cnt.index)))
    return attr, list(prv_cnt)


def gd_stats(users):
    df = pd.DataFrame(users)
    data = df.query('province == "广东"')
    res = data.groupby('city', as_index=True)['city'].count().sort_values()
    attr = list(map(lambda x: '%s市' % x if x != '' else '未知', list(res.index)))
    return attr, list(res)


def create_charts():
    users = get_friends()
    page = Page()
    style = Style(width=1100, height=600)
    style_middle = Style(width=900, height=500)
    data = sex_stats(users)
    attr, value = data
    chart = Pie('微信性别')  # title_pos='center'
    chart.add('', attr, value, center=[50, 50],
              radius=[30, 70], is_label_show=True, legend_orient='horizontal', legend_pos='center',
              legend_top='bottom', is_area_show=True)
    page.add(chart)
    data = prov_stats(users)
    attr, value = data
    chart = Map('中国地图', **style.init_style)
    chart.add('', attr, value, is_label_show=True, is_visualmap=True, visual_text_color='#000')
    page.add(chart)
    chart = Bar('柱状图', **style_middle.init_style)
    chart.add('', attr, value, is_stack=True, is_convert=True, label_pos='inside', is_legend_show=True,
              is_label_show=True)
    page.add(chart)
    data = gd_stats(users)
    attr, value = data
    chart = Map('广东', **style.init_style)
    chart.add('', attr, value, maptype='广东', is_label_show=True, is_visualmap=True, visual_text_color='#000')
    page.add(chart)
    chart = Bar('柱状图', **style_middle.init_style)
    chart.add('', attr, value, is_stack=True, is_convert=True, label_pos='inside', is_label_show=True)
    page.add(chart)
    page.render()


def jieba_cut(users):
    signature = users['signature']
    words = ''.join(signature)
    res_list = jieba.cut(words, cut_all=True)
    return res_list


def create_wc(words_list):
    res_path = os.path.abspath('./../resource')
    words = ' '.join(words_list)
    back_pic = numpy.array(Image.open("%s/china1.png" % res_path))
    stopwords = set(STOPWORDS)
    stopwords = stopwords.union(set(['class', 'span', 'emoji', 'emoji', 'emoji1f388', 'emoji1f604', 'emoji1f436']))
    wc = WordCloud(background_color="white", margin=0,
                   font_path='%s/hanyiqihei.ttf' % res_path,
                   mask=back_pic,
                   max_font_size=70,
                   stopwords=stopwords
                   ).generate(words)
    # image_colors = ImageColorGenerator(back_pic)
    plt.imshow(wc)
    # plt.imshow(wc.recolor(color_func=image_colors))
    plt.axis('off')
    plt.show()


if __name__ == '__main__':
    create_charts()
    users = get_friends()
    word_list = jieba_cut(users)
    create_wc(word_list)
