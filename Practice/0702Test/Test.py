import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# 设置中文字体显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 文件路径设置
file_path = "test.xlsx"
sheet_name = "子游戏每日数据-inr"

# 检查文件是否存在
if not os.path.exists(file_path):
    raise FileNotFoundError(f"找不到指定的Excel文件：{os.path.abspath(file_path)}")

try:
    # 读取 Excel 数据
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=1, engine="openpyxl")
except Exception as e:
    print(f"读取工作表 {sheet_name} 时发生错误：{e}")
    exit(1)

# 清洗子游戏名称（只保留 CN: 开头）
df = df[df["子游戏名称"].astype(str).str.startswith("CN:")].copy()

# 去掉“CN:”前缀并去除前后空格
df["子游戏名称"] = df["子游戏名称"].str.replace("CN:", "", regex=False).str.strip()

# 添加虚拟日期列（每10行分配一个新日期）
num_days = (df.shape[0] // 10) + 1
dates = pd.date_range(start="2025-06-01", periods=num_days, freq='D')
df["日期"] = np.repeat(dates, 10)[:len(df)]

# 转换日期列为 datetime 类型
df["日期"] = pd.to_datetime(df["日期"])

# 清理金额字段
amount_fields = ["投注金额", "投注人数", "税费", "有效投注金额", "派彩金额", "输赢额"]
for col in amount_fields:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 创建结果输出目录
output_dir = "图表输出"
os.makedirs(output_dir, exist_ok=True)

# --- 图表 1：每个子游戏每日投注金额趋势图 ---
print("生成图表 1：每个子游戏每日投注金额趋势图...")
for game in df["子游戏名称"].unique():
    gdf = df[df["子游戏名称"] == game].sort_values("日期")
    plt.figure(figsize=(10, 4))
    sns.lineplot(data=gdf, x="日期", y="投注金额", marker="o")
    plt.title(f"{game} 每日投注金额趋势")
    plt.ylabel("投注金额")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{game}_趋势图.png"))
    plt.close()

# --- 图表 2：子游戏整月投注金额占比饼图 ---
print("生成图表 2：子游戏整月投注金额占比饼图...")
monthly = df.groupby("子游戏名称")["投注金额"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 8))
monthly.plot.pie(autopct="%.1f%%")
plt.ylabel("")
plt.title("子游戏整月投注金额占比")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "整月子游戏占比.png"))
plt.close()

# --- 图表 3：新彩种（摩托车+视频wingo）每日投注趋势分析 ---
print("生成图表 3：新彩种每日投注趋势...")
new_games = df[df["子游戏名称"].str.contains("摩托车|Moto|Racing|视频wingo|WinGo", case=False, na=False)]
new_games_grouped = new_games.groupby(["日期", "子游戏名称"])["投注金额"].sum().unstack().fillna(0)
new_games_grouped.plot(figsize=(12, 5), marker='o')
plt.title("新彩种每日投注趋势")
plt.ylabel("投注金额")
plt.xticks(rotation=45)
plt.legend(title="子游戏名称")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "新彩种趋势.png"))
plt.close()

# --- 图表 4：彩种分类合并趋势图（新彩种 vs 其他） ---
print("生成图表 4：彩种分类合并趋势图...")
df["彩种分类"] = df["子游戏名称"].apply(
    lambda x: "新彩种" if "摩托车" in x.lower() or "moto" in x.lower() or "win" in x.lower() else "其他"
)
merged = df.groupby(["日期", "彩种分类"])["投注金额"].sum().unstack()
merged.plot(figsize=(10, 4), marker="o")
plt.title("彩种类型每日投注金额趋势")
plt.ylabel("投注金额")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "彩种合并趋势.png"))
plt.close()

# ====== 设置阈值（用户可修改）======
MIN_PERCENTAGE_THRESHOLD = 1  # 单位：%

# --- 图表 5：特定游戏分类饼图（K3、5D、TRx、WinGo、摩托赛车、视频WinGO）---
print("生成图表 5：特定游戏分类饼图...")

def categorize_game(game_name):
    game_name = game_name.lower()

    # K3 系列（支持中英文时间单位）
    if "k3" in game_name and any(k in game_name for k in ["1min", "1分钟", "3min", "3分钟", "5min", "5分钟", "10min", "10分钟"]):
        return "K3"

    # 5D 系列
    elif "5d" in game_name and any(k in game_name for k in ["1min", "1分钟", "3min", "3分钟", "5min", "5分钟", "10min", "10分钟"]):
        return "5D"

    # WinGo 系列
    elif "wingo" in game_name and any(k in game_name for k in ["30s", "30sec", "1min", "1分钟", "3min", "3分钟", "5min", "5分钟"]):
        return "WinGo"

    # TRxWinGo 系列
    elif "trx" in game_name and "win" in game_name and any(k in game_name for k in ["1min", "1分钟", "3min", "3分钟", "5min", "5分钟", "10min", "10"]):
        return "TRx"

    # 摩托赛车
    elif "摩托赛车" in game_name or ("moto" in game_name and "racing" in game_name):
        return "摩托赛车"

    # 视频WinGO
    elif ("视频wingo" in game_name or "videowinggo" in game_name) and ("3分钟" in game_name or "3 mins" in game_name):
        return "视频WinGO"

    else:
        return None  # 不属于任何大类的直接排除

# 应用分类
df["游戏分类"] = df["子游戏名称"].apply(categorize_game)

# 过滤掉不属于指定类别的行
df_filtered = df[df["游戏分类"].notna()]

# 分组统计
category_summary = df_filtered.groupby("游戏分类")["投注金额"].sum().sort_values(ascending=False)

# 只保留指定的六大类，只取实际存在的类别
valid_categories = ["K3", "5D", "TRx", "WinGo", "摩托赛车", "视频WinGO"]
existing_categories = [cat for cat in valid_categories if cat in category_summary.index]
missing_categories = [cat for cat in valid_categories if cat not in category_summary.index]

# 提取存在的类别
if existing_categories:
    category_summary = category_summary.loc[existing_categories]
else:
    category_summary = pd.Series(dtype='float64')

# 如果还有缺失的类别，添加为 0
for cat in missing_categories:
    category_summary[cat] = 0

# 排序：按投注金额降序排列（自动排序）
final_summary = category_summary.sort_values(ascending=False)

# 准备绘图参数
labels = final_summary.index.tolist()
sizes = final_summary.values.tolist()
explode = [0.1 if cat in ["摩托赛车", "视频WinGO", "TRx"] else 0 for cat in labels]
colors = sns.color_palette("pastel")[0:len(labels)]

# 计算真实百分比
total = sum(sizes)
percentages = [(size / total * 100) if total != 0 else 0 for size in sizes]
formatted_labels = []

for pct in percentages:
    if pct >= 1:
        if abs(pct - int(pct)) < 0.01:
            formatted_labels.append(f'{int(round(pct, 0))}%')
        else:
            formatted_labels.append(f'{pct:.2f}%')
    else:
        formatted_labels.append(f'{pct:.4f}%')

# 绘图
fig, ax = plt.subplots(figsize=(14, 9))

patches, texts, autotexts = ax.pie(
    sizes,
    explode=explode,
    labels=None,
    colors=colors,
    autopct=lambda i: '',  # 自定义显示，这里留空
    startangle=90,
    textprops=dict(color="black", fontsize=10),
    pctdistance=0.75,
    wedgeprops=dict(width=0.4)  # 控制饼图厚度
)

# 手动设置每个 autopct 的文字内容
for i, autotext in enumerate(autotexts):
    autotext.set_text(formatted_labels[i])
    autotext.set_color('black')
    autotext.set_fontsize(10)

# 添加图例（放在饼图右侧）
ax.legend(patches, labels,
          title="游戏分类",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1),
          prop={'size': 10})

# 添加标题
ax.set_title("特定游戏分类投注金额占比（大类）", fontsize=16, pad=20)

# 自动调整标签避免重叠
plt.setp(texts, visible=False)
plt.tight_layout()

# 保存图像
plt.savefig(os.path.join(output_dir, "特定游戏分类投注金额占比_大类.png"), bbox_inches='tight', dpi=200)
plt.close()

# --- 表格 5：汇总表格导出，计算盈利率 ---
print("生成汇总表格...")
summary = df.groupby("子游戏名称").agg({
    "投注金额": "sum",
    "投注人数": "sum",
    "税费": "sum",
    "有效投注金额": "sum",
    "派彩金额": "sum",
    "输赢额": "sum"
}).sort_values(by="投注金额", ascending=False)

# 盈利率 = 输赢额 / 有效投注金额，避免除以零
summary["盈利率"] = summary.apply(
    lambda row: round(row["输赢额"] / row["有效投注金额"], 4) if row["有效投注金额"] != 0 else 0,
    axis=1
)

# 导出到 Excel
summary.to_excel(os.path.join(output_dir, "子游戏分析汇总.xlsx"))

# 输出完成提示
print(f"✅ 分析完成！所有图表和汇总表已保存在 '{output_dir}' 文件夹。")