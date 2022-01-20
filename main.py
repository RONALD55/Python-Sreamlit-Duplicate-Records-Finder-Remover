# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 10:46:43 2022

@author: Ronald Nyasha Kanyepi
@email : kanyepironald@gmail.com
"""
import io
import os
import base64
import csv
from datetime import datetime
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid as ag


def config():
    file_path = "./components/img/"
    img = Image.open(os.path.join(file_path, 'logo.ico'))
    st.set_page_config(page_title='DUPLICATE REMOVER', page_icon=img, layout="wide", initial_sidebar_state="expanded")

    # code to check turn of setting and footer
    st.markdown(""" <style>
    MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)

    # encoding format
    encoding = "utf-8"

    st.markdown(
        """
        <style>
            .stProgress > div > div > div > div {
                background-color: #1c4b27;
            }
        </style>""",
        unsafe_allow_html=True,
    )

    st.balloons()
    # I want it to show balloon when it finished loading all the configs


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)


def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)


def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')  # <--- here
    writer.save()
    processed_data = output.getvalue()


def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def get_table_download_link(df, file_type, btn_name):
    filename = btn_name + "_" + str(datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p"))
    if file_type == 'csv':
        file_name = filename + ".csv"
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}"><button class="btn btn-success"><i ' \
               f'class="fa fa-download"></i> {btn_name}</button></a> '

    elif file_type == 'excel':
        file_name = filename + ".xlsx"
        val = to_excel(df)
        b64 = base64.b64encode(val)
        href = f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{file_name}"><button class="btn btn-success"><i class="fa fa-download"></i> {btn_name}</button></a>'
    return href


def dataframe_finder(file):
    if file is not None:
        try:
            if file.name[-3:] == 'csv' or file.name[-3:] == 'txt':
                try:

                    # df_data = pd.read_csv(file,dtype=str,quotechar ="'",skipinitialspace=True,quoting=csv.QUOTE_MINIMAL)
                    # df_data.replace("'",'',inplace=True)
                    file.seek(0)
                    df_data = pd.concat((chunk for chunk in
                                         pd.read_csv(io.StringIO(file.read().decode('utf-8')), dtype=str, quotechar='"',
                                                     skipinitialspace=True, quoting=csv.QUOTE_MINIMAL,
                                                     chunksize=10000)))
                    df_data.replace('"', '', inplace=True)


                except:
                    file.seek(0)
                    df_data = pd.concat((chunk for chunk in
                                         pd.read_csv(io.StringIO(file.read().decode('utf-8')), sep='[;,|]',
                                                     engine='python', dtype=str)))
                    df_data.replace('"', '', inplace=True)

            else:
                df_data = pd.read_excel(file)

            return df_data

        except Exception as e:
            st.error(e)


@st.cache(allow_output_mutation=True)
def choice_download_dup(choice):
    if choice == "KEEP FIRST RECORD OF THE DUPLICATE":
        download = 'first'
    elif choice == "KEEP LAST RECORD OF THE DUPLICATE":
        download = "last"
    else:
        download = False

    return download


def duplicate_finder():
    st.title('DUPLICATES REMOVER')
    st.header('Identify and Remove Duplicate Records')
    st.markdown("""> At this section you can identify and remove dupicates based on single or multiple columns""")
    uploaded_file_3 = st.file_uploader("Upload your input here", type=["csv", "xlsx", "txt"])

    df = dataframe_finder(uploaded_file_3)
    duplicate = pd.DataFrame()
    if uploaded_file_3 is not None:

        try:
            columns = df.columns.tolist()
            columns_selected = st.multiselect(
                'Select columns : Note if you leave blank, it will search for duplicates based on all columns', columns)
            if columns_selected:
                st.write(columns_selected)

                # check if columns are selected
                if columns_selected:
                    # duplicate = duplicate.append(df[df.duplicated(columns_selected)])
                    # in case we want to remove the original record from the files use that code as well
                    duplicate = df.loc[df.duplicated(subset=columns_selected, keep=False)]
                else:
                    duplicate = duplicate.append(df[df.duplicated()])

                if duplicate.empty:
                    st.warning('There are no duplicates found based on the matched criteria above')


                else:
                    st.success("Duplicate files found")
                    st.subheader("Duplicate files found")
                    ag(duplicate)

                    st.subheader("Handling File without Duplicates")
                    st.markdown(
                        """> How do you want to handle the file without duplicates, Do you want to keep the first or 
                        last record of the duplicates in the new file or you want to remove all records that were not 
                        unique when you ran the report""")

                    dup_menu = ["KEEP FIRST RECORD OF THE DUPLICATE", "KEEP LAST RECORD OF THE DUPLICATE",
                                "REMOVE ALL NON UNIQUE RECORDS "]

                    choice_dup_menu = st.selectbox("Menu", dup_menu)

                    if choice_dup_menu and (uploaded_file_3 is not None):
                        # dropping all duplicate values and keeping the first one only , it can be keep='last' or
                        # keep=False
                        try:
                            df.drop_duplicates(subset=columns_selected, keep=choice_download_dup(choice_dup_menu),
                                               inplace=True)
                            ag(df)
                            st.subheader('Savings the report')
                            col6, col7, col8, col9 = st.columns((1, 1, 1, 1))
                            remote_css('https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css')
                            remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

                            with col6:
                                st.markdown(get_table_download_link(duplicate, 'csv', "Duplicates as CSV"),
                                            unsafe_allow_html=True)

                            with col7:
                                st.markdown(get_table_download_link(duplicate, 'excel', "Duplicates as Excel"),
                                            unsafe_allow_html=True)

                            with col8:
                                st.markdown(get_table_download_link(df, 'csv', "Unique Records as CSV"),
                                            unsafe_allow_html=True)

                            with col9:
                                st.markdown(get_table_download_link(df, 'excel', "Unique Records as Excel"),
                                            unsafe_allow_html=True)
                        except Exception as e:
                            st.error(e)

        except Exception:
            st.error('Failed to get the headers , the files is not formatted correctly')
def other_tab():
    st.header("Other TAB")

def main():
    config()
    choice = option_menu(None, ["Home", "Other Tab", "Other Tab 2", 'Other Tab 3'],
                            icons=['house', 'cloud-upload', "list-task", 'gear'],
                            menu_icon="cast", default_index=0, orientation="horizontal")
    duplicate_finder() if (choice == "Home") else other_tab()


if __name__ == '__main__':
    main()
