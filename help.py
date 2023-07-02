import re
import pandas as pd
from urlextract import URLExtract
import altair as alt
from collections import Counter
from wordcloud import WordCloud


def get_dataframe(df):
    pattern1 = "\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s[A|P]M\s-\s"
    pattern2 = "\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s-\s"
    pattern3 = "\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s[a|p]m\s-\s"

    dates1 = re.findall(pattern1, df)
    dates2 = re.findall(pattern2, df)
    dates3 = re.findall(pattern3, df)

    if len(dates1) != 0:
        pattern = pattern1
        dates = dates1
    elif len(dates2) != 0:
        pattern = pattern2
        dates = dates2
    else:
        pattern = pattern3
        dates = dates3

    message = re.split(pattern, df)[1:]
    df = pd.DataFrame({"message": message, "date": dates})

    formate1 = "%m/%d/%y, %H:%M %p - "
    formate2 = "%m/%d/%y, %H:%M - "
    formate3 = "%d/%m/%y, %H:%M %p - "

    if dates == dates1:
        formate = formate1
    elif dates == dates2:
        formate = formate2
    else:
        formate = formate3

    df['date'] = pd.to_datetime(df['date'], format=formate)

    messages = []
    users = []
    for i in df['message']:
        p = ":\s"
        entry = re.split(p, i)
        if len(entry) > 1:
            users.append(entry[0])
            messages.append(entry[1])
        else:
            users.append("group notification")
            messages.append(entry[0])
    df['user'] = users
    df['message'] = messages
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['date_only']=df['date'].dt.date
    return df
def total_messages(selected_user,df):
    if selected_user!='Overall':
        df=df[df['user']==selected_user]
    return df.shape[0],df
def total_words(selected_user,df):
    if selected_user!='Overall':
        df=df[df['user']==selected_user]
    df=df[(df['message']!='<Media omitted>\n')  & (df['message']!="This message was deleted\n")]
    if selected_user=="Overall":
        df=df[df['user']!='group notification']
    count_words=0
    for message in df['message']:
        lt=message.split()
        count_words=count_words+len(lt)
    return count_words
def total_media(selected_user,df):
    if selected_user!='Overall':
        df=df[df['user']==selected_user]
    df = df[(df['message'] == '<Media omitted>\n')]
    return df.shape[0]

def total_links(selected_user,df):
    if selected_user!='Overall':
        df=df[df['user']==selected_user]
    url=URLExtract()
    link=[]
    for i in df['message']:
        link.extend(url.find_urls(i))
    return link,len(link)
def most_busy_user(df):
    df=df[~(df['user']=='group notification')]
    x=df['user'].value_counts()
    return x
def daily_timeline(df,selected_user):
    if selected_user!='Overall':
        df=df[df['user']==selected_user]
    return df.groupby("date_only").count()['message'].reset_index()
def create_line_plot_daily(data):
    chart = alt.Chart(data).mark_line().encode(
        x='date_only',
        y='message'
    )
    return chart
def weekly_timeline(df,selected_user):
    if selected_user!='Overall':
        df=df[df['user']==selected_user]
    return df.groupby("day_name").count()['message']
def monthly_timeline(df,selected_user):
    if selected_user!='Overall':
        df=df[df['user']==selected_user]
    return df.groupby("month").count()['message']
def yearly_timeline(df,selected_user):
    if selected_user!='Overall':
        df=df[df['user']==selected_user]
    return df.groupby("year").count()['message']
def get_timeline(df,selected_user):
    if selected_user!="Overall":
        df=df[df['user']==selected_user]
    df['month_num'] = df['date'].dt.month
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline
def create_line_plot_overall(data):
    chart = alt.Chart(data).mark_line().encode(
        x='time',
        y='message'
    )
    return chart
def most_common_words(df,selected_user):
    if selected_user!="Overall":
        df=df[df['user']==selected_user]
    df = df[(df['message'] != '<Media omitted>\n') & (df['message'] != "This message was deleted\n")]
    if selected_user == "Overall":
        df = df[df['user'] != 'group notification']
    f=open("stop_word_hinglish.txt",'r')
    stop_words=f.read()
    word=[]
    for message in df['message']:
        for words in message.lower().split():
            if words not in stop_words:
                word.append(words)
    df_words=pd.DataFrame(Counter(word).most_common(20))
    return df_words
def create_bar_chart(data):
    chart = alt.Chart(data).mark_bar().encode(
        y=alt.Y('Words:O', sort=None),
        x='count:Q'
    )
    return chart

def create_word_cloud(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user']==selected_user]
    wc=WordCloud(width=500,height=400,min_font_size=10,background_color="white")
    df1 = df[~(df['user'] == 'group notification')]
    df1 = df1[~(df1['message'] == '<Media omitted>\n')]
    f = open("stop_word_hinglish.txt", 'r')
    stop_words = f.read()
    def remove_stop_words(message):
        y=[]
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    df1['message']=df1['message'].apply(remove_stop_words)
    wc.generate(df1['message'].str.cat(sep=" "))
    image = wc.to_image()
    return image


