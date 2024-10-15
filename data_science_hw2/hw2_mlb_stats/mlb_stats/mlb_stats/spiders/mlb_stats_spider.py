import scrapy
from scrapy.crawler import CrawlerProcess

class MlbStatsSpider(scrapy.Spider):
    name = "mlb_stats"
    allowed_domains = ["mlb.com"]
    start_urls = ["https://www.mlb.com/stats/"]

    # Total number of pages to crawl
    total_pages = 6  # Updated to 6 pages as per your requirement

    def parse(self, response):
        # Adjust the table selector based on the actual class or id
        table = response.xpath('//table[contains(@class, "bui-table")]')

        # Extract the table headers
        headers = table.xpath('.//thead//tr//th//text()').getall()
        headers = [header.strip() for header in headers]

        # Extract all player rows
        rows = table.xpath('.//tbody//tr')

        for row in rows:
            # Extract all columns in the row
            cols = row.xpath('.//td')

            # Initialize a list to hold column data
            item = {}

            for index, col in enumerate(cols):
                # Get the header for the current column
                if index < len(headers):
                    header = headers[index]
                else:
                    header = f"extra_{index}"

                # Extract text, handling nested elements
                if index == 0:
                    # First column: Player name with position
                    player_full = col.xpath('.//text()').getall()
                    player_full = [text.strip() for text in player_full if text.strip()]
                    if player_full:
                        player_name = player_full[0]  # Assuming the first text is the name
                    else:
                        player_name = "N/A"
                    item["Player"] = player_name
                else:
                    # Other columns: Direct text
                    cell_text = col.xpath('.//text()').get()
                    if cell_text:
                        cell_text = cell_text.strip()
                    else:
                        cell_text = "N/A"
                    item[header] = cell_text

            yield item

        # Handle pagination
        current_page = response.meta.get('page', 1)
        if current_page < self.total_pages:
            next_page = current_page + 1
            next_page_url = f"https://www.mlb.com/stats/?page={next_page}"
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={'page': next_page}
            )

# Define the main function to run the spider
def main():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "mlb_player_stats.csv": {
                "format": "csv",
                "overwrite": True
            },
        },
        "LOG_LEVEL": "INFO",  # To minimize the logs, set to "DEBUG" for more details
    })

    process.crawl(MlbStatsSpider)
    process.start()

if __name__ == "__main__":
    main()
