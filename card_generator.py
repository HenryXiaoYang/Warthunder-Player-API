from io import BytesIO

import aiohttp
import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import os

matplotlib.use('Agg')  # 必须在导入 pyplot 之前设置


async def card_generator(data) -> BytesIO:
    # 字体设置
    custom_font_path = "./微软雅黑.ttf"

    fm.fontManager.addfont(custom_font_path)
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 使用微软雅黑字体

    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    plt.rcParams['font.size'] = 10
    plt.rcParams['figure.titlesize'] = 10
    plt.rcParams['axes.titlesize'] = 20
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 9

    # 设置更现代的配色方案
    COLORS = {
        'background': '#F5F5F5',  # 浅灰色背景
        'title': '#2C3E50',  # 深蓝灰色标题
        'text': '#34495E',  # 正文文字颜色
        'accent': '#3498DB'  # 强调色
    }

    # 更新图片背景色
    width = 1200
    height = 1500
    img = Image.new('RGB', (width, height), color=COLORS['background'])
    draw = ImageDraw.Draw(img)

    try:
        # 使用自定义字体文件
        title_font = ImageFont.truetype(custom_font_path, 28)
        normal_font = ImageFont.truetype(custom_font_path, 20)
    except:
        title_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()

    # 添加标题装饰
    y = 30
    draw.rectangle((20, y - 5, 150, y + 35), fill=COLORS['accent'])  # 标题背景
    draw.text((30, y), "基本信息", fill='white', font=normal_font)
    draw.rectangle((490, y - 5, 620, y + 35), fill=COLORS['accent'])
    draw.text((500, y), "战斗数据", fill='white', font=normal_font)

    # 在标题下方放置头像和信息
    y += 40  # 标题和内容之间留出间距

    # 下载并添加头像
    try:
        avatar_url = data.get('avatar', '')
        if avatar_url:
            # 创建缓存目录
            cache_dir = "./avatars"
            os.makedirs(cache_dir, exist_ok=True)
            
            # 使用URL的最后部分作为文件名
            filename = os.path.join(cache_dir, avatar_url.split('/')[-1])
            
            # 检查缓存
            if os.path.exists(filename):
                avatar_img = Image.open(filename)
            else:
                # 如果缓存不存在，下载并保存
                async with aiohttp.ClientSession() as session:
                    async with session.get(avatar_url) as response:
                        avatar_data = await response.read()
                        avatar_img = Image.open(BytesIO(avatar_data))
                        # 保存到缓存
                        avatar_img.save(filename)
                        
            # 调整头像大小为合适尺寸
            avatar_img = avatar_img.resize((150, 150))
            # 在左侧放置头像
            img.paste(avatar_img, (30, y))
    except:
        pass

    # 在头像右侧绘制详细信息
    draw.text((220, y), f"玩家昵称: {data.get('nickname', 'N/A')}", fill='black', font=normal_font)
    y += 30
    draw.text((220, y), f"公会: {data.get('clan_name', 'N/A')}", fill='black', font=normal_font)
    y += 30
    draw.text((220, y), f"玩家等级: {data.get('player_level', 'N/A')}", fill='black', font=normal_font)
    y += 30
    draw.text((220, y), f"注册日期: {data.get('register_date', 'N/A')}", fill='black', font=normal_font)

    # 计算总KDA数据
    total_kills = 0
    total_deaths = 0

    for mode in ['arcade', 'realistic', 'simulation']:
        stats = data.get('statistics', {}).get(mode, {})
        total_kills += stats.get('AirTargetsDestroyed', 0)
        total_kills += stats.get('GroundTargetsDestroyed', 0)
        total_kills += stats.get('NavalTargetsDestroyed', 0)
        total_deaths += stats.get('Deaths', 0)

    kd_ratio = round(total_kills / total_deaths if total_deaths > 0 else total_kills, 2)

    # 在基本信息右边添加KDA数据，与基本信息对齐
    base_y = y - 90  # 回到与基本信息相同的起始高度
    kda_font = ImageFont.truetype(custom_font_path, 32)
    draw.text((500, base_y), f"击杀: {total_kills}", fill='black', font=kda_font)
    draw.text((500, base_y + 40), f"死亡: {total_deaths}", fill='black', font=kda_font)
    draw.text((500, base_y + 80), f"KD比: {kd_ratio}", fill='black', font=kda_font)

    # 创建战斗数据图表
    fig = Figure(figsize=(8, 4))
    ax = fig.add_subplot(111)

    # 调整图表边距
    fig.subplots_adjust(bottom=0.09, top=0.85)  # 增加 bottom 值，调整 top 值

    # 设置标题位置
    ax.set_title('战斗数据统计', pad=20, y=1.05)

    modes = ['arcade', 'realistic', 'simulation']
    victories = []
    air_battles = []
    ground_battles = []
    naval_battles = []
    kills = []
    deaths = []

    for mode in modes:
        stats = data.get('statistics', {}).get(mode, {})
        victories.append(float(stats.get('VictoriesPerBattlesRatio', '0%').strip('%') or 0))

        # 获取详细战斗数据
        air_stats = stats.get('aviation', {})
        ground_stats = stats.get('ground', {})
        fleet_stats = stats.get('fleet', {})

        air_battles.append(air_stats.get('AirBattle', 0))
        ground_battles.append(ground_stats.get('GroundBattles', 0))
        naval_battles.append(fleet_stats.get('NavalBattles', 0))
        kills.append(stats.get('AirTargetsDestroyed', 0) + stats.get('GroundTargetsDestroyed', 0) + stats.get('NavalTargetsDestroyed', 0))
        deaths.append(stats.get('Deaths', 0))


    # 创建多组柱状图
    x = np.arange(len(modes))
    width_bar = 0.15

    # 更新图表样式
    plt.style.use('ggplot')  # 使用 ggplot 样式替代 seaborn

    # 自定义图表样式
    plt.rcParams.update({
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'axes.grid': True,
        'grid.color': '#E5E5E5',
        'axes.edgecolor': '#666666',
        'axes.linewidth': 1.0,
    })

    # 更新柱状图颜色
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6', '#34495e', '#95a5a6', '#1abc9c', '#f39c12', '#d35400']

    # 在创建柱状图时应用新颜色
    bars1 = ax.bar(x - width_bar * 2, victories, width_bar, label='胜率 (%)', color=colors[0])
    bars2 = ax.bar(x - width_bar, air_battles, width_bar, label='空战次数', color=colors[1])
    bars3 = ax.bar(x, ground_battles, width_bar, label='陆战次数', color=colors[2])
    bars4 = ax.bar(x + width_bar, naval_battles, width_bar, label='海战次数', color=colors[3])
    bars5 = ax.bar(x + width_bar * 2, kills, width_bar, label='击杀数', color=colors[4])
    bars6 = ax.bar(x + width_bar * 3, deaths, width_bar, label='死亡数', color=colors[5])

    # 为每个柱状图添加数值标签
    def autolabel(rects, labels):
        for rect, label in zip(rects, labels * len(modes)):
            height = rect.get_height()
            value = f'{height:.1f}%' if isinstance(height, float) else f'{height}'
            ax.annotate(f'{label}\n{value}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3点垂直偏移
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=8)

    # 为每组柱状图添加标签
    autolabel(bars1, ['胜率'])
    autolabel(bars2, ['空战'])
    autolabel(bars3, ['陆战'])
    autolabel(bars4, ['海战'])
    autolabel(bars5, ['击杀'])
    autolabel(bars6, ['死亡'])

    ax.set_ylabel('数值')
    ax.set_title('战斗数据统计')
    ax.set_xticks(x)
    ax.set_xticklabels(['娱乐街机', '历史性能', '真实模拟'])
    ax.legend()

    # 更新y轴显示范围
    ax.set_ylim(0, max(max(victories), max(air_battles), max(ground_battles), max(naval_battles), max(kills), max(deaths)) * 1.2)  # 设置上限为最大值的1.2倍

    # 将matplotlib图表转换为PIL图像
    canvas = FigureCanvas(fig)
    buf = BytesIO()
    canvas.print_png(buf)
    buf.seek(0)
    chart_img = Image.open(buf)

    # 将图表粘贴到主图片上
    img.paste(chart_img, (50, 250))

    # 创建载具数据饼图
    fig2 = Figure(figsize=(4, 4))
    ax2 = fig2.add_subplot(111)

    countries = ['USA', 'USSR', 'Germany', 'GreatBritain', 'Japan', 'China', 'Italy', 'France', 'Sweden', 'Israel']
    vehicles_data = data.get('vehicles_and_rewards', {})

    owned_vehicles = []
    country_labels = []

    for country in countries:
        vehicles = vehicles_data.get(country, {}).get('OwnedVehicles', 0)
        if vehicles > 0:
            owned_vehicles.append(vehicles)
            country_labels.append({
                                      'USA': '美国',
                                      'USSR': '苏联',
                                      'Germany': '德国',
                                      'GreatBritain': '英国',
                                      'Japan': '日本',
                                      'China': '中国',
                                      'Italy': '意大利',
                                      'France': '法国',
                                      'Sweden': '瑞典',
                                      'Israel': '以色列'
                                  }.get(country, country))

    if owned_vehicles:
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(owned_vehicles)))  # 使用柔和的颜色方案
        ax2.pie(owned_vehicles, labels=country_labels, autopct='%1.1f%%', colors=colors)
        ax2.set_title('载具分布')

        canvas2 = FigureCanvas(fig2)
        buf2 = BytesIO()
        canvas2.print_png(buf2)
        buf2.seek(0)
        pie_img = Image.open(buf2)

        # 调整饼图位置
        img.paste(pie_img, (775, 250))

    # 重新布局详细战斗数据
    categories = ['空战数据', '陆战数据', '海战数据']
    y_start = 670
    # 增加模式之间的间距，每个模式预留更多空间
    mode_y_positions = [y_start + 40, y_start + 300, y_start + 560]  # 每个模式之间间隔260像素

    for category_index, category in enumerate(categories):
        if category_index == 0:
            x = 50
        elif category_index == 1:
            x = 420
        else:
            x = 790

        # 绘制分类标题
        draw.text((x, y_start), f"{category}", fill='black', font=title_font)

        for mode_index, mode in enumerate(modes):
            stats = data.get('statistics', {}).get(mode, {})
            mode_name = {'arcade': '娱乐街机', 'realistic': '历史性能', 'simulation': '真实模拟'}[mode]

            y = mode_y_positions[mode_index]  # 使用预设的y坐标
            draw.text((x, y), f"【{mode_name}】", fill='black', font=normal_font)
            y += 30

            if category == '空战数据':
                aviation = stats.get('aviation', {})
                draw.text((x + 20, y), f"空战次数: {aviation.get('AirBattle', 0)}", fill='black', font=normal_font)
                y += 25
                draw.text((x + 20, y), f"战斗机空战: {aviation.get('AirBattlesInFighters', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"轰炸机空战: {aviation.get('AirBattlesInBombers', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"攻击机空战: {aviation.get('AirBattlesInAttackers', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"击毁空中目标: {stats.get('AirTargetsDestroyed', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"击毁地面目标: {stats.get('GroundTargetsDestroyed', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"击毁海上目标: {stats.get('NavalTargetsDestroyed', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"游戏时间: {aviation.get('TimePlayedInAirBattles', '0m')}", fill='black',
                          font=normal_font)

            elif category == '陆战数据':
                ground = stats.get('ground', {})
                draw.text((x + 20, y), f"陆战次数: {ground.get('GroundBattles', 0)}", fill='black', font=normal_font)
                y += 25
                draw.text((x + 20, y), f"坦克战斗: {ground.get('GroundBattlesInTanks', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"自行火炮战斗: {ground.get('GroundBattlesInSPGs', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"重型坦克战斗: {ground.get('GroundBattlesInHeavyTanks', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"防空车战斗: {ground.get('GroundBattlesInSPAA', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"击毁目标总数: {ground.get('TotalTargetsDestroyed', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"游戏时间: {ground.get('TimePlayedInGroundBattles', '0m')}", fill='black',
                          font=normal_font)

            else:  # 海战数据
                fleet = stats.get('fleet', {})
                draw.text((x + 20, y), f"海战次数: {fleet.get('NavalBattles', 0)}", fill='black', font=normal_font)
                y += 25
                draw.text((x + 20, y), f"军舰战斗: {fleet.get('ShipBattles', 0)}", fill='black', font=normal_font)
                y += 25
                draw.text((x + 20, y), f"鱼雷艇战斗: {fleet.get('MotorTorpedoBoatBattles', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"炮艇战斗: {fleet.get('MotorGunBoatBattles', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"驱逐舰战斗: {fleet.get('DestroyerBattles', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"击毁目标总数: {fleet.get('TotalTargetsDestroyed', 0)}", fill='black',
                          font=normal_font)
                y += 25
                draw.text((x + 20, y), f"游戏时间: {fleet.get('TimePlayedNaval', '0m')}", fill='black',
                          font=normal_font)

    # 将最终图片转换为字节流
    final_img_buf = BytesIO()
    img.save(final_img_buf, format='PNG')
    final_img_buf.seek(0)

    return final_img_buf
