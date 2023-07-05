import csv
import requests
from bs4 import BeautifulSoup


def get_sub_post(post):
    post_link = post.find('a', class_='striped-list-title')
    post_soup = None

    if post_link is not None:
        post_url = post_link['href']
        post_response = requests.get(post_url)
        post_soup = BeautifulSoup(post_response.text, 'html.parser')

    return post_soup

def scrape_forum_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup.prettify())

    posts = soup.find_all('div', class_='striped-list-item')

    data = []
    for post in posts:
        title_element = post.find('a', class_='striped-list-title')
        title = title_element.text.strip() if title_element else ''
        date_element = post.find('time')
        date = date_element['datetime'] if date_element else ''

        post_overview = post.find('div', class_='post-overview-count striped-list-count')
        if post_overview:
            votes_element = post_overview.find('span', class_='striped-list-count-item')
            comments_element = post_overview.find_all('span', class_='striped-list-count-item')[1]

            votes = votes_element.find('span', class_='striped-list-number').text.strip() if votes_element else ''
            comments = comments_element.find('span',
                                             class_='striped-list-number').text.strip() if comments_element else ''
        else:
            votes = ''
            comments = ''


        post_data = ''
        post_soup = get_sub_post(post)
        post_data_element = post_soup.find('div', class_='post-body')
        if post_data_element:
            post_data = post_data_element.text.strip()

        master_moderator_info = ''
        if comments != '':
            if int(comments) > 0:
                if post_soup:
                    comments_section = post_soup.find('div', class_='post')
                    comments_list = comments_section.find('ul', class_='comment-list')

                    comments_data = []
                    for comment in comments_list.find_all('li', class_='comment'):
                        commenter_element = comment.find('div', class_='guide__user-comment__meta').find('a')
                        commenter = ''
                        if commenter_element:
                            commenter = commenter_element.text.strip()

                        comment_text = comment.find('section', class_='comment-body').text.strip()

                        moderator_element = comment.find('span', class_='community-badge community-badge-titles')
                        if moderator_element:
                            moderator_info = moderator_element.text.strip()
                            master_moderator_info = moderator_info
                        else:
                            ''

                        comments_data.append([commenter, comment_text])

                    data.append([title, date, votes, comments,  master_moderator_info, post_data, comments_data])
            else:
                data.append([title, date, votes, comments, master_moderator_info, post_data, []])

    return data, soup

def scrape_forum_pages(base_url):
    all_data = []
    page = 1

    while True:
        page_url = f"{base_url}?page={page}"
        data, soup = scrape_forum_data(page_url)
        all_data.extend(data)

        next_link = soup.find('a', class_='pagination-next-link')
        if not next_link:
            break

        base_url = '' + next_link['href']
        page += 1

    return all_data

def save_data_to_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Date', 'Votes', 'Comments', 'Moderator Info', 'Post Content', 'Thread Posts'])
        writer.writerows(data)

base_url = ''

forum_data = scrape_forum_pages(base_url)

csv_filename = 'forum_data.csv'
save_data_to_csv(forum_data, csv_filename)