import pandas as pd
import streamlit as st
import emoji
import help
from collections import Counter
st.sidebar.image("WhatsApp-Logo-700x394.png",width=250)
st.sidebar.title("WhatsApp chat Analysis")

uploaded_file = st.sidebar.file_uploader("Export WhatsApp Chat and upload here")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data=bytes_data.decode("utf-8")
    df=help.get_dataframe(data)
    user_list=df['user'].unique().tolist()
    user_list.remove("group notification")
    user_list.sort()
    user_list.insert(0,"Overall")
    selected_user=st.sidebar.selectbox("Choose a participant",user_list)
    get_analysis=st.sidebar.button("Get Analysis")
    if get_analysis:
        col1,col2,col3,col4=st.columns([1.2,1,1,1])

        with col1:
            total_messgaes,dfn = help.total_messages(selected_user, df)
            st.header("Total Messages")
            st.header(total_messgaes)
            st.markdown("""---""")
        with col2:
            st.header("Total Words")
            count_words=help.total_words(selected_user, df)
            st.header(count_words)
            st.markdown("""---""")
        with col3:
            st.header("Total Media")
            total_media=help.total_media(selected_user, df)
            st.header(total_media)
            st.markdown("""---""")
        with col4:
            st.header("Total Links")
            links,total_links=help.total_links(selected_user, df)
            st.header(total_links)
            st.markdown("""---""")
        with st.expander("Get Links"):
            links=pd.DataFrame({"Links":links})
            st.dataframe(links,width=1000,height=500)
        with st.expander("Get Messages"):
            dfn = dfn[(dfn['message'] != '<Media omitted>\n') & (dfn['message'] != "This message was deleted\n")]
            if selected_user=="Overall":
                msg=pd.DataFrame({"User":dfn['user'],"Messages":dfn['message']}).reset_index()
                msg.drop('index',axis=1,inplace=True)
                st.dataframe(msg,width=1000,height=500)
            else:
                msg=pd.DataFrame({'Messages':dfn['message']}).reset_index()
                msg.drop('index', axis=1, inplace=True)
                st.dataframe(msg,width=1000,height=500)
        st.markdown("---")
        if selected_user == "Overall":
            st.title("Most busy users ")
            col1,col2=st.columns(2)
            with col1:
                x=help.most_busy_user(df)
                y=x.head()
                st.bar_chart(y)
            with col2:
              df2=pd.DataFrame({"Messages count":x,"Percentage":(x.values/df.shape[0])*100})
              st.dataframe(df2)
        st.markdown("---")
        st.title("Daily Timeline")
        daily_timeline=help.daily_timeline(df, selected_user)
        line_plot = help.create_line_plot_daily(daily_timeline)
        st.altair_chart(line_plot, use_container_width=True)
        st.markdown("---")
        st.title("Weekly Timeline")
        weekly_timeline=help.weekly_timeline(df,selected_user)
        st.bar_chart(weekly_timeline)
        st.markdown("---")
        st.title("Monthly Timeline")
        monthly_timeline=help.monthly_timeline(df, selected_user)
        st.bar_chart(monthly_timeline)
        st.markdown("---")
        st.title("Yearly Timeline")
        yearly_timeline=help.yearly_timeline(df, selected_user)
        st.bar_chart(yearly_timeline)
        st.markdown("---")
        st.title("Timeline Till Now")
        timeline=help.get_timeline(df,selected_user)
        line_plot = help.create_line_plot_overall(timeline)
        st.altair_chart(line_plot, use_container_width=True)
        st.markdown("---")
        st.title("Most used words")
        df_words=help.most_common_words(df,selected_user)
        df_words.columns = ['Words', 'count']
        bar_chart = help.create_bar_chart(df_words)
        st.altair_chart(bar_chart, use_container_width=True)
        st.markdown("---")
        st.title("Most used emojis")
        col1,col2,col3=st.columns([1,1.5,1])
        with col2:
            emojis = []
            for message in df['message']:
                emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
            emoji_data = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
            emoji_data.columns=['emojis','count']
            st.dataframe(emoji_data)
        st.markdown("---")
        st.title("Word Cloud")
        image = help.create_word_cloud(selected_user, df)
        st.image(image, width=700)
        st.markdown("---")



