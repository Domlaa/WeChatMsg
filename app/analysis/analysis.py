import os
from collections import Counter
import sys
from datetime import datetime
from typing import List

import jieba

from app.DataBase import msg_db, MsgType, misc_db, micro_msg_db, hard_link_db, media_msg_db, init_db
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Calendar, Bar, Line, Pie, Map

from app.person import Contact, Me
from app.util.region_conversion import conversion_province_to_chinese
from datetime import datetime

os.makedirs('./data/聊天统计/', exist_ok=True)


def wordcloud_(wxid, time_range=None):
    import jieba
    txt_messages = msg_db.get_messages_by_type(wxid, MsgType.TEXT, time_range=time_range)
    if not txt_messages:
        return {
            'chart_data': None,
            'keyword': "没有聊天你想分析啥",
            'max_num': "0",
            'dialogs': []
        }
    # text = ''.join(map(lambda x: x[7], txt_messages))
    text = ''.join(map(lambda x: x[7], txt_messages))  # 1“我”说的话，0“Ta”说的话

    total_msg_len = len(text)
    # 使用jieba进行分词，并加入停用词
    words = jieba.cut(text)
    # 统计词频
    word_count = Counter(words)
    # 过滤停用词
    stopwords_file = './app/data/stopwords.txt'
    with open(stopwords_file, "r", encoding="utf-8") as stopword_file:
        stopwords1 = set(stopword_file.read().splitlines())
    # 构建 FFmpeg 可执行文件的路径
    stopwords = set()
    stopwords_file = './app/resources/data/stopwords.txt'
    if not os.path.exists(stopwords_file):
        resource_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        stopwords_file = os.path.join(resource_dir, 'app', 'resources', 'data', 'stopwords.txt')
    with open(stopwords_file, "r", encoding="utf-8") as stopword_file:
        stopwords = set(stopword_file.read().splitlines())
        stopwords = stopwords.union(stopwords1)
    filtered_word_count = {word: count for word, count in word_count.items() if len(word) > 1 and word not in stopwords}

    # 转换为词云数据格式
    data = [(word, count) for word, count in filtered_word_count.items()]
    # text_data = data
    data.sort(key=lambda x: x[1], reverse=True)

    text_data = data[:100] if len(data) > 100 else data
    # 创建词云图
    keyword, max_num = text_data[0]
    w = (
        WordCloud(init_opts=opts.InitOpts())
        .add(series_name="聊天文字", data_pair=text_data, word_size_range=[5, 100])
    )
    # return w.render_embed()
    return {
        'chart_data': w.dump_options_with_quotes(),
        'keyword': keyword,
        'max_num': str(max_num),
        'dialogs': msg_db.get_messages_by_keyword(wxid, keyword, num=5, max_len=12)
    }


def get_wordcloud(text):
    total_msg_len = len(text)
    jieba.load_userdict('./app/data/new_words.txt')
    # 使用jieba进行分词，并加入停用词
    words = jieba.cut(text)
    # 统计词频
    word_count = Counter(words)
    # 过滤停用词
    stopwords_file = './app/data/stopwords.txt'
    with open(stopwords_file, "r", encoding="utf-8") as stopword_file:
        stopwords1 = set(stopword_file.read().splitlines())
    # 构建 FFmpeg 可执行文件的路径
    stopwords = set()
    stopwords_file = './app/resources/data/stopwords.txt'
    if not os.path.exists(stopwords_file):
        resource_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        stopwords_file = os.path.join(resource_dir, 'app', 'resources', 'data', 'stopwords.txt')
    with open(stopwords_file, "r", encoding="utf-8") as stopword_file:
        stopwords = set(stopword_file.read().splitlines())
        stopwords = stopwords.union(stopwords1)

    filtered_word_count = {word: count for word, count in word_count.items() if len(word) > 1 and word not in stopwords}
    # 转换为词云数据格式
    data = [(word, count) for word, count in filtered_word_count.items()]
    # text_data = data
    data.sort(key=lambda x: x[1], reverse=True)

    text_data = data[:100] if len(data) > 100 else data
    # 创建词云图
    if text_data:
        keyword, max_num = text_data[0]
    else:
        keyword, max_num = '', 0
    w = (
        WordCloud()
        .add(series_name="聊天文字", data_pair=text_data, word_size_range=[5, 40])
    )
    return {
        'chart_data_wordcloud': w.dump_options_with_quotes(),
        'keyword': keyword,
        'keyword_max_num': max_num,
    }


def wordcloud_christmas(wxid, time_range=None, year='2023'):
    import jieba

    txt_messages = msg_db.get_messages_by_type(wxid, MsgType.TEXT, time_range=time_range)
    if not txt_messages:
        return {
            'wordcloud_chart_data': None,
            'keyword': "没有聊天你想分析啥",
            'max_num': '0',
            'dialogs': [],
            'total_num': 0,
        }
    text = ''.join(map(lambda x: x[7], txt_messages))
    total_msg_len = len(text)
    wordcloud_data = get_wordcloud(text)
    # return w.render_embed()
    keyword = wordcloud_data.get('keyword')
    max_num = wordcloud_data.get('keyword_max_num')
    dialogs = msg_db.get_messages_by_keyword(wxid, keyword, num=3, max_len=12, time_range=time_range)

    return {
        'wordcloud_chart_data': wordcloud_data.get('chart_data_wordcloud'),
        'keyword': keyword,
        'keyword_max_num': str(max_num),
        'dialogs': dialogs,
        'total_num': total_msg_len,
    }


def calendar_chart(wxid, time_range=None):
    calendar_data = msg_db.get_messages_by_days(wxid, time_range)
    if not calendar_data:
        return {
            'chart_data': None,
            'calendar_chart_data': None,
            'chat_days': 0,
            # 'chart':c,
        }
    min_ = min(map(lambda x: x[1], calendar_data))
    max_ = max(map(lambda x: x[1], calendar_data))
    start_date_ = calendar_data[0][0]
    end_date_ = calendar_data[-1][0]
    print(start_date_, '---->', end_date_)
    calendar_days = (start_date_, end_date_)
    calendar_title = '和Ta的聊天情况'
    c = (
        Calendar()
        .add(
            "",
            calendar_data,
            calendar_opts=opts.CalendarOpts(range_=calendar_days)
        )
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(
                max_=max_,
                min_=min_,
                orient="horizontal",
                pos_bottom="0px",
                pos_left="0px",
            ),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    return {
        'chart_data': c.dump_options_with_quotes(),
        'calendar_chart_data': c.dump_options_with_quotes(),
        'chat_days': len(calendar_data),
        # 'chart':c,
    }


def month_count(wxid, time_range=None):
    """
    每月聊天条数
    """
    msg_data = msg_db.get_messages_by_month(wxid, time_range)
    y_data = list(map(lambda x: x[1], msg_data))
    x_axis = list(map(lambda x: x[0], msg_data))
    m = (
        Bar(init_opts=opts.InitOpts())
        .add_xaxis(x_axis)
        .add_yaxis("消息数量", y_data,
                   label_opts=opts.LabelOpts(is_show=True),
                   itemstyle_opts=opts.ItemStyleOpts(color="#ffae80"),
                   )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="逐月统计", subtitle=None),
            datazoom_opts=opts.DataZoomOpts(),
            toolbox_opts=opts.ToolboxOpts(),
            yaxis_opts=opts.AxisOpts(
                name="消息数",
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            visualmap_opts=opts.VisualMapOpts(
                min_=min(y_data),
                max_=max(y_data),
                dimension=1,  # 根据第2个维度（y 轴）进行映射
                is_piecewise=False,  # 是否分段显示
                range_color=["#ffbe7a", "#fa7f6f"],  # 设置颜色范围
                type_="color",
                pos_right="0%",
            ),
        )
    )
    return {
        'chart_data': m.dump_options_with_quotes(),
        # 'chart': m,
    }


def hour_count(wxid, is_Annual_report=False, year='2023'):
    """
    小时计数聊天条数
    """
    msg_data = msg_db.get_messages_by_hour(wxid, is_Annual_report, year)
    print(msg_data)
    y_data = list(map(lambda x: x[1], msg_data))
    x_axis = list(map(lambda x: x[0], msg_data))
    h = (
        Line(init_opts=opts.InitOpts())
        .add_xaxis(xaxis_data=x_axis)
        .add_yaxis(
            series_name="聊天频率",
            y_axis=y_data,
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值", value=int(10)),
                ]
            ),
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="average", name="平均值")]
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="聊天时段", subtitle=None),
            # datazoom_opts=opts.DataZoomOpts(),
            # toolbox_opts=opts.ToolboxOpts(),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(
                is_show=False
            )
        )
    )

    return {
        'chart_data': h
    }


types = {
    '文本': 1,
    '图片': 3,
    '语音': 34,
    '视频': 43,
    '表情包': 47,
    '音乐与音频': 4903,
    '文件': 4906,
    '分享卡片': 4905,
    '转账': 492000,
    '音视频通话': 50,
    '拍一拍等系统消息': 10000,
}
types_ = {
    1: '文本',
    3: '图片',
    34: '语音',
    43: '视频',
    47: '表情包',
    4957: '引用消息',
    4903: '音乐与音频',
    4906: '文件',
    4905: '分享卡片',
    492000: '转账',
    50: '音视频通话',
    10000: '拍一拍等系统消息',
}


def get_weekday(timestamp):
    # 将时间戳转换为日期时间对象
    dt_object = datetime.fromtimestamp(timestamp)

    # 获取星期几，0代表星期一，1代表星期二，以此类推
    weekday = dt_object.weekday()
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return weekdays[weekday]


# 三张饼图的数据
def sender(wxid, time_range, my_name='', ta_name=''):
    # 根据参数获取消息
    msg_data = []
    try:
        msg_data = msg_db.get_messages(wxid, time_range)
    except Exception as e:
        print(f"fail Exception: {e}")

    print(f"{wxid} find msg size: {len(msg_data)}")
    # 消息类型 字典 统计数量
    types_count = {}
    # 发送次数
    send_num = 0  # 发送消息的数量
    # 周数据 字典 (key=周几, value=count)
    weekday_count = {}
    # 发言次数 字典 (key=remark, value=count)
    chat_count = {}
    # 发言天数 字典 (key=remark, value=count)
    chat_day_count = {}
    # 熬夜冠军 字典 (key=remark, value=count)
    night_owls = {}

    for message in msg_data:
        type_ = message[2]
        is_sender = message[4]
        subType = message[3]
        timestamp = message[5]
        # 计算是周几
        weekday = get_weekday(timestamp)
        str_content = message[7]
        str_time = message[8]
        # 如果是自己发的消息 is_sender = 1 否则 = 0
        send_num += is_sender
        # 如果 subType 不为 0，将主类型和子类型拼接成字符串，子类型用两位数字表示（如 1 -> 01）。
        # 如果 subType = 0，则只保留主类型。
        # subType:0>2d 是一种格式化字符串的写法，用于将整数 subType 格式化为两位数的字符串。
        # 如果 subType 的值不足两位，则在左侧填充 0。
        type_ = f'{type_}{subType:0>2d}' if subType != 0 else type_
        type_ = int(type_)
        if type_ in types_count:
            types_count[type_] += 1
        else:
            types_count[type_] = 1
        if weekday in weekday_count:
            weekday_count[weekday] += 1
        else:
            weekday_count[weekday] = 1
        if wxid.__contains__('@chatroom'):
            contact = message[13]
            unique_id = get_unique_id(contact)
            # if not contact.nickName:
            #      unique_id = contract.nickName
            # elif not contact.remark:
            #     unique_id = contract.remark
            # else:
            #     unique_id = contract.wxid
            if not unique_id:
                # print(f"uniqueId null: {str_content}")
                pass
            else:
                # print(f"{unique_id} : {str_content}")
                if unique_id in chat_count:
                    chat_count[unique_id] += 1
                else:
                    print(f"id: {unique_id} , remark: {contact.remark}, nick:{contact.nickName}, name:{contact}")
                    chat_count[unique_id] = 1

                if unique_id in chat_day_count:
                    chat_day_count[unique_id] += 1
                else:
                    print(f"id: {unique_id} , remark: {contact.remark}, nick:{contact.nickName}, name:{contact}")
                    chat_day_count[unique_id] = 1

    # 这里就能得到收到的消息数
    receive_num = len(msg_data) - send_num
    data = [[types_.get(key), value] for key, value in types_count.items() if key in types_]
    print(
        f"[{my_name}] <--> [{ta_name}] 数据统计： 消息占比：{data}, 收发：{receive_num}/{send_num}, 星期分布: {weekday_count}, 发言次数: {chat_count}")
    if not data:
        return {
            'chart_data_sender': None,
            'chart_data_types': None,
            'chart_data_weekday': None,
            'chart_data_chat': None,
            'chart_data_chat_day': None,
            'chart_data_night_owls': None,
        }
    p1 = (
        Pie()
        .add(
            "",
            data,
            center=["40%", "50%"],
        )
        .set_global_opts(
            datazoom_opts=opts.DataZoomOpts(),
            toolbox_opts=opts.ToolboxOpts(),
            title_opts=opts.TitleOpts(title="消息类型占比"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", pos_top="20%", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        # .render("./data/聊天统计/types_pie.html")
    )
    p2 = (
        Pie()
        .add(
            "",
            [[my_name, send_num], [ta_name, receive_num]],
            center=["40%", "50%"],
        )
        .set_global_opts(
            datazoom_opts=opts.DataZoomOpts(),
            toolbox_opts=opts.ToolboxOpts(),
            title_opts=opts.TitleOpts(title="双方消息占比"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", pos_top="20%", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}\n{d}%"))
        # .render("./data/聊天统计/pie_scroll_legend.html")
    )
    p3 = (
        Pie()  # 创建一个 `Pie` 对象，表示饼图。
        .add(
            "",
            [[key, value] for key, value in weekday_count.items()],  # 数据项为 weekday_count 字典的键值对，转换成 [(key, value)] 的格式。
            radius=["40%", "75%"],  # 饼图的半径，设置为一个环形图。内圈半径为 40%，外圈半径为 75%。
        )
        .set_global_opts(
            datazoom_opts=opts.DataZoomOpts(),  # 配置数据缩放功能（通常用于其他类型的图表，饼图默认无法使用）。
            toolbox_opts=opts.ToolboxOpts(),  # 工具箱选项，提供工具（如保存图片、数据视图等）。
            title_opts=opts.TitleOpts(title="星期分布图"),  # 设置图表标题为“星期分布图”。
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"),  # 配置图例，设置为垂直布局，位置在图表左上角。
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}: {c}\n{d}%")  # 配置饼图的标签格式：显示名称({b})、值({c}) 和百分比({d})。
        )
        # .render("./data/聊天统计/pie_weekdays.html")  # （注释掉的代码）将图表渲染为 HTML 文件，保存到指定路径。
    )
    chat_bar = (
        Bar()
        .add_xaxis(list(chat_count.keys()))  # 从字典的键中获取 x 轴数据（姓名）
        .add_yaxis("发言次数", list(chat_count.values()))  # 从字典的值中获取 y 轴数据（得分）
        .reversal_axis()  # 转换坐标轴，使其变为水平条形图
        .set_global_opts(
            title_opts=opts.TitleOpts(title="活跃度统计"),
            xaxis_opts=opts.AxisOpts(name="发言次数", type_="value"),
            yaxis_opts=opts.AxisOpts(name="群员"),
        )
    )
    chat_day_bar = (
        Bar()
        .add_xaxis(list(chat_day_count.keys()))  # 从字典的键中获取 x 轴数据（姓名）
        .add_yaxis("发言天数", list(chat_day_count.values()))  # 从字典的值中获取 y 轴数据（得分）
        .reversal_axis()  # 转换坐标轴，使其变为水平条形图
        .set_global_opts(
            title_opts=opts.TitleOpts(title="活跃天数统计"),
            xaxis_opts=opts.AxisOpts(name="天数", type_="value"),
            yaxis_opts=opts.AxisOpts(name="群员"),
        )
    )
    night_owls_bar = (
        Bar()
        .add_xaxis(list(chat_day_count.keys()))  # 从字典的键中获取 x 轴数据（姓名）
        .add_yaxis("熬夜冠军", list(chat_day_count.values()))  # 从字典的值中获取 y 轴数据（得分）
        .reversal_axis()  # 转换坐标轴，使其变为水平条形图
        .set_global_opts(
            title_opts=opts.TitleOpts(title="熬夜冠军统计"),
            xaxis_opts=opts.AxisOpts(name="次数", type_="value"),
            yaxis_opts=opts.AxisOpts(name="群员"),
        )
    )
    # 将图表的配置项（options）导出为带引号的JSON字符串
    return {
        # 收发消息占比 饼图
        'chart_data_sender': p2.dump_options_with_quotes(),
        # 消息类型占比 饼图
        'chart_data_types': p1.dump_options_with_quotes(),
        # 消息在一周的占比 饼图
        'chart_data_weekday': p3.dump_options_with_quotes(),
        # 活跃度排行
        'chart_data_chat': chat_bar.dump_options_with_quotes(),
        # 活跃天数排行
        'chart_data_chat_day': chat_day_bar.dump_options_with_quotes(),
        # 熬夜冠军排行
        'chart_data_night_owls': night_owls_bar.dump_options_with_quotes(),
    }


def get_unique_id(contact) -> str:
    if contact.remark:
        return contact.remark
    if contact.nickName:
        return contact.nickName
    # TODO 昵称相同的情况
    # if contact.remark == contact.wxid:
    return contact.wxid

def find_night_owls(chat_logs):
    night_owls = {}

    # 过滤出凌晨0点到5点之间的记录
    for log in chat_logs:
        timestamp = datetime.strptime(log["timestamp"], "%Y-%m-%d %H:%M:%S")
        hour = timestamp.hour

        # 检查时间是否在0点到5点之间
        if 0 <= hour < 6:
            date_str = timestamp.date()  # 获取日期部分
            if date_str not in night_owls:
                night_owls[date_str] = log
            else:
                # 比较当前记录的时间是否比已有记录的时间晚
                existing_timestamp = datetime.strptime(night_owls[date_str]["timestamp"], "%Y-%m-%d %H:%M:%S")
                if timestamp > existing_timestamp:
                    night_owls[date_str] = log

    return night_owls


def contacts_analysis(contacts):
    man_contact_num = 0
    woman_contact_num = 0
    province_dict = {
        '北京': '北京市',
        '上海': '上海市',
        '天津': '天津市',
        '重庆': '重庆市',
        '新疆': '新疆维吾尔族自治区',
        '广西': '广西壮族自治区',
        '内蒙古': '内蒙古自治区',
        '宁夏': '宁夏回族自治区',
        '西藏': '西藏自治区'
    }
    provinces = []
    for contact, num, text_length in contacts:
        if contact.detail.get('gender') == 1:
            man_contact_num += 1
        elif contact.detail.get('gender') == 2:
            woman_contact_num += 1
        province_py = contact.detail.get('region')
        if province_py:
            province = province_py[1]
            province = conversion_province_to_chinese(province)
            if province:
                if province in province_dict:
                    province = province_dict[province]
                else:
                    province += '省'
                provinces.append(province)
                print(province, contact.detail)
    data = Counter(provinces)
    data = [[k, v] for k, v in data.items()]
    print(data)
    max_ = max(list(map(lambda x: x[1], data)))
    c = (
        Map()
        .add("分布", data, "china")
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="地区分布"),
            visualmap_opts=opts.VisualMapOpts(max_=max_, is_piecewise=True),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return {
        'woman_contact_num': woman_contact_num,
        'man_contact_num': man_contact_num,
        'contact_region_map': c.dump_options_with_quotes(),
    }


def my_message_counter(time_range, my_name=''):
    msg_data = msg_db.get_messages_all(time_range=time_range)
    types_count = {}
    send_num = 0  # 发送消息的数量
    weekday_count = {}
    str_content = ''
    total_text_num = 0
    for message in msg_data:
        type_ = message[2]
        is_sender = message[4]
        subType = message[3]
        timestamp = message[5]
        weekday = get_weekday(timestamp)
        str_time = message[8]
        send_num += is_sender
        type_ = f'{type_}{subType:0>2d}' if subType != 0 else type_
        type_ = int(type_)
        if type_ in types_count:
            types_count[type_] += 1
        else:
            types_count[type_] = 1
        if weekday in weekday_count:
            weekday_count[weekday] += 1
        else:
            weekday_count[weekday] = 1
        if type_ == 1:
            total_text_num += len(message[7])
            if is_sender == 1:
                str_content += message[7]
    receive_num = len(msg_data) - send_num
    data = [[types_.get(key), value] for key, value in types_count.items() if key in types_]
    if not data:
        return {
            'chart_data_sender': None,
            'chart_data_types': None,
        }
    p1 = (
        Pie()
        .add(
            "",
            data,
            center=["40%", "50%"],
        )
        .set_global_opts(
            datazoom_opts=opts.DataZoomOpts(),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="70%", pos_top="10%", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        # .render("./data/聊天统计/types_pie.html")
    )
    p2 = (
        Pie()
        .add(
            "",
            [['发送', send_num], ['接收', receive_num]],
            center=["40%", "50%"],
        )
        .set_global_opts(
            datazoom_opts=opts.DataZoomOpts(),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="70%", pos_top="20%", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}\n{d}%", position='inside'))
        # .render("./data/聊天统计/pie_scroll_legend.html")
    )
    w = get_wordcloud(str_content)
    return {
        'chart_data_sender': p2.dump_options_with_quotes(),
        'chart_data_types': p1.dump_options_with_quotes(),
        'chart_data_wordcloud': w.get('chart_data_wordcloud'),
        'keyword': w.get('keyword'),
        'keyword_max_num': w.get('keyword_max_num'),
        'total_text_num': total_text_num,
    }


if __name__ == '__main__':
    from app.web_ui.web import get_contact

    # wxid = 'wxid_64lta87ier9q22'
    # 39333455129  8203426743 22050612613
    wxid = '22050612613@chatroom'

    msg_db.init_database(path='../DataBase/Msg/MSG.db')

    # w = wordcloud(wxid)
    # w_data = wordcloud(wxid, True, '2023')
    # print(w_data)

    # w_data['chart_data'].render("./data/聊天统计/wordcloud.html")
    # data = month_count(wxid, time_range=None)
    # data['chart'].render("./data/聊天统计/month_count.html")
    # data = calendar_chart(wxid, time_range=None)
    # data['chart'].render("./data/聊天统计/calendar_chart.html")
    contact = get_contact(wxid)

    data = sender(wxid, time_range=None, my_name=Me().name, ta_name=contact.remark)
    # print(data)
