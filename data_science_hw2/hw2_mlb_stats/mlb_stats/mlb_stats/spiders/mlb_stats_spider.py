import scrapy
import re

class MlbSpider(scrapy.Spider):
    name = 'mlb_spider'
    allowed_domains = ['mlb.com']
    start_urls = ['https://www.mlb.com/stats/']

    def parse(self, response):
        # Extract table headers
        headers = response.xpath('//table//th[not(@scope="colgroup")]/button/div/abbr/text()').getall()
        headers = [header.strip() for header in headers]

        # Remove 'POSITION' from headers if present
        if 'POSITION' in headers:
            headers.remove('POSITION')

        # Initialize the data list on the first page
        if response.url == self.start_urls[0]:
            self.data = []
            self.headers = headers

        # Extract player rows
        rows = response.xpath('//table//tbody/tr')
        for row in rows:
            # Extract both 'th' and 'td' elements
            player_data = row.xpath('.//th|.//td')
            data_dict = {}
            for i, cell in enumerate(player_data):
                # Handle the player name (first cell)
                if i == 0:
                    player_name = cell.xpath('.//a/@aria-label').get()
                    if player_name:
                        # Remove any defensive position in parentheses
                        player_name = re.sub(r'\s*\(.*?\)', '', player_name).strip()
                        data_dict[self.headers[i]] = player_name
                    else:
                        data_dict[self.headers[i]] = ''
                else:
                    # Extract text from other cells
                    text = cell.xpath('.//text()').get()
                    if text:
                        data_dict[self.headers[i]] = text.strip()
                    else:
                        data_dict[self.headers[i]] = ''
            self.data.append(data_dict)

        # Handle pagination (pages 2 to 6)
        current_page = response.url.split('=')[-1] if '=' in response.url else '1'
        if int(current_page) < 6:
            next_page = int(current_page) + 1
            next_page_url = f'https://www.mlb.com/stats?page={next_page}'
            yield scrapy.Request(url=next_page_url, callback=self.parse)
        else:
            # After scraping all pages, write data to CSV
            self.save_to_csv()

    def save_to_csv(self):
        import csv
        with open('mlb_player_stats.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.headers)
            writer.writeheader()
            for row in self.data:
                writer.writerow(row)
