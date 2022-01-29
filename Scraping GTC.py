import requests
from bs4 import BeautifulSoup
import os
from glob import glob



#Scrap All Elements of Website

def scrape_go_to_class(webpage, page_number=1):
    next_page = webpage + str(page_number)
    response= requests.get(str(next_page))
    soup = BeautifulSoup(response.content,"html.parser")
    courses = soup.findAll('div',class_='rt-inline-block')

    for course in courses:
        soup_link = course.find('a')["href"]
        soup_img = course.find("img")['src']
        retrieve_link = requests.get(soup_link)
        retrieve_soup = BeautifulSoup(retrieve_link.content,"html.parser")
        page_contents = retrieve_soup.select('div#wrapper')

        for page_content in page_contents:
            main_title = page_content.find('h1',class_='course_title')
            title= page_content.find("h3",class_='m-0')
            
            if page_content.find('video'):
                video = page_content.find('video').find('source')["src"]
            
            subtitle = page_content.find("div",class_='rtheight')
            description = page_content.find(id='details_editor')
            teacher_name = page_content.find(id = 'course_teacher').find("div",class_="col-xs-12").find('h2')
            teacher_img =  page_content.find(id = 'course_teacher').find("img")["src"]
            teacher_descrpition = page_content.find(id = 'course_teacher').find('p')
            comments = page_content.findAll('ol',class_='commentlist')
            for get_li in comments:
                get_li.find('li').find('p')

#Making Folder and Files

            def create_folder_files():
                try:
                    os.makedirs(main_title.text.strip())
                except:
                    pass
            
            
            
            with open('توضیحات.txt','w') as course_description:
                course_description.writelines([soup_link + '\n'*2 ,main_title.text.strip()+ '\n'*2,title.text.strip()+ '\n'*2,subtitle.text.strip()+ '\n'*2])
                
            
            with open('جدول زمان بندی.html','w',encoding='utf8') as time_table:
                time_table.write(str(description))
            
            with open('مشخصات استاد.txt','w') as teacher_info:
                teacher_info.writelines([teacher_name.text.strip() + '\n'*2,teacher_descrpition.text.strip() +  '\n'*2])
            
            if page_content.findAll('ol'):
                with open('نظرات.txt','w') as post_comments:
                    post_comments.write(get_li.text.strip() +  '\n'*2)
            else:
                with open('نظرات.txt','w') as post_comments:
                    post_comments.write('نظری برای این دوره وجود ندارد!!!')
            
                
            img_data = requests.get(soup_img).content
            with open('عکس اصلی.jpg', 'wb') as pic:
                pic.write(img_data)

                
            img_teacher_data = requests.get(teacher_img).content
            with open('عکس استاد.jpg', 'wb') as teacher_pic:
                teacher_pic.write(img_teacher_data)
                
            if page_content.findAll('video'):    
                video_data = requests.get(video).content
                with open('ویدیو استاد.m4v', 'wb') as teacher_video:
                    teacher_video.write(video_data)
            else:
                pass
            
                
            


#Moving Files To Created Folder:


            files_list = glob('*.*')
            
            def move_files():
                for each_file in files_list:
                    extention = each_file.split('.')[1]
                    if extention == 'py':
                        continue
                    else:
                        os.rename(each_file,main_title.text.strip() + '/' + each_file)
                    
            create_folder_files()
            move_files()   



            
#Generating the next page url
    if page_number < 5:
        page_number = page_number + 1
        scrape_go_to_class(webpage,page_number)



scrape_go_to_class('https://gotoclass.ir/courses/page/')

