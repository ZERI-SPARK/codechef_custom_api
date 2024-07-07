import json
import re
import requests
from bs4 import BeautifulSoup

class UsernameError(Exception):
    pass

class PlatformError(Exception):
    pass

class BrokenChangesError(Exception):
    pass

class UserData:
    def __init__(self, username=None):
        self.__username = username

    def update_username(self, username):
        self.__username = username

    def __codechef(self):
        url = f'https://www.codechef.com/users/{self.__username}'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        try:
            rating = soup.find('div', class_='rating-number').text
        except AttributeError:
            raise UsernameError('User not Found')

        stars = soup.find('span', class_='rating')
        if stars:
            stars = stars.text

        highest_rating_container = soup.find('div', class_='rating-header')
        highest_rating = highest_rating_container.find_next('small').text.split()[-1].rstrip(')')

        rating_ranks_container = soup.find('div', class_='rating-ranks')
        rating_ranks = rating_ranks_container.find_all('a')

        global_rank = rating_ranks[0].strong.text
        country_rank = rating_ranks[1].strong.text

        if global_rank != 'NA' and global_rank != 'Inactive':
            global_rank = int(global_rank)
            country_rank = int(country_rank)

        def contests_details_get():
            rating_table = soup.find('table', class_='rating-table')
            if not rating_table:
                return []
            rating_table_rows = rating_table.find_all('td')

            def get_contest_data(indexes):
                try:
                    return {
                        'name': indexes['name'],
                        'rating': int(rating_table_rows[indexes['rating']].text),
                        'global_rank': int(rating_table_rows[indexes['global_rank']].a.strong.text),
                        'country_rank': int(rating_table_rows[indexes['country_rank']].a.strong.text)
                    }
                except ValueError:
                    return {
                        'name': indexes['name'],
                        'rating': int(rating_table_rows[indexes['rating']].text),
                        'global_rank': rating_table_rows[indexes['global_rank']].a.strong.text,
                        'country_rank': rating_table_rows[indexes['country_rank']].a.strong.text
                    }

            contests = [
                {'name': 'Long Challenge', 'rating': 1, 'global_rank': 2, 'country_rank': 3},
                {'name': 'Cook-off', 'rating': 5, 'global_rank': 6, 'country_rank': 7},
                {'name': 'Lunch Time', 'rating': 9, 'global_rank': 10, 'country_rank': 11},
            ]

            return [get_contest_data(contest) for contest in contests]

        def contest_rating_details_get():
            start_ind = page.text.find('[', page.text.find('all_rating'))
            end_ind = page.text.find(']', start_ind) + 1

            next_opening_brack = page.text.find('[', start_ind + 1)
            while next_opening_brack < end_ind:
                end_ind = page.text.find(']', end_ind + 1) + 1
                next_opening_brack = page.text.find('[', next_opening_brack + 1)

            all_rating = json.loads(page.text[start_ind: end_ind])
            for rating_contest in all_rating:
                rating_contest.pop('color')

            return all_rating

        def problems_solved_get():
            problem_solved_section = soup.find('section', class_='rating-data-section problems-solved')

            if not problem_solved_section:
                return {}, {}

            no_solved = problem_solved_section.find_all('h5')
            if len(no_solved) < 2:
                return {}, {}

            categories = problem_solved_section.find_all('article')

            fully_solved = {'count': int(re.findall(r'\d+', no_solved[0].text)[0])}

            if fully_solved['count'] != 0 and len(categories) > 0:
                for category in categories[0].find_all('p'):
                    category_name = category.find('strong').text[:-1]
                    fully_solved[category_name] = []

                    for prob in category.find_all('a'):
                        fully_solved[category_name].append({'name': prob.text, 'link': 'https://www.codechef.com' + prob['href']})

            partially_solved = {'count': int(re.findall(r'\d+', no_solved[1].text)[0])}
            if partially_solved['count'] != 0 and len(categories) > 1:
                for category in categories[1].find_all('p'):
                    category_name = category.find('strong').text[:-1]
                    partially_solved[category_name] = []

                    for prob in category.find_all('a'):
                        partially_solved[category_name].append({'name': prob.text, 'link': 'https://www.codechef.com' + prob['href']})

            return fully_solved, partially_solved

        def user_details_get():
            user_details_attribute_exclusion_list = {'username', 'link', 'teams list', 'discuss profile'}

            header_containers = soup.find_all('header')
            name = header_containers[1].find('h1', class_="h2-style").text

            user_details_section = soup.find('section', class_='user-details')
            user_details_list = user_details_section.find_all('li')

            user_details_response = {'name': name, 'username': user_details_list[0].text.split('★')[-1].rstrip('\n')}
            for user_details in user_details_list:
                attribute, value = user_details.text.split(':')[:2]
                attribute = attribute.strip().lower()
                value = value.strip()

                if attribute not in user_details_attribute_exclusion_list:
                    user_details_response[attribute] = value

            return user_details_response

        full, partial = problems_solved_get()
        details = {
            'status': 'Success',
            'rating': int(rating),
            'stars': stars,
            'highest_rating': int(highest_rating),
            'global_rank': global_rank,
            'country_rank': country_rank,
            'user_details': user_details_get(),
            'contests': contests_details_get(),
            'contest_ratings': contest_rating_details_get(),
            'fully_solved': full,
            'partially_solved': partial
        }

        return details

    def get_details(self, platform):
        # if platform == 'codechef':
            return self.__codechef()
        # if platform == 'codeforces':
        #     return self.__codeforces()
        # if platform == 'spoj':
        #     try:
        #         return self.__spoj()
        #     except AttributeError:
        #         raise UsernameError('User not Found')
        # if platform == 'interviewbit':
        #     return self.__interviewbit()
        # if platform == 'atcoder':
        #     return self.__atcoder()
        # raise PlatformError('Platform not Found')
