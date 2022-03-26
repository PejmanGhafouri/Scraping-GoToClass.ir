import requests
from bs4 import BeautifulSoup
import os
import json


class Scrap:
    def scrape_go_to_class(self):
        gotoclass_starter_point_link = 'https://gotoclass.ir/courses/page/'

        for page_number in range(1, 5):
            page_content = self._get_page_content(gotoclass_starter_point_link, page_number)

            course_items = page_content.findAll('div', class_='rt-inline-block')
            for course_item in course_items:
                course_content = self._get_course_content(course_item)
                print('Scraping {}'.format(course_content['title']))
                self._create_course_folder(course_content)

    @staticmethod
    def _get_page_content(page_link, page_number):
        paginated_link = page_link + str(page_number)
        page_html = requests.get(str(paginated_link))
        page_content = BeautifulSoup(page_html.content, 'html.parser')

        return page_content

    @staticmethod
    def _get_course_content(course_item):
        course_landing_link = course_item.find('a')['href']
        course_landing_html = requests.get(course_landing_link)
        course_landing = BeautifulSoup(course_landing_html.content, 'html.parser')

        video_content = course_landing.find('video')
        if video_content:
            video = video_content.find('source')['src']
        else:
            video = None

        comment_content = course_landing.find('ol', class_='commentlist')
        if comment_content:
            comments_li = comment_content.findAll('li', class_='parent')

            comment_contents = []
            for comment_li in comments_li:
                reply_contents = []
                reply_ol = comment_li.find('ol', class_='children')
                if reply_ol:
                    for reply_comment in reply_ol.findAll('li'):
                        reply_contents.append(
                            {
                                'author': reply_comment.find('b', class_='fn').text.strip(),
                                'comment': reply_comment.find('div', class_='comment-content').text.strip(),
                            }
                        )

                comment_contents.append(
                    {
                        'author': comment_li.find('div', class_='comment-author').find('b', class_='fn').text.strip(),
                        'comment': comment_li.find('div', class_='comment-content').find('p').text.strip(),
                        'replies': reply_contents,
                    }
                )
            comments = comment_contents
        else:
            comments = 'نظری برای این پست وجود ندارد'

        course_content = {
            'link': course_landing_link,
            'img': course_item.find('img')['src'],
            'title': course_landing.find('h1', class_='course_title').text.strip(),
            'intro_description': course_landing.find('h3', class_='m-0').text.strip(),
            'description': course_landing.find('div', class_='rtheight').text.strip(),
            'time_table': course_landing.find(id='details_editor'),
            'video': video,
            'teacher_name': course_landing.find(id='course_teacher')
            .find('div', class_='col-xs-12')
            .find('h2')
            .text.strip(),
            'teacher_img': course_landing.find(id='course_teacher').find('img')['src'],
            'teacher_description': course_landing.find(id='course_teacher').find('p').text.strip(),
            'comments': comments,
        }

        return course_content

    @staticmethod
    def _create_course_folder(course_content):

        course_title = course_content['title']
        if not os.path.isdir(course_title):
            os.makedirs(course_title)

        current_path = course_title + '/'

        with open(os.path.join(current_path, 'course_description.txt'), 'w') as course_description:
            course_description.writelines(
                [
                    course_content['link'] + '\n' * 2,
                    course_title + '\n' * 2,
                    course_content['intro_description'] + '\n' * 2,
                    course_content['description'] + '\n' * 2,
                ]
            )

        with open(os.path.join(current_path, 'time_table.html'), 'w', encoding='utf8') as time_table:
            time_table.write(str(course_content['time_table']))

        with open(os.path.join(current_path, 'teacher_info.txt'), 'w') as teacher_info:
            teacher_info.writelines(
                [
                    course_content['teacher_name'] + '\n' * 2,
                    course_content['teacher_description'] + '\n' * 2,
                ]
            )

        with open(os.path.join(current_path, 'comment.json'), 'w') as json_file:
            json_file.write(json.dumps(course_content['comments']))

        img_data = requests.get(course_content['img']).content
        with open(os.path.join(current_path, 'pic.jpg'), 'wb') as pic:
            pic.write(img_data)

        img_teacher_data = requests.get(course_content['teacher_img']).content
        with open(os.path.join(current_path, 'teacher_pic.jpg'), 'wb') as teacher_pic:
            teacher_pic.write(img_teacher_data)

        video_content = course_content['video']
        if video_content:
            video_data = requests.get(video_content).content
            with open(os.path.join(current_path, 'teacher_video.m4v'), 'wb') as teacher_video:
                teacher_video.write(video_data)


if __name__ == '__main__':
    Scrap().scrape_go_to_class()
